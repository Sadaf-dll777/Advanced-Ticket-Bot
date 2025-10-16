import discord
from discord.ext import commands
from discord import ui
from config import PREFIX, COLORS, EMOJIS
from datetime import datetime

class OnMentionView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
        self.add_item(ui.Button(label="Invite", url=invite_url, emoji="🎫", style=discord.ButtonStyle.link))
        self.add_item(ui.Button(label="Support", url="https://discord.gg/rzB3GcWmtx", emoji="💬", style=discord.ButtonStyle.link))

class OnMention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if (self.bot.user.mentioned_in(message) and
            not message.mention_everyone and
            not (message.reference and message.reference.resolved and
                 message.reference.resolved.author == self.bot.user)):
            
            try:
                prefix = PREFIX
                guilds = self.bot.db._load_json(self.bot.db.guilds_file)
                guild_id = str(message.guild.id) if message.guild else None
                if guild_id and guild_id in guilds and 'prefix' in guilds[guild_id]:
                    prefix = guilds[guild_id]['prefix']
                
                embed = discord.Embed(
                    description=f"**{EMOJIS['sparkle']} Hey! I'm {self.bot.user.name}**\n"
                               f"Your advanced ticket management bot serving **{len(self.bot.guilds):,}** servers!\n"
                               f"**Quick Start:**\n"
                               f"`{prefix}help` or `/ticketsetup` to begin!\n",
                    color=COLORS['dark']
                )
                
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                embed.set_footer(text=f"Prefix: {prefix}")
                
                view = OnMentionView(self.bot)
                await message.reply(embed=embed, view=view, mention_author=False)
                
            except Exception as e:
                print(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(OnMention(bot))