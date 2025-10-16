import discord
from config import COLORS, PRIORITY_COLORS, PRIORITY_EMOJIS, EMOJIS, RATING_EMOJIS, TICKET_EMBED_IMAGE
from datetime import datetime

def create_preview_embed(panel_data: dict) -> discord.Embed:
    embed = discord.Embed(
        title=panel_data.get('title', '🎫 Support Ticket'),
        description=panel_data.get('description', 'Click below to create a ticket!'),
        color=int(panel_data.get('color', COLORS['dark'])),
        timestamp=datetime.utcnow()
    )
    
    if panel_data.get('image'):
        embed.set_image(url=panel_data['image'])
    
    if panel_data.get('thumbnail'):
        embed.set_thumbnail(url=panel_data['thumbnail'])
    
    embed.set_footer(text="LazyX Ticket System")
    return embed

def create_ticket_embed(user: discord.Member, ticket_data: dict) -> discord.Embed:
    priority = ticket_data.get('priority', 'medium')
    priority_emoji = PRIORITY_EMOJIS.get(priority, '🟡')
    
    # Main embed - exactly like image
    embed = discord.Embed(
        title=f"{EMOJIS['ticket']} Support Ticket",
        description=f"Welcome to your support ticket, {user.mention}!\n"
                   f"Our support team has been notified and will assist you shortly.\n"
                   f"Please provide any additional details about your issue below.\n",
        color=COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    # Single field with all ticket information
    ticket_info = (
        f"{EMOJIS['clipboard']} **Ticket Information**\n"
        f"**Category:** {ticket_data.get('category', 'General')}\n"
        f"**Subject:** {ticket_data.get('subject', 'No subject')}\n"
        f"**Priority:** {priority_emoji} {priority.title()}\n"
        f"**Created:** <t:{int(datetime.utcnow().timestamp())}:R>\n"
        f"{EMOJIS['pencil']} **Issue Description\n**"
        f"```{ticket_data.get('description', 'No description provided')}```"
    )
    
    embed.add_field(
        name="​",
        value=ticket_info,
        inline=False
    )
    
    # Set author
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    
    # Set footer with ticket number
    embed.set_footer(
        text=f"LazyX Devs Support System • Ticket Management | {datetime.utcnow().strftime('%m/%d/%Y %I:%M %p')}"
    )
    
    embed.set_image(url=TICKET_EMBED_IMAGE)
    
    return embed

def create_error_embed(message: str, user: discord.Member = None) -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJIS['error']} Error",
        description=message,
        color=COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    if user:
        embed.set_footer(text=f"Requested by {user}", icon_url=user.display_avatar.url)
    
    return embed

def create_success_embed(message: str, user: discord.Member = None) -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJIS['success']} Success",
        description=message,
        color=COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    if user:
        embed.set_footer(text=f"Requested by {user}", icon_url=user.display_avatar.url)
    
    return embed

def create_info_embed(title: str, message: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJIS['info']} {title}",
        description=message,
        color=COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text="LazyX Ticket System")
    return embed

def create_log_embed(title: str, fields: dict, color: int = None) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        color=color or COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    for name, value in fields.items():
        embed.add_field(name=name, value=value, inline=True)
    
    embed.set_footer(text="LazyX Support Logs")
    return embed

def create_closing_embed() -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJIS['close']} Closing Ticket",
        description=f"{EMOJIS['time']} **This ticket will be closed in 5 seconds...**\n"
                   f"{EMOJIS['transcript']} Generating transcript and saving logs.\n"
                   f"{EMOJIS['inbox']} Sending copy to your DMs.\n",
        color=COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text="Thank you for contacting support!")
    return embed

def create_claim_embed(claimer: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJIS['claim']} Ticket Claimed",
        description=f"{claimer.mention} has claimed this ticket and will handle your request!\n"
                   f"{EMOJIS['sparkle']} You're in good hands!\n",
        color=COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    embed.set_author(name=claimer.display_name, icon_url=claimer.display_avatar.url)
    embed.set_footer(text="LazyX Support")
    return embed

