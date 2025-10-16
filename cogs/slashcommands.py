import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import (
    create_error_embed, create_success_embed, 
    create_closing_embed, create_lock_embed,
    create_user_action_embed, create_log_embed
)
from config import COLORS, PRIORITY_EMOJIS, EMOJIS
import asyncio

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="close", description="Close the current ticket")
    async def close_ticket(self, interaction: discord.Interaction):
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, interaction.channel.id)
        
        if not ticket_data:
            error_embed = create_error_embed("This is not a ticket channel!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        closing_embed = create_closing_embed()
        await interaction.response.send_message(embed=closing_embed)
        
        user_id = ticket_data.get('user_id')
        user = interaction.guild.get_member(user_id)
        
        transcript_cog = self.bot.get_cog('Transcript')
        if transcript_cog:
            transcript = await transcript_cog.create_transcript(interaction.channel, ticket_data)
            
            logs_channel_id = self.bot.db.get_ticket_logs_channel(interaction.guild.id)
            if logs_channel_id:
                logs_channel = interaction.guild.get_channel(logs_channel_id)
                if logs_channel:
                    priority = ticket_data.get('priority', 'medium')
                    priority_emoji = PRIORITY_EMOJIS.get(priority, '🟡')
                    
                    log_embed = create_log_embed(
                        f"{EMOJIS['close']} Ticket Closed",
                        {
                            f"{EMOJIS['ticket']} Ticket": f"#{ticket_data.get('ticket_number', 0):04d}",
                            f"{EMOJIS['user']} Closed by": interaction.user.mention,
                            f"{EMOJIS['category']} Category": ticket_data.get('category'),
                            f"{EMOJIS['pencil']} Subject": ticket_data.get('subject'),
                            f"{EMOJIS['priority']} Priority": f"{priority_emoji} {priority.title()}"
                        }
                    )
                    await logs_channel.send(embed=log_embed, file=transcript)
        
        review_cog = self.bot.get_cog('Reviews')
        if review_cog and user:
            await review_cog.send_review_request(user, ticket_data, interaction.guild.id)
        
        await asyncio.sleep(5)
        await interaction.channel.delete()
        self.bot.db.delete_ticket(interaction.guild.id, interaction.channel.id)
    
    @app_commands.command(name="add", description="Add a user to the ticket")
    @app_commands.describe(user="User to add")
    async def add_user(self, interaction: discord.Interaction, user: discord.Member):
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, interaction.channel.id)
        
        if not ticket_data:
            error_embed = create_error_embed("This is not a ticket channel!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.add_user(user)
        else:
            await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
        
        action_embed = create_user_action_embed("add", interaction.user, user)
        await interaction.response.send_message(embed=action_embed)
    
    @app_commands.command(name="remove", description="Remove a user from the ticket")
    @app_commands.describe(user="User to remove")
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member):
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, interaction.channel.id)
        
        if not ticket_data:
            error_embed = create_error_embed("This is not a ticket channel!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.remove_user(user)
        else:
            await interaction.channel.set_permissions(user, overwrite=None)
        
        action_embed = create_user_action_embed("remove", interaction.user, user)
        await interaction.response.send_message(embed=action_embed)
    
    @app_commands.command(name="lock", description="Lock the ticket")
    async def lock_ticket(self, interaction: discord.Interaction):
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, interaction.channel.id)
        
        if not ticket_data:
            error_embed = create_error_embed("This is not a ticket channel!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        user = interaction.guild.get_member(ticket_data['user_id'])
        
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.edit(locked=True)
        else:
            await interaction.channel.set_permissions(user, send_messages=False)
        
        self.bot.db.update_ticket(interaction.guild.id, interaction.channel.id, locked=True)
        
        lock_embed = create_lock_embed(user, True)
        await interaction.response.send_message(embed=lock_embed)
    
    @app_commands.command(name="unlock", description="Unlock the ticket")
    async def unlock_ticket(self, interaction: discord.Interaction):
        ticket_data = self.bot.db.get_ticket(interaction.guild.id, interaction.channel.id)
        
        if not ticket_data:
            error_embed = create_error_embed("This is not a ticket channel!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        user = interaction.guild.get_member(ticket_data['user_id'])
        
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.edit(locked=False, archived=False)
        else:
            await interaction.channel.set_permissions(user, send_messages=True)
        
        self.bot.db.update_ticket(interaction.guild.id, interaction.channel.id, locked=False)
        
        lock_embed = create_lock_embed(user, False)
        await interaction.response.send_message(embed=lock_embed)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))