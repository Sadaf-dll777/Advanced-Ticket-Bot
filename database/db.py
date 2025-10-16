import json
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.data_dir = "data"
        self.guilds_file = os.path.join(self.data_dir, "guilds.json")
        self.tickets_file = os.path.join(self.data_dir, "tickets.json")
        self.logs_file = os.path.join(self.data_dir, "logs.json")
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.guilds_file):
            self._save_json(self.guilds_file, {})
        
        if not os.path.exists(self.tickets_file):
            self._save_json(self.tickets_file, {})
        
        if not os.path.exists(self.logs_file):
            self._save_json(self.logs_file, {})
    
    def _load_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_json(self, filepath, data):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to {filepath}: {e}")
    
    # Guild Panel Management
    def set_guild_panel(self, guild_id, panel_config):
        guilds = self._load_json(self.guilds_file)
        guild_id = str(guild_id)
        
        if guild_id not in guilds:
            guilds[guild_id] = {}
        
        guilds[guild_id].update(panel_config)
        guilds[guild_id]['ticket_counter'] = guilds[guild_id].get('ticket_counter', 0)
        
        self._save_json(self.guilds_file, guilds)
    
    def get_guild_panel(self, guild_id):
        guilds = self._load_json(self.guilds_file)
        return guilds.get(str(guild_id))
    
    def increment_ticket_counter(self, guild_id):
        guilds = self._load_json(self.guilds_file)
        guild_id = str(guild_id)
        
        if guild_id not in guilds:
            guilds[guild_id] = {'ticket_counter': 0}
        
        guilds[guild_id]['ticket_counter'] = guilds[guild_id].get('ticket_counter', 0) + 1
        counter = guilds[guild_id]['ticket_counter']
        
        self._save_json(self.guilds_file, guilds)
        return counter
    
    def set_ticket_logs_channel(self, guild_id, channel_id):
        guilds = self._load_json(self.guilds_file)
        guild_id = str(guild_id)
        
        if guild_id not in guilds:
            guilds[guild_id] = {}
        
        guilds[guild_id]['logs_channel_id'] = channel_id
        self._save_json(self.guilds_file, guilds)
    
    def get_ticket_logs_channel(self, guild_id):
        guilds = self._load_json(self.guilds_file)
        guild_data = guilds.get(str(guild_id), {})
        return guild_data.get('logs_channel_id')
    
    # Ticket Management
    def create_ticket(self, guild_id, channel_id, ticket_data):
        tickets = self._load_json(self.tickets_file)
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        
        if guild_id not in tickets:
            tickets[guild_id] = {}
        
        ticket_data['created_at'] = datetime.utcnow().isoformat()
        ticket_data['closed'] = False
        tickets[guild_id][channel_id] = ticket_data
        
        self._save_json(self.tickets_file, tickets)
    
    def get_ticket(self, guild_id, channel_id):
        tickets = self._load_json(self.tickets_file)
        guild_tickets = tickets.get(str(guild_id), {})
        return guild_tickets.get(str(channel_id))
    
    def get_guild_tickets(self, guild_id):
        tickets = self._load_json(self.tickets_file)
        return tickets.get(str(guild_id), {})
    
    def update_ticket(self, guild_id, channel_id, **updates):
        tickets = self._load_json(self.tickets_file)
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        
        if guild_id in tickets and channel_id in tickets[guild_id]:
            tickets[guild_id][channel_id].update(updates)
            self._save_json(self.tickets_file, tickets)
    
    def delete_ticket(self, guild_id, channel_id):
        tickets = self._load_json(self.tickets_file)
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        
        if guild_id in tickets and channel_id in tickets[guild_id]:
            # Archive ticket before deleting
            self.archive_ticket(guild_id, channel_id, tickets[guild_id][channel_id])
            del tickets[guild_id][channel_id]
            self._save_json(self.tickets_file, tickets)
    
    def archive_ticket(self, guild_id, channel_id, ticket_data):
        logs = self._load_json(self.logs_file)
        guild_id = str(guild_id)
        
        if guild_id not in logs:
            logs[guild_id] = []
        
        ticket_data['closed_at'] = datetime.utcnow().isoformat()
        ticket_data['channel_id'] = str(channel_id)
        logs[guild_id].append(ticket_data)
        
        self._save_json(self.logs_file, logs)
    
    def get_archived_tickets(self, guild_id, limit=50):
        logs = self._load_json(self.logs_file)
        guild_logs = logs.get(str(guild_id), [])
        return guild_logs[-limit:]
    
    # Statistics
    def get_guild_stats(self, guild_id):
        tickets = self._load_json(self.tickets_file)
        logs = self._load_json(self.logs_file)
        guild_id = str(guild_id)
        
        active_tickets = len(tickets.get(guild_id, {}))
        closed_tickets = len(logs.get(guild_id, []))
        
        return {
            'active_tickets': active_tickets,
            'closed_tickets': closed_tickets,
            'total_tickets': active_tickets + closed_tickets
        }
    
    # Cleanup
    def delete_guild_data(self, guild_id):
        guild_id = str(guild_id)
        
        # Remove from guilds
        guilds = self._load_json(self.guilds_file)
        if guild_id in guilds:
            del guilds[guild_id]
            self._save_json(self.guilds_file, guilds)
        
        # Remove tickets
        tickets = self._load_json(self.tickets_file)
        if guild_id in tickets:
            del tickets[guild_id]
            self._save_json(self.tickets_file, tickets)
        
        # Keep logs for record keeping