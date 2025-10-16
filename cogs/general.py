import discord
from discord.ext import commands
from discord import app_commands
import time
from datetime import datetime
from config import COLORS, EMOJIS


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # SERVER INFO
    @commands.hybrid_command(name="serverinfo", description="Get detailed server information")
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild

        embed = discord.Embed(
            title=f"{EMOJIS['info']} Server Information",
            description=f"Detailed information about **{guild.name}**",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name=f"{EMOJIS['ticket']} General",
            value=f"• **Name:** {guild.name}\n"
                  f"• **ID:** `{guild.id}`\n"
                  f"• **Owner:** {guild.owner.mention}\n"
                  f"• **Created:** <t:{int(guild.created_at.timestamp())}:R>\n",
            inline=True
        )

        embed.add_field(
            name=f"{EMOJIS['user']} Members",
            value=f"• **Total:** {guild.member_count:,}\n"
                  f"• **Humans:** {len([m for m in guild.members if not m.bot]):,}\n"
                  f"• **Bots:** {len([m for m in guild.members if m.bot]):,}\n",
            inline=True
        )

        embed.add_field(
            name=f"{EMOJIS['category']} Channels",
            value=f"• **Text:** {len(guild.text_channels)}\n"
                  f"• **Voice:** {len(guild.voice_channels)}\n"
                  f"• **Categories:** {len(guild.categories)}\n",
            inline=True
        )

        embed.add_field(
            name=f"{EMOJIS['tools']} Other",
            value=f"• **Roles:** {len(guild.roles)}\n"
                  f"• **Emojis:** {len(guild.emojis)}\n"
                  f"• **Boost Level:** {guild.premium_tier}\n",
            inline=True
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        requester = ctx.author if isinstance(ctx, commands.Context) else ctx.user
        embed.set_footer(
            text=f"Requested by {requester}",
            icon_url=requester.display_avatar.url
        )

        if isinstance(ctx, commands.Context):
            await ctx.send(embed=embed)
        else:
            await ctx.response.send_message(embed=embed, ephemeral=True)

    # INVITE
    @commands.hybrid_command(name="invite", description="Get bot invite link")
    async def invite(self, ctx: commands.Context):
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"

        embed = discord.Embed(
            title=f"{EMOJIS['ticket']} Invite LazyX Ticket Bot",
            description=f"Add **{self.bot.user.name}** to your server!\n"
                        f"Click the button below to invite me to your server.\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Thank you for using LazyX!")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Invite Bot", url=invite_url, emoji=EMOJIS['ticket']))

        if isinstance(ctx, commands.Context):
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.response.send_message(embed=embed, view=view, ephemeral=True)

    # SUPPORT
    @commands.hybrid_command(name="support", description="Get support server link")
    async def support(self, ctx: commands.Context):
        support_url = "https://discord.gg/rzB3GcWmtx"

        embed = discord.Embed(
            title=f"{EMOJIS['bell']} Support Server",
            description=f"Need help? Join our support server!\n"
                        f"Get 24/7 support from our team and community.\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="We're here to help!")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Support Server", url=support_url, emoji=EMOJIS['bell']))

        if isinstance(ctx, commands.Context):
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.response.send_message(embed=embed, view=view, ephemeral=True)

    # SETPREFIX (Admin Only)
    @commands.hybrid_command(name="setprefix", description="Change bot prefix (Admin only)")
    @app_commands.describe(prefix="New prefix for the bot")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx: commands.Context, prefix: str):
        if len(prefix) > 5:
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Error",
                description="Prefix cannot be longer than 5 characters!",
                color=COLORS['red']
            )

            if isinstance(ctx, commands.Context):
                return await ctx.send(embed=error_embed)
            else:
                return await ctx.response.send_message(embed=error_embed, ephemeral=True)

        guilds = self.bot.db._load_json(self.bot.db.guilds_file)
        guild_id = str(ctx.guild.id)

        if guild_id not in guilds:
            guilds[guild_id] = {}

        guilds[guild_id]['prefix'] = prefix
        self.bot.db._save_json(self.bot.db.guilds_file, guilds)

        embed = discord.Embed(
            title=f"{EMOJIS['success']} Prefix Updated",
            description=f"Bot prefix has been changed to: `{prefix}`\n"
                        f"**Example:** `{prefix}ping`\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )

        requester = ctx.author if isinstance(ctx, commands.Context) else ctx.user
        embed.set_footer(
            text=f"Changed by {requester}",
            icon_url=requester.display_avatar.url
        )

        if isinstance(ctx, commands.Context):
            await ctx.send(embed=embed)
        else:
            await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
