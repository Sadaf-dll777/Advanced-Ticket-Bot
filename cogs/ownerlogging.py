import discord
from discord.ext import commands
from config import OWNER_WEBHOOK_URL, COLORS, EMOJIS
from datetime import datetime
import aiohttp

class OwnerLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook = None
        if OWNER_WEBHOOK_URL:
            self.setup_webhook()
    
    def setup_webhook(self):
        async def create_session():
            session = aiohttp.ClientSession()
            self.webhook = discord.Webhook.from_url(
                OWNER_WEBHOOK_URL,
                session=session
            )
        
        self.bot.loop.create_task(create_session())
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not self.webhook:
            return
        
        total_servers = len(self.bot.guilds)
        total_users = sum(g.member_count for g in self.bot.guilds)
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} Joined New Server",
            color=COLORS['green'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name=f"{EMOJIS['ticket']} Server Info\n",
            value=f"**Name:** {guild.name}\n"
                  f"**ID:** `{guild.id}`n"
                  f"**Members:** {guild.member_count:,}\n"
                  f"**Owner:** {guild.owner.mention} (`{guild.owner.id}`)\n",
            inline=False
        )
        
        embed.add_field(
            name=f"{EMOJIS['settings']} Server Stats\n",
            value=f"**Text Channels:** {len(guild.text_channels)}\n"
                  f"**Voice Channels:** {len(guild.voice_channels)}\n"
                  f"**Roles:** {len(guild.roles)}\n"
                  f"**Created:** <t:{int(guild.created_at.timestamp())}:R>\n",
            inline=False
        )
        
        embed.add_field(
            name=f"{EMOJIS['trophy']} Bot Stats\n",
            value=f"**Total Servers:** {total_servers:,}\n"
                  f"**Total Users:** {total_users:,}\n",
            inline=False
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"Server Count: {total_servers}")
        
        try:
            await self.webhook.send(embed=embed)
        except Exception as e:
            print(f"Error sending guild join log: {e}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if not self.webhook:
            return
        
        total_servers = len(self.bot.guilds)
        total_users = sum(g.member_count for g in self.bot.guilds)
        
        embed = discord.Embed(
            title=f"{EMOJIS['close']} Left Server",
            color=COLORS['red'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name=f"{EMOJIS['ticket']} Server Info\n",
            value=f"**Name:** {guild.name}\n"
                  f"**ID:** `{guild.id}`\n"
                  f"**Members:** {guild.member_count:,}\n"
                  f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n",
            inline=False
        )
        
        embed.add_field(
            name=f"{EMOJIS['trophy']} Bot Stats\n",
            value=f"**Total Servers:** {total_servers:,}\n"
                  f"**Total Users:** {total_users:,}\n",
            inline=False
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"Server Count: {total_servers}")
        
        try:
            await self.webhook.send(embed=embed)
        except Exception as e:
            print(f"Error sending guild remove log: {e}")
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        if not self.webhook:
            return
        
        embed = discord.Embed(
            title=f"{EMOJIS['tools']} Command Executed",
            color=COLORS['blurple'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name=f"{EMOJIS['pencil']} Command Details\n",
            value=f"**Command:** `{ctx.command}`\n"
                  f"**User:** {ctx.author.mention} (`{ctx.author.id}`)\n"
                  f"**Server:** {ctx.guild.name if ctx.guild else 'DM'}\n"
                  f"**Channel:** {ctx.channel.mention if hasattr(ctx.channel, 'mention') else 'DM'}\n",
            inline=False
        )
        
        if ctx.args[2:]:
            args_list = ', '.join(str(arg) for arg in ctx.args[2:])
            embed.add_field(
                name=f"{EMOJIS['settings']} Arguments",
                value=f"``````",
                inline=False
            )
        
        embed.set_footer(text=f"User ID: {ctx.author.id}", icon_url=ctx.author.display_avatar.url)
        
        try:
            await self.webhook.send(embed=embed)
        except Exception as e:
            print(f"Error sending command log: {e}")
    
    @commands.Cog.listener()
    async def on_application_command(self, interaction: discord.Interaction):
        if not self.webhook:
            return
        
        if interaction.type != discord.InteractionType.application_command:
            return
        
        embed = discord.Embed(
            title=f"{EMOJIS['sparkle']} Slash Command Executed",
            color=COLORS['blurple'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name=f"{EMOJIS['pencil']} Command Details\n",
            value=f"**Command:** `/{interaction.command.name}`\n"
                  f"**User:** {interaction.user.mention} (`{interaction.user.id}`)\n"
                  f"**Server:** {interaction.guild.name if interaction.guild else 'DM'}\n"
                  f"**Channel:** {interaction.channel.mention if hasattr(interaction.channel, 'mention') else 'DM'}\n",
            inline=False
        )
        
        if interaction.data.get('options'):
            options_text = ""
            for option in interaction.data['options']:
                options_text += f"{EMOJIS['dot']} **{option['name']}:** `{option.get('value', 'N/A')}`"
            embed.add_field(
                name=f"{EMOJIS['settings']} Parameters",
                value=options_text,
                inline=False
            )
        
        embed.set_footer(text=f"User ID: {interaction.user.id}", icon_url=interaction.user.display_avatar.url)
        
        try:
            await self.webhook.send(embed=embed)
        except Exception as e:
            print(f"Error sending slash command log: {e}")

async def setup(bot):
    await bot.add_cog(OwnerLogging(bot))