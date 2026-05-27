import discord
import requests
import os
import json

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
ALLOWED_CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# Hugging Face free model (No OpenAI needed)
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

user_state = {}
conversation_history = {}

def query_huggingface(prompt, user_id):
    # Keep last 5 messages for context
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    conversation_history[user_id].append(prompt)
    if len(conversation_history[user_id]) > 5:
        conversation_history[user_id] = conversation_history[user_id][-5:]
    
    context = " ".join(conversation_history[user_id])
    
    payload = {
        "inputs": context,
        "parameters": {
            "max_length": 100,
            "temperature": 0.9,
            "do_sample": True
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        reply = result[0]['generated_text'] if isinstance(result, list) else result['generated_text']
        # Clean up reply
        reply = reply.replace(prompt, "").strip()
        if not reply:
            reply = "হুম 😊"
        return reply[:200]  # Short replies
    else:
        return "আমি এখন একটু ব্যস্ত 😅 একটু পরে কথা বলি?"

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Momo অনলাইনে! (Hugging Face ফ্রি ভার্সন) 💕')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id != ALLOWED_CHANNEL_ID:
            return

        user_id = str(message.author.id)
        content = message.content.strip()
        
        if user_id not in user_state:
            user_state[user_id] = {'mode': 'friend', 'history': []}
        
        # Store history
        user_state[user_id]['history'].append(content)
        if len(user_state[user_id]['history']) > 10:
            user_state[user_id]['history'] = user_state[user_id]['history'][-10:]
        
        # Check for love trigger
        if user_state[user_id]['mode'] == 'friend':
            if "চার বছরের ভিতরে অনেকে আসলো কেন কিন্তু তুই থেকে গেলি" in content:
                await message.channel.send("আমি তোকে কোনদিন ছেড়ে যাবো না। যদি তুই আমাকে ধরে রাখিস।")
                return
        
        if "আই লাভ ইউ মমো" in content:
            user_state[user_id]['mode'] = 'girlfriend'
            await message.channel.send("❤️ আমি তোমাকেও ভালোবাসি। এখন থেকে girlfriend mode. তোমাকে ভালোবাসি 😘")
            return
        
        # Build prompt based on mode
        if user_state[user_id]['mode'] == 'friend':
            prompt = f"""You are Momo. My best friend for 4 years. You call me "তুই". Console me, be caring. Use short replies. Never use "like". Reply in Bangla mixed with English: {content}"""
        else:
            prompt = f"""You are Momo. Now my girlfriend. You call me "তুমি". Extremely caring, loving, romantic. Use ❤️😘💕🥰. Never use "like". Ask questions like: কোথায় ছিলে? কি দিয়ে খাচ্ছ? Short replies only. Reply in Bangla: {content}"""
        
        # Get AI response
        reply = query_huggingface(prompt, user_id)
        
        # Add girlfriend mode flavor
        if user_state[user_id]['mode'] == 'girlfriend':
            if "কোথায়" not in reply and "কি" not in reply and "কেমন" not in reply:
                reply += " ❤️ তোমার দিন কেমন যাচ্ছে?"
        
        await message.channel.send(reply)

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
