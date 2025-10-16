import discord
from discord.ext import commands
from discord import ui
from config import PREFIX, COLORS, EMOJIS
from datetime import datetime

class HelpCategorySelect(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        
        options = [
            discord.SelectOption(
                label="Commands",
                value="commands",
                emoji="<:gear_icons:1424969532275163207>",
                description="Browse all bot commands"
            ),
            discord.SelectOption(
                label="FAQ",
                value="faq",
                emoji="<:icon_chat:1425507996473233602>",
                description="Frequently asked questions"
            ),
            discord.SelectOption(
                label="Setup",
                value="setup",
                emoji="<:icon_staff:1425508129642381443>",
                description="How to setup the bot"
            )
        ]
        
        super().__init__(
            placeholder="📋 Select what you need help with...",
            options=options,
            custom_id="help_category_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        
        # Get prefix
        prefix = PREFIX
        try:
            guilds = self.bot.db._load_json(self.bot.db.guilds_file)
            prefix = guilds.get(str(interaction.guild.id), {}).get('prefix', PREFIX)
        except:
            pass
        
        if category == "commands":
            embed = self.create_commands_embed(prefix)
        elif category == "faq":
            embed = self.create_faq_embed(prefix)
        elif category == "setup":
            embed = self.create_setup_embed(prefix)
        
        await interaction.response.edit_message(embed=embed)
    
    def create_commands_embed(self, prefix):
        """Create commands list embed"""
        embed = discord.Embed(
            title="<:gear_icons:1424969532275163207> Commands",
            description="Browse through all available commands",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        # Ticket Commands
        embed.add_field(
            name=f"{EMOJIS['ticket']} Ticket Management",
            value=f"`/ticketsetup` - Setup ticket system\n"
                  f"**Close Button** - Close ticket (Staff)\n"
                  f"**Claim Button** - Claim ticket (Staff)\n"
                  f"**Priority Button** - Change priority (Staff)\n",
            inline=False
        )
        
        # General Commands
        embed.add_field(
            name="<:icon_write:1424969520958935164> General",
            value=f"`{prefix}help` - Help menu\n"
                  f"`{prefix}ping` - Bot latency\n"
                  f"`{prefix}uptime` - Bot uptime\n"
                  f"`{prefix}invite` - Invite bot\n"
                  f"`{prefix}support` - Support server\n",
            inline=False
        )
        
        # Info Commands
        embed.add_field(
            name="<:icons_info:1424794337857896532> Information",
            value=f"`{prefix}botinfo` - Bot information\n"
                  f"`{prefix}stats` - Bot statistics\n"
                  f"`{prefix}serverinfo` - Server info\n"
                  f"`{prefix}userinfo` - User info\n",
            inline=False
        )
        
        embed.set_footer(text=f"Current Prefix: {prefix} • LazyX Development")
        return embed
    
    def create_faq_embed(self, prefix):
        """Create FAQ embed"""
        embed = discord.Embed(
            title="<:icon_chat:1425507996473233602> FAQ",
            description="Solutions for the most frequent questions",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        faqs = [
            (
                "**How do I setup the bot?**\n",
                f"Run `/ticketsetup` and follow the interactive setup wizard. It takes less than 5 minutes!\n\n"
            ),
            (
                "**How do I create a ticket?**\n",
                "Click the button on the ticket panel or use the dropdown menu to select a category.\n\n"
            ),
            (
                "**Who can close tickets?**\n",
                "Only staff members with the assigned role can close, claim, and manage tickets.\n\n"
            ),
            (
                "**How do I change the prefix?**\n",
                f"Use `/ticketsetup` and go to settings to change the bot prefix.\n\n"
            ),
            (
                "**Can I customize the bot?**\n",
                "Yes! You can customize colors, emojis, categories, and staff roles through setup.\n\n"
            ),
            (
                "**Where are transcripts saved?**\n",
                "Transcripts are automatically saved to your logs channel as HTML files when tickets close.\n\n"
            ),
            (
                "**How do I add staff members?**\n",
                "Assign the staff role you configured during setup to users who should manage tickets.\n\n"
            ),
            (
                "**Need more help?**",
                "Join our support server using `/support` command!\n\n"
            )
        ]
        
        for question, answer in faqs:
            embed.add_field(name=question, value=answer, inline=False)
        
        embed.set_footer(text="Still have questions? Join our support server!")
        return embed
    
    def create_setup_embed(self, prefix):
        """Create setup guide embed"""
        embed = discord.Embed(
            title="<:icon_staff:1425508129642381443> Setup",
            description="Follow these steps to setup LazyX Ticket Bot on your server",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="**<:icons_1:1425507544347971616> Run Setup Command**",
            value=f"Use `/ticketsetup` to start the interactive setup wizard.",
            inline=False
        )
        
        embed.add_field(
            name="**<:icons_dua:1425507616859095130> Setuping Panel**",
            value="Setup Ticket panel embed according to yourself by Given buttons like Title, Description, etc.",
            inline=False
        )
        
        embed.add_field(
            name="**<:icons_3:1425507692054708235> Creating Categories**",
            value="Create ticket categories like Support, Bug Report, Suggestions, etc.",
            inline=False
        )
        
        embed.add_field(
            name="**<:icons_4:1425507864495128608> Sending Panel**",
            value="Click on Submit Button to send the panel",
            inline=False
        )
               
        embed.add_field(
            name=f"{EMOJIS['success']} Done!",
            value="Your ticket system is now ready! Users can create tickets by clicking buttons.\n",
            inline=False
        )
        
        embed.set_footer(text="Setup takes less than 5 minutes • Need help? Use /support")
        return embed

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        self.add_item(HelpCategorySelect(bot))
        
        # Add Buttons
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
        self.add_item(ui.Button(label="Invite Bot", url=invite_url, emoji="<:icon_ticket:1424793495427616909>", style=discord.ButtonStyle.link, row=1))
        self.add_item(ui.Button(label="Support Server", url="https://discord.gg/rzB3GcWmtx", emoji="<:icon_chat:1425507996473233602> ", style=discord.ButtonStyle.link, row=1))
    
    async def on_timeout(self):
        """Disable dropdown on timeout"""
        for item in self.children:
            if isinstance(item, ui.Select):
                item.disabled = True
    
    @ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="<:icon_bin:1425000109216763944> ", row=2)
    async def delete_button(self, interaction: discord.Interaction, button: ui.Button):
        """Delete help message"""
        await interaction.message.delete()

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="help", description="Display the help menu")
    async def help(self, ctx: commands.Context):
        """Interactive help menu"""
        
        # Get prefix
        prefix = PREFIX
        try:
            guilds = self.bot.db._load_json(self.bot.db.guilds_file)
            prefix = guilds.get(str(ctx.guild.id), {}).get('prefix', PREFIX)
        except:
            pass
        
        # Create main embed
        embed = discord.Embed(
            title=f"{EMOJIS['ticket']} LazyX Ticket Help Menu",
            description=f"**LazyX Ticket is the only ticketing bot you'll ever need!**\n"
                       f"Explore its features and set the best ticket system for your server!\n\n"
                       f"<:gear_icons:1424969532275163207> **Commands** - Browse through commands list\n\n"
                       f"<:icon_chat:1425507996473233602> **FAQ** - Solutions for frequent questions\n\n"
                       f"<:icon_staff:1425508129642381443> **Setup** - Steps to setup the bot\n\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Select what you need help with • Prefix: {prefix}",
            icon_url=self.bot.user.display_avatar.url
        )        
        
        view = HelpView(self.bot)
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))