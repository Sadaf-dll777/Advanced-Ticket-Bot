import discord
from discord import ui
from discord.ext import commands
from utils.embeds import (
    create_review_request_embed, 
    create_review_submitted_embed,
    create_review_post_embed,
    create_info_embed
)
from config import COLORS, EMOJIS, RATING_EMOJIS, REVIEW_ENABLED
from datetime import datetime

class ReviewModal(ui.Modal, title="📊 Rate Your Support Experience"):
    staff_member = ui.TextInput(
        label="Which staff member helped you most?",
        placeholder="Enter their username or type 'No one specific'",
        required=True,
        max_length=100,
        style=discord.TextStyle.short
    )
    
    rating = ui.TextInput(
        label="Rating (1-5 stars)",
        placeholder="Enter a number from 1 to 5",
        required=True,
        max_length=1,
        style=discord.TextStyle.short
    )
    
    feedback = ui.TextInput(
        label="Your Feedback",
        placeholder="Tell us about your experience...",
        required=True,
        max_length=1000,
        style=discord.TextStyle.paragraph
    )
    
    suggestions = ui.TextInput(
        label="Suggestions for Improvement (Optional)",
        placeholder="How can we improve our support?",
        required=False,
        max_length=500,
        style=discord.TextStyle.paragraph
    )
    
    def __init__(self, bot, ticket_data, guild_id):
        super().__init__()
        self.bot = bot
        self.ticket_data = ticket_data
        self.guild_id = guild_id
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            rating_value = int(self.rating.value)
            if rating_value < 1 or rating_value > 5:
                raise ValueError()
        except:
            error_embed = discord.Embed(
                description=f"{EMOJIS['error']} Invalid rating! Please enter a number between 1 and 5.",
                color=COLORS['red']
            )
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        submit_embed = create_review_submitted_embed()
        await interaction.response.send_message(embed=submit_embed, ephemeral=True)
        
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return
        
        review_channel = discord.utils.get(guild.channels, name="ticket-reviews")
        if not review_channel:
            try:
                review_channel = await guild.create_text_channel(
                    name="ticket-reviews",
                    topic=f"{EMOJIS['review']} Customer feedback and support reviews"
                )
            except:
                return
        
        review_data = {
            'ticket_number': self.ticket_data.get('ticket_number', 0),
            'category': self.ticket_data.get('category', 'N/A'),
            'staff_member': self.staff_member.value,
            'rating': rating_value,
            'feedback': self.feedback.value,
            'suggestions': self.suggestions.value if self.suggestions.value else None
        }
        
        review_embed = create_review_post_embed(review_data, interaction.user)
        await review_channel.send(embed=review_embed)

class ReviewView(ui.View):
    def __init__(self, bot, ticket_data, guild_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_data = ticket_data
        self.guild_id = guild_id
    
    @ui.button(label="Leave a Review", style=discord.ButtonStyle.green, emoji="<:glowingstar:1424969557621215302>", custom_id="leave_review_btn")
    async def leave_review(self, interaction: discord.Interaction, button: ui.Button):
        modal = ReviewModal(self.bot, self.ticket_data, self.guild_id)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Skip", style=discord.ButtonStyle.grey, emoji="<:icon_right_arrow:1424997270000111696>", custom_id="skip_review_btn")
    async def skip_review(self, interaction: discord.Interaction, button: ui.Button):
        skip_embed = create_info_embed(
            "Review Skipped",
            f"Thank you for using our support system!\n"
            f"{EMOJIS['heart']} We hope your issue was resolved."
        )
        await interaction.response.send_message(embed=skip_embed, ephemeral=True)
        
        try:
            await interaction.message.delete()
        except:
            pass

class Reviews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def send_review_request(self, user: discord.User, ticket_data: dict, guild_id: int):
        if not REVIEW_ENABLED:
            return
        
        try:
            review_embed = create_review_request_embed(ticket_data)
            review_view = ReviewView(self.bot, ticket_data, guild_id)
            
            await user.send(embed=review_embed, view=review_view)
            
        except discord.Forbidden:
            print(f"Could not send review request to {user} - DMs disabled")
        except Exception as e:
            print(f"Error sending review request: {e}")

async def setup(bot):
    await bot.add_cog(Reviews(bot))