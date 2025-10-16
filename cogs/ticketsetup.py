import discord
from discord import ui
from discord.ext import commands
from discord import app_commands
from utils.embeds import create_preview_embed, create_error_embed, create_success_embed, create_setup_embed
from utils.views import TicketDropdownView, TicketButtonView
from config import COLORS, THREAD_TICKET, EMOJIS
import asyncio
import re

class PanelEditView(discord.ui.View):
    def __init__(self, interaction_or_ctx, bot, preview_msg):
        super().__init__(timeout=300)
        self.interaction_or_ctx = interaction_or_ctx
        self.bot = bot
        self.preview_msg = preview_msg
        self.panel_data = {
            'title': '🎫 Support Ticket',
            'description': 'Click below to create a ticket!',
            'color': str(COLORS['dark']),
            'image': None,
            'thumbnail': None
        }
    
    async def update_preview(self):
        preview_embed = create_preview_embed(self.panel_data)
        await self.preview_msg.edit(embed=preview_embed)
    
    def get_channel(self):
        if isinstance(self.interaction_or_ctx, discord.Interaction):
            return self.interaction_or_ctx.channel
        return self.interaction_or_ctx.channel
    
    def get_author(self):
        if isinstance(self.interaction_or_ctx, discord.Interaction):
            return self.interaction_or_ctx.user
        return self.interaction_or_ctx.author
    
    @discord.ui.button(label="Title", style=discord.ButtonStyle.blurple, row=0)
    async def title_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        
        await interaction.response.send_message(
            f"{EMOJIS['pencil']} **Send the new title for the panel:**",
            ephemeral=True
        )
        
        def check(m):
            return m.author == self.get_author() and m.channel == self.get_channel()
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            self.panel_data['title'] = msg.content
            await msg.delete()
            await self.update_preview()
        except asyncio.TimeoutError:
            pass
    
    @discord.ui.button(label="Description", style=discord.ButtonStyle.blurple, row=0)
    async def desc_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        
        await interaction.response.send_message(
            f"{EMOJIS['pencil']} **Send the new description for the panel:**",
            ephemeral=True
        )
        
        def check(m):
            return m.author == self.get_author() and m.channel == self.get_channel()
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=120)
            self.panel_data['description'] = msg.content
            await msg.delete()
            await self.update_preview()
        except asyncio.TimeoutError:
            pass
    
    @discord.ui.button(label="Image", style=discord.ButtonStyle.blurple, row=0)
    async def image_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        
        await interaction.response.send_message(
            f"{EMOJIS['sparkle']} **Send the image URL or type `none` to remove:**",
            ephemeral=True
        )
        
        def check(m):
            return m.author == self.get_author() and m.channel == self.get_channel()
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            if msg.content.lower() == 'none':
                self.panel_data['image'] = None
            else:
                self.panel_data['image'] = msg.content
            await msg.delete()
            await self.update_preview()
        except asyncio.TimeoutError:
            pass
    
    @discord.ui.button(label="Thumbnail", style=discord.ButtonStyle.blurple, row=0)
    async def thumb_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        
        await interaction.response.send_message(
            f"{EMOJIS['sparkle']} **Send the thumbnail URL or type `none` to remove:**",
            ephemeral=True
        )
        
        def check(m):
            return m.author == self.get_author() and m.channel == self.get_channel()
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            if msg.content.lower() == 'none':
                self.panel_data['thumbnail'] = None
            else:
                self.panel_data['thumbnail'] = msg.content
            await msg.delete()
            await self.update_preview()
        except asyncio.TimeoutError:
            pass
    
    @discord.ui.button(label="Colour", style=discord.ButtonStyle.blurple, row=1)
    async def color_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        
        await interaction.response.send_message(
            f"{EMOJIS['settings']} **Send the hex color code (e.g., #2F3136):**",
            ephemeral=True
        )
        
        def check(m):
            return m.author == self.get_author() and m.channel == self.get_channel()
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            color_hex = msg.content.replace('#', '')
            self.panel_data['color'] = str(int(color_hex, 16))
            await msg.delete()
            await self.update_preview()
        except (asyncio.TimeoutError, ValueError):
            pass
    
    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=1)
    async def submit_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        
        success_embed = create_success_embed(
            "Panel design saved! Moving to category setup...",
            self.get_author()
        )
        await interaction.response.send_message(embed=success_embed, ephemeral=True)
        self.stop()

