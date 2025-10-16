import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '&'
OWNER_ID = 1382744437049790495

THREAD_TICKET = True
DEFAULT_TICKET_CATEGORY = "Tickets"

OWNER_WEBHOOK_URL = os.getenv('OWNER_WEBHOOK_URL')

REVIEW_ENABLED = True
TICKET_EMBED_IMAGE = "https://cdn.discordapp.com/attachments/1424289886747365418/1425011587030188096/15946.jpg?ex=68e608f5&is=68e4b775&hm=72f6781501ad4aa2d5d395a3efcde14b9ed952c9d7e52f482dfdc38ffce3ac42&"

COLORS = {
    'success': 0x2F3136,
    'error': 0x2F3136,
    'info': 0x2F3136,
    'warning': 0x2F3136,
    'primary': 0x2F3136,
    'blurple': 0x5865F2,
    'black': 0x000000,
    'dark': 0x2F3136,
    'gold': 0xFFD700,
    'green': 0x43B581,
    'red': 0xED4245,
}

PRIORITY_EMOJIS = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🟠',
    'extreme': '🔴'
}

PRIORITY_COLORS = {
    'low': 0x43B581,
    'medium': 0xFAA61A,
    'high': 0xF26522,
    'extreme': 0xED4245
}

EMOJIS = {
    'ticket': '<:icon_ticket:1424793495427616909>',
    'lock': '<:icon_locked:1424793667259863163>',
    'unlock': '<:icons_unlock:1424793648402268160>',
    'delete': '<:icon_bin:1425000109216763944>',
    'claim': '<:bye:1424995824999596042>',
    'transcript': '<:clipboard1:1424969535651446837>',
    'success': '<:icon_tick:1424794374767906938>',
    'error': '<:icons_cross:1424794344292094084>',
    'info': '<:icons_info:1424794337857896532>',
    'priority': '<a:lighting_icons:1424969456177778729>',
    'user': '<:icons_Person:1424969501925052589>',
    'category': '<:icons_folder:1424969505318375576>',
    'time': '<:icons_clock:1424969510846205982>',
    'close': '<:icons_cross:1424794344292094084>',
    'staff': '<:people_icons:1424969497449861222>',
    'pencil': '<:icon_write:1424969520958935164>',
    'warning': '<:warning:1424969528521003059>',
    'settings': '<:gear_icons:1424969532275163207>',
    'clipboard': '<:clipboard1:1424969535651446837>',
    'inbox': '<:welcome:1424969538855899157>',
    'check': '<:icon_tick:1424794374767906938>',
    'cross': '<:icons_cross:1424794344292094084>',
    'arrow_right': '<:icon_right_arrow:1424997270000111696>',
    'arrow_down': '<:icons_arrow:1424997209346412575>',
    'dot': '<a:dot:1424997525458518016>',
    'sparkle': '<a:sparkles_sparkles:1424989855880052827>',
    'tools': '<:icons_wrench:1424969542366400574>',
    'bell': '<:icon_bell:1424997788889911377>',
    'pin': '<:icons_pin:1424997956699947100>',
    'star': '<:glowingstar:1424969557621215302>',
    'heart': '<a:hearts1:1424998350331318313>',
    'trophy': '<:Target:1424969552676257844>',
    'review': '<:Rise:1424969549144526878>',
    'fire': '<a:iconop:1424998743094202409>',
    'crown': '<:LM_Icons_Crown:1424969545759719554>',
    'shield': '<:icon_sheild:1425000128112230512>',
    'clock': '<:icons_clock:1424969510846205982>',
}

RATING_EMOJIS = {
    1: '⭐',
    2: '⭐⭐',
    3: '⭐⭐⭐',
    4: '⭐⭐⭐⭐',
    5: '⭐⭐⭐⭐⭐'
}