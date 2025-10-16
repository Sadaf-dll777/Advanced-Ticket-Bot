# 🎫 LazyX Ticket Bot

A powerful Discord ticket management system with modern UI and advanced features.

---

## ✨ Features

- ✅ Multi-category ticket system
- ✅ Interactive button & dropdown panels
- ✅ Priority levels (Low, Medium, High, Extreme)
- ✅ Automatic HTML transcripts
- ✅ Staff-only controls with permissions
- ✅ Review system for feedback
- ✅ Persistent buttons (work after restart)
- ✅ Custom prefix support
- ✅ Modern dark theme UI

---

## 📦 Installation

### Requirements
- Python 3.10 or higher
- Discord Bot Token

### Setup Steps

**1. Clone the repository**
```
git clone https://github.com/Azhaan4130/Advanced-Ticket-Bot.git
cd Advanced-Ticket-Bot
```

**2. Install dependencies**
```
pip install -r requirements.txt
```

**3. Create `.env` file**
```
DISCORD_TOKEN=your_bot_token_here
OWNER_WEBHOOK_URL=your_webhook_url_here
```

**4. Edit `config.py`**
```
PREFIX = '.'
OWNER_ID = your_discord_id
```

**5. Run the bot**
```
python LazyX.py
```

---

## 🛠️ Configuration

Run `/ticketsetup` in your server to:
- Add ticket categories
- Assign staff roles
- Set logs channel
- Deploy ticket panel

---

## 📝 Commands

### General Commands
```
/help       - Help menu
/ping       - Bot latency
/uptime     - Bot uptime
/botinfo    - Bot information
/stats      - Statistics
/invite     - Invite bot
/support    - Support server
```

### Ticket Management
```
/ticketsetup      - Setup wizard (Admin)
Close Button      - Close ticket (Staff)
Claim Button      - Claim ticket (Staff)
Priority Button   - Change priority (Staff)
```

### Developer Commands (Owner Only)
```
.sync         - Sync slash commands
.reload       - Reload a cog
.reloadall    - Reload all cogs
.servers      - List servers
.shutdown     - Shutdown bot
```

---

## 📁 Project Structure

```
LazyX-Ticket-Bot/
├── bot.py
├── config.py
├── requirements.txt
├── .env
│
├── cogs/
│   ├── general.py
│   ├── botinfo.py
│   ├── onmention.py
│   ├── dev.py
│   ├── ticketsetup.py
│   ├── ticketcreation.py
│   ├── ticketcontrols.py
│   ├── channelticket.py
│   ├── threadticket.py
│   ├── transcript.py
│   ├── reviews.py
│   └── ownerlogging.py
│
├── database/
│   └── db.py
│
├── utils/
│   ├── embeds.py
│   └── views.py
│
└── data/
    ├── guilds.json
    └── tickets.json
```

---

## 🎨 Customization

Edit colors in `config.py`:
```
COLORS = {
    'dark': 0x2F3136,
    'green': 0x43B581,
    'red': 0xED4245,
}
```

---

## ⚠️ Important - Credits & Usage

### 📹 Video Content Creators

**If you're making a video/tutorial about this bot, CREDITS ARE MANDATORY!**

You **MUST** include:
- ✅ **Bot Name:** LazyX Ticket Bot
- ✅ **Developer:** LazyX Development
- ✅ **GitHub Link:** [Github](https://github.com/Azhaan4130/Advanced-Ticket-Bot.git)
- ✅ **Discord:** [Discord](https://discord.gg/rzB3GcWmtx)

### ✅ Acceptable Use
- ✓ Use in your Discord server
- ✓ Modify for personal use
- ✓ Learn from the code
- ✓ Make videos WITH credits

### ❌ Not Allowed
- ✗ Claim as your own
- ✗ Remove credits from code
- ✗ Sell or monetize without permission
- ✗ Make videos WITHOUT credits

**Violation of credit requirements may result in DMCA takedown.**