def create_priority_change_embed(old_priority: str, new_priority: str) -> discord.Embed:
    old_emoji = PRIORITY_EMOJIS.get(old_priority, '🟡')
    new_emoji = PRIORITY_EMOJIS.get(new_priority, '🟡')
    
    embed = discord.Embed(
        title=f"{EMOJIS['priority']} Priority Updated",
        description=f"Ticket priority has been changed:\n"
                   f"**From:** {old_emoji} {old_priority.title()}\n"
                   f"**To:** {new_emoji} {new_priority.title()}",
        color=PRIORITY_COLORS.get(new_priority, COLORS['dark']),
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text="Priority Level Changed")
    return embed

def create_lock_embed(user: discord.Member, locked: bool) -> discord.Embed:
    if locked:
        embed = discord.Embed(
            title=f"{EMOJIS['lock']} Ticket Locked",
            description=f"This ticket has been locked.\n"
                       f"{user.mention} cannot send messages until unlocked.\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
    else:
        embed = discord.Embed(
            title=f"{EMOJIS['unlock']} Ticket Unlocked",
            description=f"This ticket has been unlocked.\n"
                       f"{user.mention} can now send messages.\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
    
    embed.set_footer(text="LazyX Support")
    return embed

def create_user_action_embed(action: str, user: discord.Member, target: discord.Member) -> discord.Embed:
    if action == "add":
        embed = discord.Embed(
            title=f"{EMOJIS['success']} User Added",
            description=f"{target.mention} has been added to this ticket.\n"
                       f"They can now view and participate in this conversation.\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
    else:
        embed = discord.Embed(
            title=f"{EMOJIS['close']} User Removed",
            description=f"{target.mention} has been removed from this ticket.\n"
                       f"They can no longer access this conversation.\n",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
    
    embed.set_footer(text=f"Action by {user}", icon_url=user.display_avatar.url)
    return embed

def create_review_request_embed(ticket_data: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJIS['star']} Your Ticket Has Been Closed",
        description=f"Thank you for contacting our support team!\n"
                   f"{EMOJIS['heart']} **We'd love to hear about your experience.\n**"
                   f"Your feedback helps us improve our services.",
        color=COLORS['gold'],
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name=f"{EMOJIS['ticket']} Ticket Summary",
        value=f"**Ticket:** #{ticket_data.get('ticket_number', 0):04d}\n"
              f"**Category:** {ticket_data.get('category', 'N/A')}\n"
              f"**Subject:** {ticket_data.get('subject', 'N/A')}\n",
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJIS['arrow_down']} Leave a Review",
        value="Click the button below to share your experience!",
        inline=False
    )
    
    embed.set_footer(text="Your feedback matters! • LazyX Support")
    return embed

def create_review_submitted_embed() -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJIS['success']} Thank You for Your Feedback!",
        description=f"{EMOJIS['heart']} Your review has been submitted successfully!\n"
                   f"We appreciate you taking the time to share your experience.\n"
                   f"Your feedback helps us provide better support.\n",
        color=COLORS['gold'],
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text="LazyX Support Team")
    return embed

def create_review_post_embed(review_data: dict, user: discord.Member) -> discord.Embed:
    rating = review_data.get('rating', 5)
    rating_emoji = RATING_EMOJIS.get(rating, '⭐')
    
    embed = discord.Embed(
        title=f"{EMOJIS['review']} New Support Review",
        description=f"{rating_emoji} **{rating}/5 Stars**\n",
        color=COLORS['gold'],
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name=f"{EMOJIS['ticket']} Ticket Information",
        value=f"**Ticket:** #{review_data.get('ticket_number', 0):04d}\n"
              f"**Category:** {review_data.get('category', 'N/A')}\n"
              f"**Customer:** {user.mention}\n",
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJIS['staff']} Most Helpful Staff",
        value=review_data.get('staff_member', 'Not specified'),
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJIS['pencil']} Customer Feedback",
        value=review_data.get('feedback', 'No feedback provided'),
        inline=False
    )
    
    if review_data.get('suggestions'):
        embed.add_field(
            name=f"{EMOJIS['sparkle']} Suggestions for Improvement",
            value=review_data['suggestions'],
            inline=False
        )
    
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    embed.set_footer(text="Customer Review • LazyX Support")
    return embed

def create_setup_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"{EMOJIS['settings']} {title}",
        description=description,
        color=COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text="Ticket System Setup")
    return embed