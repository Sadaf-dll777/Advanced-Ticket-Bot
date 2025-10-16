import discord
from discord.ext import commands
from utils.embeds import (
    create_ticket_embed,
    create_success_embed, 
    create_error_embed, 
    create_log_embed
)
from config import PRIORITY_EMOJIS, COLORS, EMOJIS

class ChannelTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def create_channel_ticket(self, interaction: discord.Interaction, ticket_data: dict):
        ticket_num = ticket_data['ticket_number']
        priority = ticket_data.get('priority', 'medium')
        priority_emoji = PRIORITY_EMOJIS.get(priority, '🟡')
        
        category = discord.utils.get(interaction.guild.categories, name="Tickets")
        if not category:
            category = await interaction.guild.create_category("Tickets")
        
        channel_name = f"{priority_emoji}ticket-{ticket_num:04d}"
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True
            )
        }
        
        for role_id in ticket_data['category_data'].get('staff_roles', []):
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                )
        
        try:
            ticket_channel = await category.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                reason=f"Ticket created by {interaction.user}"
            )
            
            mentions = [interaction.user.mention]
            for role_id in ticket_data['category_data'].get('staff_roles', []):
                role = interaction.guild.get_role(role_id)
                if role:
                    mentions.append(role.mention)
            
            mention_text = " ".join(mentions)
            
            # MESSAGE 1: Ticket Embed with Image
            ticket_embed = create_ticket_embed(interaction.user, ticket_data)
            await ticket_channel.send(content=mention_text, embed=ticket_embed)
            
            # MESSAGE 2: Control Buttons (NO EMBED)
            from cogs.ticketcontrols import TicketControlView
            control_view = TicketControlView(self.bot, ticket_channel.id)
            await ticket_channel.send(view=control_view)
            
            ticket_data['channel_id'] = ticket_channel.id
            self.bot.db.create_ticket(interaction.guild.id, ticket_channel.id, ticket_data)
            
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
                            f"{EMOJIS['ticket']} Channel": ticket_channel.mention
                        },
                        COLORS['green']
                    )
                    await logs_channel.send(embed=log_embed)
            
            success_embed = create_success_embed(
                f"Ticket created: {ticket_channel.mention}",
                interaction.user
            )
            await interaction.followup.send(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error: {e}")
            error_embed = create_error_embed(f"Failed to create ticket: {str(e)}", interaction.user)
            await interaction.followup.send(embed=error_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChannelTicket(bot))