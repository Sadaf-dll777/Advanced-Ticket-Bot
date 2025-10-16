import discord
from discord import ui
from discord.ext import commands
from config import EMOJIS

class TicketModal(ui.Modal, title="Create Ticket"):
    subject = ui.TextInput(
        label="Subject",
        placeholder="Brief description of your issue",
        required=True,
        max_length=100,
        style=discord.TextStyle.short
    )
    
    description = ui.TextInput(
        label="Description",
        placeholder="Detailed description of your issue",
        required=True,
        max_length=1000,
        style=discord.TextStyle.paragraph
    )
    
    priority = ui.TextInput(
        label="Priority (low/medium/high/extreme)",
        placeholder="Enter: low, medium, high, or extreme",
        required=True,
        max_length=10,
        style=discord.TextStyle.short
    )
    
    def __init__(self, bot, category_data):
        super().__init__()
        self.bot = bot
        self.category_data = category_data
    
    async def on_submit(self, interaction: discord.Interaction):
        priority = self.priority.value.lower().strip()
        
        if priority not in ['low', 'medium', 'high', 'extreme']:
            from utils.embeds import create_error_embed
            error_embed = create_error_embed(
                "Invalid priority! Use: low, medium, high, or extreme",
                interaction.user
            )
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        ticket_data = {
            'user_id': interaction.user.id,
            'category': self.category_data['name'],
            'category_data': self.category_data,
            'subject': self.subject.value,
            'description': self.description.value,
            'priority': priority
        }
        
        cog = self.bot.get_cog('TicketCreation')
        if cog:
            await cog.handle_ticket_creation(interaction, ticket_data)

class TicketDropdownView(ui.View):
    def __init__(self, bot, categories):
        super().__init__(timeout=None)
        self.bot = bot
        self.categories = categories
        
        select = ui.Select(
            placeholder="Select a category to create a ticket",
            custom_id="ticket_category_select_persistent"
        )
        
        for category in categories:
            select.add_option(
                label=category['name'],
                value=category['name'],
                emoji=category.get('emoji')
            )
        
        select.callback = self.dropdown_callback
        self.add_item(select)
    
    async def dropdown_callback(self, interaction: discord.Interaction):
        category_name = interaction.data['values'][0]
        
        category_data = None
        for cat in self.categories:
            if cat['name'] == category_name:
                category_data = cat
                break
        
        if not category_data:
            from utils.embeds import create_error_embed
            error_embed = create_error_embed("Category not found!", interaction.user)
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        modal = TicketModal(self.bot, category_data)
        await interaction.response.send_modal(modal)

class TicketButtonView(ui.View):
    def __init__(self, bot, categories):
        super().__init__(timeout=None)
        self.bot = bot
        self.categories = categories
        
        color_map = {
            'red': discord.ButtonStyle.red,
            'green': discord.ButtonStyle.green,
            'blue': discord.ButtonStyle.blurple,
            'grey': discord.ButtonStyle.grey,
            'blurple': discord.ButtonStyle.blurple
        }
        
        for i, category in enumerate(categories[:25]):
            button = ui.Button(
                label=category['name'],
                style=color_map.get(category.get('color', 'blurple'), discord.ButtonStyle.blurple),
                emoji=category.get('emoji'),
                custom_id=f"ticket_button_persistent_{i}",
                row=i // 5
            )
            button.callback = self.create_button_callback(category)
            self.add_item(button)
    
    def create_button_callback(self, category_data):
        async def callback(interaction: discord.Interaction):
            modal = TicketModal(self.bot, category_data)
            await interaction.response.send_modal(modal)
        return callback