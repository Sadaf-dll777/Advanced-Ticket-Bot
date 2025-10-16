import discord
from discord.ext import commands
import asyncio
import sys
import os
import traceback
from datetime import datetime
from config import COLORS, EMOJIS, OWNER_ID

def is_bot_owner():
    """Custom check for bot owner from config"""
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = OWNER_ID  # Store owner ID from config
    
    async def cog_check(self, ctx):
        """Global check for all commands in this cog"""
        if ctx.author.id != self.owner_id:
            await ctx.send(f"{EMOJIS['error']} This command is owner only! (ID: {self.owner_id})")
            return False
        return True
    
    @commands.command(name="sync", description="Sync slash commands")
    async def sync(self, ctx):
        try:
            msg = await ctx.send(f"{EMOJIS['time']} Syncing slash commands...")
            synced = await self.bot.tree.sync()
            
            embed = discord.Embed(
                title=f"{EMOJIS['success']} Commands Synced",
                description=f"Successfully synced **{len(synced)}** slash commands!",
                color=COLORS['dark'],
                timestamp=datetime.utcnow()
            )
            
            await msg.edit(content=None, embed=embed)
        except Exception as e:
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Sync Failed",
                description=f"``````",
                color=COLORS['red']
            )
            await ctx.send(embed=error_embed)
    
    @commands.command(name="reload", description="Reload a cog")
    async def reload(self, ctx, cog: str):
        try:
            await self.bot.reload_extension(f'cogs.{cog}')
            
            embed = discord.Embed(
                title=f"{EMOJIS['success']} Cog Reloaded",
                description=f"Successfully reloaded `cogs.{cog}`",
                color=COLORS['dark']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Reload Failed",
                description=f"``````",
                color=COLORS['red']
            )
            await ctx.send(embed=error_embed)
    
    @commands.command(name="load", description="Load a cog")
    async def load(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f'cogs.{cog}')
            
            embed = discord.Embed(
                title=f"{EMOJIS['success']} Cog Loaded",
                description=f"Successfully loaded `cogs.{cog}`",
                color=COLORS['dark']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Load Failed",
                description=f"``````",
                color=COLORS['red']
            )
            await ctx.send(embed=error_embed)
    
    @commands.command(name="unload", description="Unload a cog")
    async def unload(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f'cogs.{cog}')
            
            embed = discord.Embed(
                title=f"{EMOJIS['success']} Cog Unloaded",
                description=f"Successfully unloaded `cogs.{cog}`",
                color=COLORS['dark']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Unload Failed",
                description=f"``````",
                color=COLORS['red']
            )
            await ctx.send(embed=error_embed)
    
    @commands.command(name="reloadall", description="Reload all cogs")
    async def reloadall(self, ctx):
        msg = await ctx.send(f"{EMOJIS['time']} Reloading all cogs...")
        
        cogs_list = list(self.bot.extensions.keys())
        reloaded = []
        failed = []
        
        for cog in cogs_list:
            try:
                await self.bot.reload_extension(cog)
                reloaded.append(cog)
            except Exception as e:
                failed.append(f"{cog}: {str(e)}")
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} Cogs Reloaded",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        if reloaded:
            embed.add_field(
                name=f"{EMOJIS['check']} Successful ({len(reloaded)})",
                value="".join([f"`{cog}`" for cog in reloaded]) or "None",
                inline=False
            )
        
        if failed:
            embed.add_field(
                name=f"{EMOJIS['error']} Failed ({len(failed)})",
                value="".join([f"`{err}`" for err in failed])[:1024] or "None",
                inline=False
            )
        
        await msg.edit(content=None, embed=embed)
    
    @commands.command(name="cogs", description="List all loaded cogs")
    async def cogs(self, ctx):
        cogs_list = [cog for cog in self.bot.cogs]
        
        embed = discord.Embed(
            title=f"{EMOJIS['settings']} Loaded Cogs",
            description=f"**Total:** {len(cogs_list)}" + "".join([f"`{i+1}.` {cog}" for i, cog in enumerate(cogs_list)]),
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="eval", description="Evaluate Python code")
    async def eval_command(self, ctx, *, code: str):
        code = code.strip('` ')
        if code.startswith('py'):
            code = code[3:]
        if code.startswith('python'):
            code = code[7:]
        
        try:
            result = eval(code)
            if asyncio.iscoroutine(result):
                result = await result
            
            embed = discord.Embed(
                title=f"{EMOJIS['success']} Evaluation Successful",
                color=COLORS['dark']
            )
            
            embed.add_field(
                name="Input",
                value=f"``````",
                inline=False
            )
            
            result_str = str(result)
            if len(result_str) > 1000:
                result_str = result_str[:1000] + "..."
            
            embed.add_field(
                name="Output",
                value=f"``````",
                inline=False
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            error_traceback = traceback.format_exc()
            if len(error_traceback) > 4000:
                error_traceback = error_traceback[:4000] + "..."
            
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Evaluation Error",
                description=f"``````",
                color=COLORS['red']
            )
            await ctx.send(embed=error_embed)
    
    @commands.command(name="shutdown", description="Shutdown the bot")
    async def shutdown(self, ctx):
        embed = discord.Embed(
            title=f"{EMOJIS['close']} Shutting Down",
            description="Bot is shutting down...",
            color=COLORS['red'],
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)
        await self.bot.close()
    
    @commands.command(name="restart", description="Restart the bot")
    async def restart(self, ctx):
        embed = discord.Embed(
            title=f"{EMOJIS['sparkle']} Restarting",
            description="Bot is restarting...",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)
        os.execv(sys.executable, ['python'] + sys.argv)
    
    @commands.command(name="servers", description="List all servers")
    async def servers(self, ctx):
        guilds = sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True)[:25]
        
        embed = discord.Embed(
            title=f"{EMOJIS['trophy']} Bot Servers",
            description=f"**Total Servers:** {len(self.bot.guilds)}\n"
                       f"**Total Users:** {sum(g.member_count for g in self.bot.guilds):,}\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        for guild in guilds:
            embed.add_field(
                name=f"{guild.name}",
                value=f"**ID:** `{guild.id}\n`"
                      f"**Members:** {guild.member_count:,}\n"
                      f"**Owner:** {guild.owner}\n",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="leave", description="Leave a server")
    async def leave(self, ctx, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        
        if not guild:
            return await ctx.send(f"{EMOJIS['error']} Server not found!")
        
        guild_name = guild.name
        
        try:
            await guild.leave()
            
            embed = discord.Embed(
                title=f"{EMOJIS['success']} Left Server",
                description=f"Successfully left **{guild_name}**"
                           f"**ID:** `{guild_id}`",
                color=COLORS['dark']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Failed to Leave",
                description=f"``````",
                color=COLORS['red']
            )
            await ctx.send(embed=error_embed)
    
    @commands.command(name="blacklist", description="Blacklist a user")
    async def blacklist(self, ctx, user_id: int):
        guilds = self.bot.db._load_json(self.bot.db.guilds_file)
        
        if 'blacklist' not in guilds:
            guilds['blacklist'] = []
        
        if user_id in guilds['blacklist']:
            return await ctx.send(f"{EMOJIS['error']} User is already blacklisted!")
        
        guilds['blacklist'].append(user_id)
        self.bot.db._save_json(self.bot.db.guilds_file, guilds)
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} User Blacklisted",
            description=f"User ID `{user_id}` has been blacklisted.",
            color=COLORS['dark']
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="unblacklist", description="Remove user from blacklist")
    async def unblacklist(self, ctx, user_id: int):
        guilds = self.bot.db._load_json(self.bot.db.guilds_file)
        
        if 'blacklist' not in guilds or user_id not in guilds['blacklist']:
            return await ctx.send(f"{EMOJIS['error']} User is not blacklisted!")
        
        guilds['blacklist'].remove(user_id)
        self.bot.db._save_json(self.bot.db.guilds_file, guilds)
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} User Unblacklisted",
            description=f"User ID `{user_id}` has been removed from blacklist.",
            color=COLORS['dark']
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="dm", description="DM a user")
    async def dm(self, ctx, user_id: int, *, message: str):
        try:
            user = await self.bot.fetch_user(user_id)
            
            embed = discord.Embed(
                title=f"{EMOJIS['inbox']} Message from Bot Owner",
                description=message,
                color=COLORS['dark'],
                timestamp=datetime.utcnow()
            )
            
            await user.send(embed=embed)
            
            success_embed = discord.Embed(
                title=f"{EMOJIS['success']} Message Sent",
                description=f"Successfully sent DM to {user.mention}",
                color=COLORS['dark']
            )
            await ctx.send(embed=success_embed)
        except Exception as e:
            error_embed = discord.Embed(
                title=f"{EMOJIS['error']} Failed to Send",
                description=f"``````",
                color=COLORS['red']
            )
            await ctx.send(embed=error_embed)
    
    @commands.command(name="broadcast", description="Broadcast message to all servers")
    async def broadcast(self, ctx, *, message: str):
        msg = await ctx.send(f"{EMOJIS['time']} Broadcasting message...")
        
        success_count = 0
        failed_count = 0
        
        embed = discord.Embed(
            title=f"{EMOJIS['bell']} Announcement",
            description=message,
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Sent by {self.bot.user.name}")
        
        for guild in self.bot.guilds:
            try:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed=embed)
                        success_count += 1
                        break
            except:
                failed_count += 1
        
        result_embed = discord.Embed(
            title=f"{EMOJIS['success']} Broadcast Complete",
            description=f"**Successful:** {success_count}\n\n**Failed:** {failed_count}",
            color=COLORS['dark']
        )
        
        await msg.edit(content=None, embed=result_embed)
    
    @commands.command(name="serverlist", description="Get detailed server list")
    async def serverlist(self, ctx):
        guilds = sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True)
        
        text = "**Server List:**\n"
        for i, guild in enumerate(guilds, 1):
            text += f"`{i}.` **{guild.name}** (ID: {guild.id})\n\n"
            text += f"Members: {guild.member_count:,} | Owner: {guild.owner}\n"
        
        chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
        
        for chunk in chunks:
            await ctx.send(chunk)
    
    @commands.command(name="ownerinfo", description="Display owner information")
    async def ownerinfo(self, ctx):
        owner = await self.bot.fetch_user(self.owner_id)
        
        embed = discord.Embed(
            title=f"{EMOJIS['crown']} Bot Owner Information",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Owner",
            value=f"**Name:** {owner.name}\n"
                  f"**ID:** `{owner.id}`\n"
                  f"**Created:** <t:{int(owner.created_at.timestamp())}:R>",
            inline=False
        )
        
        embed.set_thumbnail(url=owner.display_avatar.url)
        embed.set_footer(text=f"Owner ID from config: {self.owner_id}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Developer(bot))