class CategoryManageView(discord.ui.View):
    def __init__(self, interaction_or_ctx, bot, preview_msg, style, panel_data):
        super().__init__(timeout=600)
        self.interaction_or_ctx = interaction_or_ctx
        self.bot = bot
        self.preview_msg = preview_msg
        self.style = style
        self.panel_data = panel_data
        self.categories = []
        
        if style == "dropdown":
            self.setup_dropdown_buttons()
        else:
            self.setup_button_buttons()
    
    def get_channel(self):
        if isinstance(self.interaction_or_ctx, discord.Interaction):
            return self.interaction_or_ctx.channel
        return self.interaction_or_ctx.channel
    
    def get_author(self):
        if isinstance(self.interaction_or_ctx, discord.Interaction):
            return self.interaction_or_ctx.user
        return self.interaction_or_ctx.author
    
    def setup_dropdown_buttons(self):
        self.clear_items()
        
        add_btn = discord.ui.Button(label="Add Category", style=discord.ButtonStyle.green)
        add_btn.callback = self.add_category_callback
        self.add_item(add_btn)
        
        remove_btn = discord.ui.Button(label="Remove Category", style=discord.ButtonStyle.red)
        remove_btn.callback = self.remove_category_callback
        self.add_item(remove_btn)
        
        submit_btn = discord.ui.Button(label="Submit", style=discord.ButtonStyle.green, row=1)
        submit_btn.callback = self.submit_callback
        self.add_item(submit_btn)
    
    def setup_button_buttons(self):
        self.clear_items()
        
        colors = [
            ('red', 'Red', '🔴', discord.ButtonStyle.red),
            ('green', 'Green', '🟢', discord.ButtonStyle.green),
            ('blue', 'Blue', '🔵', discord.ButtonStyle.blurple),
            ('grey', 'Grey', '⚪', discord.ButtonStyle.grey),
        ]
        
        for color_name, label, emoji, style in colors:
            btn = discord.ui.Button(label=label, style=style, emoji=emoji, row=0)
            btn.callback = self.create_add_button_callback(color_name)
            self.add_item(btn)
        
        remove_btn = discord.ui.Button(label="Remove Category", style=discord.ButtonStyle.red, row=1)
        remove_btn.callback = self.remove_category_callback
        self.add_item(remove_btn)
        
        submit_btn = discord.ui.Button(label="Submit", style=discord.ButtonStyle.green, row=1)
        submit_btn.callback = self.submit_callback
        self.add_item(submit_btn)
    
    def create_add_button_callback(self, color):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.get_author():
                return await interaction.response.send_message("This is not your setup!", ephemeral=True)
            await self.add_category(interaction, color)
        return callback
    
    async def add_category_callback(self, interaction: discord.Interaction):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        await self.add_category(interaction)
    
    async def remove_category_callback(self, interaction: discord.Interaction):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        
        if not self.categories:
            error_embed = create_error_embed("No categories to remove!", self.get_author())
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        class RemoveSelect(discord.ui.Select):
            def __init__(self, parent_view):
                self.parent_view = parent_view
                options = [
                    discord.SelectOption(
                        label=cat['name'],
                        value=str(i),
                        emoji=cat.get('emoji')
                    ) for i, cat in enumerate(parent_view.categories)
                ]
                super().__init__(placeholder="Select category to remove...", options=options, min_values=1, max_values=1)
            
            async def callback(self, select_interaction: discord.Interaction):
                if select_interaction.user != self.parent_view.get_author():
                    return await select_interaction.response.send_message("This is not your setup!", ephemeral=True)
                
                cat_index = int(self.values[0])
                removed_cat = self.parent_view.categories.pop(cat_index)
                
                success_embed = create_success_embed(f"Removed **{removed_cat['name']}**!", self.parent_view.get_author())
                await select_interaction.response.send_message(embed=success_embed, ephemeral=True)
                await self.parent_view.update_preview()
        
        remove_view = discord.ui.View(timeout=60)
        remove_view.add_item(RemoveSelect(self))
        
        remove_embed = discord.Embed(
            title=f"{EMOJIS['settings']} Remove Category",
            description="Select a category from the dropdown below to remove it.",
            color=COLORS['red']
        )
        await interaction.response.send_message(embed=remove_embed, view=remove_view, ephemeral=True)
    
    async def submit_callback(self, interaction: discord.Interaction):
        if interaction.user != self.get_author():
            return await interaction.response.send_message("This is not your setup!", ephemeral=True)
        
        if not self.categories:
            error_embed = create_error_embed("Add at least one category!", self.get_author())
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        success_embed = create_success_embed("Setup complete! Sending panel...", self.get_author())
        await interaction.response.send_message(embed=success_embed, ephemeral=True)
        self.stop()
    
    async def update_preview(self):
        preview_embed = create_preview_embed(self.panel_data)
        
        if self.categories:
            categories_text = "".join([f"{cat.get('emoji', '•')} {cat['name']}" for cat in self.categories])
            preview_embed.add_field(
                name=f"{EMOJIS['category']} Categories",
                value=categories_text,
                inline=False
            )
        
        await self.preview_msg.edit(embed=preview_embed)
    
    def is_valid_emoji(self, text):
        emoji_pattern = re.compile(
            "["
            "U0001F600-U0001F64F"
            "U0001F300-U0001F5FF"
            "U0001F680-U0001F6FF"
            "U0001F1E0-U0001F1FF"
            "U00002702-U000027B0"
            "U000024C2-U0001F251"
            "]+", flags=re.UNICODE
        )
        custom_emoji_pattern = re.compile(r'<a?:w+:d+>')
        return emoji_pattern.match(text) or custom_emoji_pattern.match(text)
    
    async def add_category(self, interaction, color=None):
        await interaction.response.send_message(
            f"{EMOJIS['pencil']} Category setup started! Check the channel.",
            ephemeral=True
        )
        
        def check(m):
            return m.author == self.get_author() and m.channel == self.get_channel()
        
        try:
            # Category Name
            await self.get_channel().send(f"{EMOJIS['pencil']} **What's the name of the category?**")
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            cat_name = msg.content
            await msg.delete()
            
            # Emoji (Optional with validation)
            cat_emoji = None
            while True:
                await self.get_channel().send(f"{EMOJIS['sparkle']} **Send an emoji or type `none` to skip:**")
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                
                if msg.content.lower() == 'none':
                    await msg.delete()
                    break
                elif self.is_valid_emoji(msg.content):
                    cat_emoji = msg.content
                    await msg.delete()
                    break
                else:
                    error_msg = await self.get_channel().send(f"{EMOJIS['error']} **Invalid emoji! Please send a valid emoji or type `none`.**")
                    await msg.delete()
                    await asyncio.sleep(3)
                    await error_msg.delete()
            
            # Staff Roles (Optional with validation)
            staff_roles = []
            while True:
                await self.get_channel().send(f"{EMOJIS['staff']} **Mention staff roles or type `none` to skip:**")
                msg = await self.bot.wait_for('message', check=check, timeout=120)
                
                if msg.content.lower() == 'none':
                    await msg.delete()
                    break
                elif msg.role_mentions:
                    staff_roles = [role.id for role in msg.role_mentions]
                    await msg.delete()
                    break
                else:
                    error_msg = await self.get_channel().send(f"{EMOJIS['error']} **No valid roles mentioned! Please mention roles or type `none`.**")
                    await msg.delete()
                    await asyncio.sleep(3)
                    await error_msg.delete()
            
            category = {
                'name': cat_name,
                'emoji': cat_emoji,
                'staff_roles': staff_roles
            }
            
            if color:
                category['color'] = color
            
            self.categories.append(category)
            
            success_msg = await self.get_channel().send(f"{EMOJIS['success']} Added **{cat_name}**!")
            await asyncio.sleep(3)
            await success_msg.delete()
            
            await self.update_preview()
            
        except asyncio.TimeoutError:
            timeout_msg = await self.get_channel().send(f"{EMOJIS['warning']} Timeout! Category creation cancelled.")
            await asyncio.sleep(3)
            await timeout_msg.delete()

class TicketSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def setup_ticket_panel(self, interaction_or_ctx, style: str, channel: discord.TextChannel = None):
        is_interaction = isinstance(interaction_or_ctx, discord.Interaction)
        
        if is_interaction:
            guild = interaction_or_ctx.guild
            author = interaction_or_ctx.user
            response_channel = interaction_or_ctx.channel
        else:
            guild = interaction_or_ctx.guild
            author = interaction_or_ctx.author
            response_channel = interaction_or_ctx.channel
        
        channel = channel or response_channel
        
        setup_embed = create_setup_embed(
            "Ticket Setup - Customize Panel\n",
            f"**Style:** {style.title()}\n\nUse the buttons below to customize your ticket panel.\n"
            f"{EMOJIS['pencil']} **Title** - Set panel title\n"
            f"{EMOJIS['clipboard']} **Description** - Set panel description\n"
            f"{EMOJIS['sparkle']} **Image** - Set panel image\n"
            f"{EMOJIS['sparkle']} **Thumbnail** - Set panel thumbnail\n"
            f"{EMOJIS['settings']} **Colour** - Set embed color\n"
        )
        
        if is_interaction:
            await interaction_or_ctx.response.send_message(embed=setup_embed, ephemeral=True)
        
        preview_embed = create_preview_embed({
            'title': '🎫 Support Ticket',
            'description': 'Click below to create a ticket!',
            'color': str(COLORS['dark'])
        })
        preview_msg = await response_channel.send(content="**📝 Preview:**", embed=preview_embed)
        
        panel_view = PanelEditView(interaction_or_ctx, self.bot, preview_msg)
        control_msg = await response_channel.send(view=panel_view)
        
        await panel_view.wait()
        
        cat_setup_embed = create_setup_embed(
            "Ticket Setup - Add Categories\n",
            f"Add ticket categories using the buttons below.\n"
            f"{EMOJIS['success']} **Add Category** - Create new category\n"
            f"{EMOJIS['error']} **Remove Category** - Delete existing category\n"
            f"{EMOJIS['check']} **Submit** - Finish setup\n"
        )
        await control_msg.edit(embed=cat_setup_embed, view=None)
        
        category_view = CategoryManageView(interaction_or_ctx, self.bot, preview_msg, style, panel_view.panel_data)
        await control_msg.edit(view=category_view)
        
        await category_view.wait()
        
        panel_config = {
            'panel_data': panel_view.panel_data,
            'style': style,
            'categories': category_view.categories,
            'channel_id': channel.id,
            'thread_ticket': THREAD_TICKET
        }
        
        self.bot.db.set_guild_panel(guild.id, panel_config)
        
        final_embed = create_preview_embed(panel_view.panel_data)
        await channel.send(embed=final_embed)
        
        if style == "dropdown":
            ticket_view = TicketDropdownView(self.bot, category_view.categories)
        else:
            ticket_view = TicketButtonView(self.bot, category_view.categories)
        
        await channel.send(view=ticket_view)
        
        logs_channel = discord.utils.get(guild.channels, name="lazyx-ticket-logs")
        if not logs_channel:
            logs_channel = await guild.create_text_channel(name="lazyx-ticket-logs")
        self.bot.db.set_ticket_logs_channel(guild.id, logs_channel.id)
        
        success_embed = create_success_embed(
            f"{EMOJIS['trophy']} Setup complete in {channel.mention}!\n"
            f"**Logs Channel:** {logs_channel.mention}\n"
            f"**Categories Added:** {len(category_view.categories)}\n"
            f"**Style:** {style.title()}\n",
            author
        )
        await response_channel.send(embed=success_embed)
    
    @app_commands.command(name="ticketsetup", description="Setup ticket system")
    @app_commands.describe(style="Dropdown or Buttons")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(style=[
        app_commands.Choice(name="Dropdown", value="dropdown"),
        app_commands.Choice(name="Buttons", value="buttons")
    ])
    async def ticket_setup_slash(self, interaction: discord.Interaction, style: app_commands.Choice[str]):
        await self.setup_ticket_panel(interaction, style.value)

async def setup(bot):
    await bot.add_cog(TicketSetup(bot))