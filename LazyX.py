import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN, PREFIX, OWNER_ID
from database.db import Database

# ANSI Color codes
class Colors:
    RESET = '\u001B[0m'
    RED = '\u001B[91m'
    GREEN = '\u001B[92m'
    YELLOW = '\u001B[93m'
    BLUE = '\u001B[94m'
    MAGENTA = '\u001B[95m'
    CYAN = '\u001B[96m'
    WHITE = '\u001B[97m'
    BOLD = '\u001B[1m'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class LazyXTicketBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None
        )
        self.db = Database()
    
    async def setup_hook(self):
        cogs_to_load = [
            'cogs.help',
            'cogs.onmention',
            'cogs.botinfo',
            'cogs.general',
            'cogs.dev',
            'cogs.ticketsetup',
            'cogs.ticketcreation',
            'cogs.threadticket',
            'cogs.channelticket',
            'cogs.ticketcontrols',
            'cogs.slashcommands',
            'cogs.transcript',
            'cogs.reviews',
            'cogs.ownerlogging'
        ]
        
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}Loading Cogs...{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                print(f'{Colors.GREEN}✓{Colors.RESET} Loaded {Colors.MAGENTA}{cog}{Colors.RESET}')
            except Exception as e:
                print(f'{Colors.RED}✗{Colors.RESET} Failed to load {Colors.MAGENTA}{cog}{Colors.RESET}: {Colors.RED}{e}{Colors.RESET}')
        
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        await self.setup_persistent_views()
        
        try:
            synced = await self.tree.sync()
            print(f'{Colors.GREEN}✓{Colors.RESET} Synced {Colors.YELLOW}{len(synced)}{Colors.RESET} slash commands')
        except Exception as e:
            print(f'{Colors.RED}✗{Colors.RESET} Failed to sync commands: {Colors.RED}{e}{Colors.RESET}')
    
    async def setup_persistent_views(self):
        from utils.views import TicketDropdownView, TicketButtonView
        from cogs.ticketcontrols import TicketControlView
        
        # Setup ticket panel views
        for guild_id, guild_data in self.db._load_json(self.db.guilds_file).items():
            if 'categories' in guild_data and 'style' in guild_data:
                if guild_data['style'] == 'dropdown':
                    view = TicketDropdownView(self, guild_data['categories'])
                else:
                    view = TicketButtonView(self, guild_data['categories'])
                self.add_view(view)
        
        # Setup ticket control views for active tickets
        tickets_data = self.db._load_json(self.db.tickets_file)
        ticket_count = 0
        
        for guild_id, tickets in tickets_data.items():
            for ticket_id, ticket_info in tickets.items():
                if not ticket_info.get('closed', False):
                    control_view = TicketControlView(self, int(ticket_id))
                    self.add_view(control_view)
                    ticket_count += 1
        
        print(f'{Colors.GREEN}✓{Colors.RESET} Setup persistent views')
        print(f'{Colors.GREEN}✓{Colors.RESET} Loaded {Colors.YELLOW}{ticket_count}{Colors.RESET} ticket control views')
    
    async def on_ready(self):
        # ASCII Art
        ascii_art = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗
{Colors.MAGENTA}  ██╗      █████╗ ███████╗██╗   ██╗██╗  ██╗
{Colors.MAGENTA}  ██║     ██╔══██╗╚══███╔╝╚██╗ ██╔╝╚██╗██╔╝
{Colors.MAGENTA}  ██║     ███████║  ███╔╝  ╚████╔╝  ╚███╔╝ 
{Colors.MAGENTA}  ██║     ██╔══██║ ███╔╝    ╚██╔╝   ██╔██╗ 
{Colors.MAGENTA}  ███████╗██║  ██║███████╗   ██║   ██╔╝ ██╗
{Colors.MAGENTA}  ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝
{Colors.CYAN}╚═══════════════════════════════════════════════════════════════╝
{Colors.YELLOW}              ✦ Ticket Management System ✦
{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.RESET}"""
        
        print(ascii_art)
        
        # Bot Info
        print(f"{Colors.BOLD}{Colors.GREEN}🤖 Bot Information:{Colors.RESET}")
        print(f"   {Colors.CYAN}├─{Colors.RESET} Name: {Colors.YELLOW}{self.user.name}#{self.user.discriminator}{Colors.RESET}")
        print(f"   {Colors.CYAN}├─{Colors.RESET} ID: {Colors.YELLOW}{self.user.id}{Colors.RESET}")
        print(f"   {Colors.CYAN}├─{Colors.RESET} Prefix: {Colors.YELLOW}{PREFIX}{Colors.RESET}")
        print(f"   {Colors.CYAN}└─{Colors.RESET} Owner ID: {Colors.YELLOW}{OWNER_ID}{Colors.RESET}")
        
        # Statistics
        total_members = sum(g.member_count for g in self.guilds)
        print(f"{Colors.BOLD}{Colors.GREEN}📊 Statistics:{Colors.RESET}")
        print(f"   {Colors.CYAN}├─{Colors.RESET} Servers: {Colors.YELLOW}{len(self.guilds):,}{Colors.RESET}")
        print(f"   {Colors.CYAN}├─{Colors.RESET} Users: {Colors.YELLOW}{total_members:,}{Colors.RESET}")
        print(f"   {Colors.CYAN}└─{Colors.RESET} Latency: {Colors.YELLOW}{round(self.latency * 1000)}ms{Colors.RESET}")
        
        # Status
        print(f"{Colors.BOLD}{Colors.GREEN}✅ Status:{Colors.RESET}")
        print(f"   {Colors.CYAN}└─{Colors.RESET} {Colors.GREEN}Bot is ONLINE and ready!{Colors.RESET}")
        
        print(f"{Colors.CYAN}{'='*63}{Colors.RESET}")
        
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="&help | LazyX Support"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(f"❌ You don't have permission to use this command!")
        
        if isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f"❌ I don't have the required permissions!")
        
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"⏰ Command on cooldown! Try again in {error.retry_after:.1f}s")
        
        if isinstance(error, commands.NotOwner):
            return await ctx.send(f"👑 This command is owner only!")
        
        print(f'{Colors.RED}Command Error:{Colors.RESET} {error}')

bot = LazyXTicketBot()

if __name__ == '__main__':
    print(f"{Colors.CYAN}{'='*63}")
    print(f"{Colors.YELLOW}          Starting LazyX Ticket Bot...{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*63}{Colors.RESET}")
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"{Colors.RED}{'='*63}")
        print(f"{Colors.RED}ERROR: {e}{Colors.RESET}")
        print(f"{Colors.RED}{'='*63}{Colors.RESET}")