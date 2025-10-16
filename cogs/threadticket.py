import discord
from discord.ext import commands
from utils.embeds import (
    create_ticket_embed,
    create_success_embed, 
    create_error_embed, 
    create_log_embed
)
from config import PRIORITY_EMOJIS, COLORS, EMOJIS

class ThreadTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def create_thread_ticket(self, interaction: discord.Interaction, ticket_data: dict):
        ticket_num = ticket_data['ticket_number']
        priority = ticket_data.get('priority', 'medium')
        priority_emoji = PRIORITY_EMOJIS.get(priority, '🟡')
        
        thread_name = f"{priority_emoji}ticket-{ticket_num:04d}"
        
        try:
            thread = await interaction.channel.create_thread(
                name=thread_name,
                type=discord.ChannelType.private_thread,
                reason=f"Ticket created by {interaction.user}"
            )
            
            await thread.add_user(interaction.user)
            
            for role_id in ticket_data['category_data'].get('staff_roles', []):
                role = interaction.guild.get_role(role_id)
                if role:
                    for member in role.members:
                        try:
                            await thread.add_user(member)
                        except:
                            pass
            
            mentions = [interaction.user.mention]
            for role_id in ticket_data['category_data'].get('staff_roles', []):
                role = interaction.guild.get_role(role_id)
                if role:
                    mentions.append(role.mention)
            
            mention_text = " ".join(mentions)
            
            # MESSAGE 1: Ticket Embed with Image
            ticket_embed = create_ticket_embed(interaction.user, ticket_data)
            await thread.send(content=mention_text, embed=ticket_embed)
            
            # MESSAGE 2: Control Buttons (NO EMBED)
            from cogs.ticketcontrols import TicketControlView
            control_view = TicketControlView(self.bot, thread.id)
            await thread.send(view=control_view)
            
            ticket_data['channel_id'] = thread.id
            self.bot.db.create_ticket(interaction.guild.id, thread.id, ticket_data)
            
            logs_channel_id = self.bot.db.get_ticket_logs_channel(interaction.guild.id)
            if logs_channel_id:
                logs_channel = interaction.guild.get_channel(logs_channel_id)
                if logs_channel:
                    log_embed = create_log_embed(
                        f"{EMOJIS['ticket']} Ticket Created",
                        {
                            f"{EMOJIS['user']} User": interaction.user.mention,
                            f"{EMOJIS['category']} Category": ticket_data['category'],
                            f"{EMOJIS['pencil']} Subject": ticket_data['subject'],
                            f"{EMOJIS['priority']} Priority": f"{priority_emoji} {priority.title()}",
                            f"{EMOJIS['ticket']} Thread": thread.mention
                        },
                        COLORS['green']
                    )
                    await logs_channel.send(embed=log_embed)
            
            success_embed = create_success_embed(
                f"Ticket created: {thread.mention}",
                interaction.user
            )
            await interaction.followup.send(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error: {e}")
            error_embed = create_error_embed(f"Failed to create ticket: {str(e)}", interaction.user)
            await interaction.followup.send(embed=error_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ThreadTicket(bot))