import discord
from discord.ext import commands
import chat_exporter
import io
from datetime import datetime

class Transcript(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def create_transcript(self, channel, ticket_data):
        try:
            transcript = await chat_exporter.export(
                channel,
                limit=None,
                tz_info="Asia/Kolkata",
                military_time=False,
                bot=self.bot
            )
            
            if transcript is None:
                transcript = await self.create_simple_transcript(channel, ticket_data)
            
            ticket_num = ticket_data.get('ticket_number', 0)
            filename = f"ticket-{ticket_num:04d}-transcript.html"
            
            transcript_file = discord.File(
                io.BytesIO(transcript.encode()),
                filename=filename
            )
            
            return transcript_file
            
        except Exception as e:
            print(f"Error creating transcript: {e}")
            return await self.create_simple_transcript(channel, ticket_data)
    
    async def create_simple_transcript(self, channel, ticket_data):
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            content = message.content or "[No content]"
            messages.append(f"[{timestamp}] {message.author}: {content}")
        
        transcript_text = "".join(messages)
        
        ticket_num = ticket_data.get('ticket_number', 0)
        filename = f"ticket-{ticket_num:04d}-transcript.txt"
        
        transcript_file = discord.File(
            io.BytesIO(transcript_text.encode()),
            filename=filename
        )
        
        return transcript_file

async def setup(bot):
    await bot.add_cog(Transcript(bot))