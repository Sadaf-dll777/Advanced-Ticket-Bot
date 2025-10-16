import discord
from discord.ext import commands
import time
import psutil
import platform
from datetime import datetime
from config import COLORS, EMOJIS

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.process = psutil.Process()
    
    def get_uptime_string(self):
        """Get formatted uptime string"""
        uptime_seconds = int(time.time() - self.start_time)
        
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        return f"{days}d {hours}h {minutes}m {seconds}s"
    
    def get_progress_bar(self, percentage, length=10):
        """Generate a progress bar"""
        filled = int(length * percentage / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f"{bar} {percentage:.1f}%"
    
    # PING - Hybrid Command
    @commands.hybrid_command(name="ping", description="Check bot latency")
    async def ping(self, ctx: commands.Context):
        """Check bot latency and connection status"""
        
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
            color = COLORS['green']
            status = "<a:green_circle2:1424969774693351564> Excellent Connection"
        elif latency < 200:
            color = COLORS['dark']
            status = "<:Yellow_circle:1424969778417893467> Good Connection"
        else:
            color = COLORS['red']
            status = "<a:red_circle1:1382704506013220986> Slow Connection"
        
        embed = discord.Embed(
            title=f"{EMOJIS['sparkle']} Latency Check",
            description=f"**{status}**",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name=f"{EMOJIS['time']} WebSocket Latency",
            value=f"**{latency}ms**",
            inline=True
        )
        
        quality = "<a:green_circle2:1424969774693351564> Optimal" if latency < 100 else "<:Yellow_circle:1424969778417893467> Stable" if latency < 200 else "<a:red_circle1:1382704506013220986> Unstable"
        embed.add_field(
            name=f"{EMOJIS['success']} Quality",
            value=f"**{quality}**",
            inline=True
        )
        
        embed.add_field(
            name=f"{EMOJIS['sparkle']} Status",
            value=f"**{EMOJIS['success']} Online**",
            inline=True
        )
        
        embed.set_footer(text="Real-time latency measurement")
        
        await ctx.send(embed=embed)
    
 
    @commands.hybrid_command(name="uptime", description="View bot uptime")
    async def uptime(self, ctx: commands.Context):
        """Display bot uptime and statistics"""
        
        uptime_str = self.get_uptime_string()
        
        embed = discord.Embed(
            title=f"{EMOJIS['time']} Bot Uptime",
            description=f"**{EMOJIS['success']} Bot has been running continuously!**",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name=f"{EMOJIS['clock']} Current Uptime",
            value=f"**{uptime_str}**",
            inline=False
        )
        
        embed.add_field(
            name=f"{EMOJIS['sparkle']} Started",
            value=f"<t:{int(self.start_time)}:F><t:{int(self.start_time)}:R>",
            inline=False
        )
        
        try:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            embed.add_field(
                name=f"💾 Memory Usage",
                value=f"**{memory_mb:.2f} MB**",
                inline=True
            )
        except:
            pass
        
        total_commands = len([cmd for cmd in self.bot.walk_commands()])
        embed.add_field(
            name=f"⚙️ Commands",
            value=f"**{total_commands}**",
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    # BOTINFO - Hybrid Command
    @commands.hybrid_command(name="botinfo", description="Display comprehensive bot information")
    async def botinfo(self, ctx: commands.Context):
        """Comprehensive bot information with detailed stats"""
        
        total_members = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        
        embed = discord.Embed(
            title=f"{EMOJIS['info']} {self.bot.user.name} Information",
            description=f"**Advanced Discord Ticket Management System**\n\nPowerful bot for handling support tickets efficiently.",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name=f"{EMOJIS['ticket']} Bot Details",
            value=f"**Name:** {self.bot.user.name}\n"
                  f"**ID:** `{self.bot.user.id}`\n"
                  f"**Created:** <t:{int(self.bot.user.created_at.timestamp())}:R>\n"
                  f"**Developer:** LazyX Development\n",
            inline=False
        )
        
        embed.add_field(
            name=f"{EMOJIS['trophy']} Statistics",
            value=f"**Servers:** {len(self.bot.guilds):,}\n"
                  f"**Users:** {total_members:,}\n"
                  f"**Channels:** {total_channels:,}\n"
                  f"**Commands:** {len([cmd for cmd in self.bot.walk_commands()])}\n",
            inline=True
        )
        
        try:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            cpu_percent = self.process.cpu_percent()
            
            embed.add_field(
                name=f"{EMOJIS['settings']} Resources",
                value=f"**Memory:** {memory_mb:.2f} MB\n"
                      f"**CPU:** {cpu_percent:.1f}%\n"
                      f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                      f"**Uptime:** {self.get_uptime_string().split()[0]}\n",
                inline=True
            )
        except:
            embed.add_field(
                name=f"{EMOJIS['settings']} Resources",
                value=f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                      f"**Status:** Online\n",
                inline=True
            )
        
        embed.add_field(
            name=f"{EMOJIS['tools']} Tech Stack",
            value=f"**Library:** discord.py\n"
                  f"**Version:** {discord.__version__}\n"
                  f"**Python:** {platform.python_version()}\n"
                  f"**Platform:** {platform.system()}\n",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    # STATS - Hybrid Command
    @commands.hybrid_command(name="stats", description="View detailed bot statistics")
    async def stats(self, ctx: commands.Context):
        """Detailed bot statistics and metrics"""
        
        total_members = sum(g.member_count for g in self.bot.guilds)
        total_text = sum(len(g.text_channels) for g in self.bot.guilds)
        total_voice = sum(len(g.voice_channels) for g in self.bot.guilds)
        total_roles = sum(len(g.roles) for g in self.bot.guilds)
        total_emojis = sum(len(g.emojis) for g in self.bot.guilds)
        
        embed = discord.Embed(
            title=f"{EMOJIS['trophy']} Bot Statistics",
            description="Detailed statistics and metrics",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🏠 Servers",
            value=f"**Total:** {len(self.bot.guilds):,}\n"
                  f"**Members:** {total_members:,}\n"
                  f"**Average:** {total_members // len(self.bot.guilds) if self.bot.guilds else 0:,}/server",
            inline=True
        )
        
        embed.add_field(
            name="📝 Channels",
            value=f"**Text:** {total_text:,}\n"
                  f"**Voice:** {total_voice:,}\n"
                  f"**Total:** {total_text + total_voice:,}\n",
            inline=True
        )
        
        embed.add_field(
            name="✨ Others",
            value=f"**Roles:** {total_roles:,}\n"
                  f"**Emojis:** {total_emojis:,}\n"
                  f"**Commands:** {len([cmd for cmd in self.bot.walk_commands()])}\n",
            inline=True
        )
        
        embed.add_field(
            name=f"{EMOJIS['time']} Performance",
            value=f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                  f"**Uptime:** {self.get_uptime_string()}\n"
                  f"**Status:** {EMOJIS['success']} Stable\n",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotInfo(bot))