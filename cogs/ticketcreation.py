import discord
from discord.ext import commands
from utils.embeds import create_error_embed
from config import THREAD_TICKET
from datetime import datetime

class TicketCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_ticket_creation(self, interaction: discord.Interaction, ticket_data: dict):
        panel_config = self.bot.db.get_guild_panel(interaction.guild.id)
        if not panel_config:
            error_embed = create_error_embed("Ticket system not configured!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        guild_tickets = self.bot.db.get_guild_tickets(interaction.guild.id)
        for tid, tdata in guild_tickets.items():
            if tdata['user_id'] == interaction.user.id and not tdata.get('closed'):
                existing_channel = interaction.guild.get_channel(tdata['channel_id'])
                if existing_channel:
                    error_embed = create_error_embed(
                        f"You already have an open ticket: {existing_channel.mention}",
                        interaction.user
                    )
                    return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        ticket_num = self.bot.db.increment_ticket_counter(interaction.guild.id)
        
        ticket_data['panel_image'] = panel_config['panel_data'].get('image')
        ticket_data['ticket_number'] = ticket_num
        ticket_data['created_at'] = datetime.utcnow().isoformat()
        ticket_data['closed'] = False
        ticket_data['locked'] = False
        
        if panel_config.get('thread_ticket', THREAD_TICKET):
            cog = self.bot.get_cog('ThreadTicket')
            if cog:
                await cog.create_thread_ticket(interaction, ticket_data)
        else:
            cog = self.bot.get_cog('ChannelTicket')
            if cog:
                await cog.create_channel_ticket(interaction, ticket_data)

async def setup(bot):
    await bot.add_cog(TicketCreation(bot))