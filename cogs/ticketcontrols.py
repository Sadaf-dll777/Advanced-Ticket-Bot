import discord
from discord import ui
from discord.ext import commands
from utils.embeds import (
    create_closing_embed, create_claim_embed, 
    create_priority_change_embed, create_error_embed,
    create_log_embed
)
from config import COLORS, PRIORITY_EMOJIS, PRIORITY_COLORS, EMOJIS
import asyncio

def has_staff_role(bot, guild, user, ticket_data):
    """Check if user has staff role for this ticket category"""
    # Owner and Admins always have access
    if user.guild_permissions.administrator:
        return True
    
    # Get staff roles for this ticket's category
    panel_data = bot.db.get_guild_panel(guild.id)
    if not panel_data or 'categories' not in panel_data:
        return False
    
    ticket_category = ticket_data.get('category')
    for category in panel_data['categories']:
        if category['name'] == ticket_category:
            staff_role_id = category.get('staff_role_id')
            if staff_role_id:
                staff_role = guild.get_role(staff_role_id)
                if staff_role and staff_role in user.roles:
                    return True
    
    return False

class PrioritySelect(ui.Select):
    def __init__(self, bot, ticket_id):
        self.bot = bot
        self.ticket_id = ticket_id
        
        options = [
            discord.SelectOption(label="Low", value="low", emoji="🟢", description="Low priority issue"),
            discord.SelectOption(label="Medium", value="medium", emoji="🟡", description="Medium priority issue"),
            discord.SelectOption(label="High", value="high", emoji="🟠", description="High priority issue"),
            discord.SelectOption(label="Extreme", value="extreme", emoji="🔴", description="Critical/Urgent issue")
        ]
        
        super().__init__(
            placeholder="Select new priority level...",
            options=options,
            custom_id=f"priority_select_{ticket_id}"
        )
    
    async def callback(self, interaction: discord.Interaction):
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, self.ticket_id)
        if not ticket_data:
            error_embed = create_error_embed("Ticket not found!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        # Check staff permissions
        if not has_staff_role(self.bot, interaction.guild, interaction.user, ticket_data):
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Permission Denied",
                description=f"{EMOJIS['warning']} **You don't have permission to change ticket priority!**\n"
                           f"{EMOJIS['shield']} Only staff members with the assigned role can use this feature.\n\n"
                           f"{EMOJIS['info']} If you believe this is an error, please contact an administrator.\n",
                color=COLORS['red'],
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(text="LazyX Support System", icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        priority = self.values[0]
        old_priority = ticket_data.get('priority', 'medium')
        priority_emoji = PRIORITY_EMOJIS.get(priority, '🟡')
        
        self.bot.db.update_ticket(interaction.guild.id, self.ticket_id, priority=priority)
        
        channel = interaction.channel
        ticket_num = ticket_data.get('ticket_number', 0)
        new_name = f"{priority_emoji}ticket-{ticket_num:04d}"
        
        try:
            await channel.edit(name=new_name)
        except:
            pass
        
        priority_embed = create_priority_change_embed(old_priority, priority)
        await interaction.response.send_message(embed=priority_embed)

class PriorityChangeView(ui.View):
    def __init__(self, bot, ticket_id):
        super().__init__(timeout=60)
        self.add_item(PrioritySelect(bot, ticket_id))

class CloseConfirmView(ui.View):
    def __init__(self, bot, ticket_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.ticket_id = ticket_id
        self.value = None
    
    @ui.button(label="Yes, Close Ticket", style=discord.ButtonStyle.danger, emoji="<:icon_tick:1424794374767906938>")
    async def confirm_close(self, interaction: discord.Interaction, button: ui.Button):
        self.value = True
        self.stop()
        
        closing_embed = discord.Embed(
            title=f"{EMOJIS['close']} Closing Ticket",
            description=(
                f"{EMOJIS['time']} **This ticket will be closed in 5 seconds...**\n"
                f"{EMOJIS['transcript']} Generating transcript and saving logs.\n"
                f"{EMOJIS['inbox']} Sending a copy to your DMs.\n"
                f"{EMOJIS['star']} You'll receive a review request shortly.\n"
                f"**Thank you for contacting our support team!**\n"
                f"{EMOJIS['heart']} We hope your issue was resolved to your satisfaction.\n"
            ),
            color=COLORS['red'],
            timestamp=discord.utils.utcnow()
        )
        closing_embed.set_footer(text="LazyX Support System", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        await interaction.response.edit_message(embed=closing_embed, view=None)
        
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, self.ticket_id)
        if ticket_data:
            user_id = ticket_data.get('user_id')
            user = interaction.guild.get_member(user_id)
            
            transcript_cog = self.bot.get_cog('Transcript')
            if transcript_cog:
                transcript = await transcript_cog.create_transcript(interaction.channel, ticket_data)
                
                logs_channel_id = self.bot.db.get_ticket_logs_channel(interaction.guild.id)
                if logs_channel_id:
                    logs_channel = interaction.guild.get_channel(logs_channel_id)
                    if logs_channel:
                        priority = ticket_data.get('priority', 'medium')
                        priority_emoji = PRIORITY_EMOJIS.get(priority, '🟡')
                        
                        log_embed = create_log_embed(
                            f"{EMOJIS['close']} Ticket Closed",
                            {
                                f"{EMOJIS['ticket']} Ticket": f"#{ticket_data.get('ticket_number', 0):04d}",
                                f"{EMOJIS['pencil']} Subject": ticket_data.get('subject', 'N/A'),
                                f"{EMOJIS['category']} Category": ticket_data.get('category', 'N/A'),
                                f"{EMOJIS['user']} Closed by": interaction.user.mention,
                                f"{EMOJIS['priority']} Priority": f"{priority_emoji} {priority.title()}"
                            }
                        )
                        
                        await logs_channel.send(embed=log_embed, file=transcript)
            
            review_cog = self.bot.get_cog('Reviews')
            if review_cog and user:
                await review_cog.send_review_request(user, ticket_data, interaction.guild.id)
        
        await asyncio.sleep(5)
        
        try:
            await interaction.channel.delete()
            self.bot.db.delete_ticket(interaction.guild.id, self.ticket_id)
        except Exception as e:
            print(f"Error deleting ticket: {e}")
    
    @ui.button(label="No, Keep Open", style=discord.ButtonStyle.secondary, emoji="<:icons_cross:1424794344292094084>")
    async def cancel_close(self, interaction: discord.Interaction, button: ui.Button):
        self.value = False
        self.stop()
        
        cancel_embed = discord.Embed(
            title=f"{EMOJIS['info']} Ticket Close Cancelled",
            description=f"{EMOJIS['success']} This ticket will remain open.\n\nFeel free to continue the conversation!",
            color=COLORS['dark'],
            timestamp=discord.utils.utcnow()
        )
        cancel_embed.set_footer(text="LazyX Support")
        
        await interaction.response.edit_message(embed=cancel_embed, view=None)

class TicketControlView(ui.View):
    def __init__(self, bot, ticket_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_id = ticket_id
    
    @ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="<:icons_cross:1424794344292094084>", custom_id="persistent_close_ticket", row=0)
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # Check staff permissions
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, self.ticket_id)
        if not ticket_data:
            error_embed = create_error_embed("Ticket not found!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        if not has_staff_role(self.bot, interaction.guild, interaction.user, ticket_data):
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Permission Denied",
                description=f"{EMOJIS['warning']} **You don't have permission to close this ticket!**\n"
                           f"{EMOJIS['shield']} Only staff members with the assigned role can close tickets.\n"
                           f"{EMOJIS['info']} If you need assistance, please wait for a staff member to respond.\n",
                color=COLORS['red'],
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(text="LazyX Support System", icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        confirm_embed = discord.Embed(
            title=f"{EMOJIS['warning']} Are You Sure?",
            description=(
                f"**You are about to close this ticket!**\n"
                f"{EMOJIS['info']} **What happens when you close:**\n\n"
                f"{EMOJIS['dot']} The ticket channel/thread will be **permanently deleted**\n"
                f"{EMOJIS['dot']} A **transcript** will be saved to the logs channel\n"
                f"{EMOJIS['dot']} The customer will receive a **review request** in DMs\n"
                f"{EMOJIS['dot']} All ticket data will be **archived**\n"
                f"{EMOJIS['warning']} **This action cannot be undone!**\n"
                f"Are you sure you want to close this ticket?\n"
            ),
            color=COLORS['red'],
            timestamp=discord.utils.utcnow()
        )
        confirm_embed.set_footer(text="Click below to confirm or cancel", icon_url=interaction.user.display_avatar.url)
        
        confirm_view = CloseConfirmView(self.bot, self.ticket_id)
        await interaction.response.send_message(embed=confirm_embed, view=confirm_view, ephemeral=True)
    
    @ui.button(label="Claim Ticket", style=discord.ButtonStyle.green, emoji="<:bye:1424995824999596042>", custom_id="persistent_claim_ticket", row=0)
    async def claim_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # Check staff permissions
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, self.ticket_id)
        if not ticket_data:
            error_embed = create_error_embed("Ticket not found!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        if not has_staff_role(self.bot, interaction.guild, interaction.user, ticket_data):
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Permission Denied",
                description=f"{EMOJIS['warning']} **You don't have permission to claim this ticket!**\n"
                           f"{EMOJIS['shield']} Only staff members with the assigned role can claim tickets.\n"
                           f"{EMOJIS['info']} Please wait for a staff member to assist you.\n",
                color=COLORS['red'],
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(text="LazyX Support System", icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        if ticket_data.get('claimed_by'):
            claimer = interaction.guild.get_member(ticket_data['claimed_by'])
            error_embed = create_error_embed(
                f"Ticket already claimed by {claimer.mention if claimer else 'someone'}!",
                interaction.user
            )
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        self.bot.db.update_ticket(interaction.guild.id, self.ticket_id, claimed_by=interaction.user.id)
        
        claim_embed = create_claim_embed(interaction.user)
        await interaction.response.send_message(embed=claim_embed)
    
    @ui.button(label="Change Priority", style=discord.ButtonStyle.blurple, emoji="<a:lighting_icons:1424969456177778729>", custom_id="persistent_change_priority", row=1)
    async def change_priority(self, interaction: discord.Interaction, button: ui.Button):
        # Check staff permissions
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, self.ticket_id)
        if not ticket_data:
            error_embed = create_error_embed("Ticket not found!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        if not has_staff_role(self.bot, interaction.guild, interaction.user, ticket_data):
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Permission Denied",
                description=f"{EMOJIS['warning']} **You don't have permission to change ticket priority!**\n"
                           f"{EMOJIS['shield']} Only staff members with the assigned role can change priority.\n\n"
                           f"{EMOJIS['info']} Priority will be adjusted by staff as needed.",
                color=COLORS['red'],
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(text="LazyX Support System", icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        priority_view = PriorityChangeView(self.bot, self.ticket_id)
        
        priority_embed = discord.Embed(
            title=f"{EMOJIS['priority']} Change Priority",
            description="Select the new priority level from the dropdown below:",
            color=COLORS['dark']
        )
        
        await interaction.response.send_message(embed=priority_embed, view=priority_view, ephemeral=True)

class TicketControls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(TicketControls(bot))