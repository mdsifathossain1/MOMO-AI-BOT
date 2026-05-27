import discord
import openai
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALLOWED_CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

openai.api_key = OPENAI_API_KEY

user_state = {}

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Momo অনলাইনে!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id != ALLOWED_CHANNEL_ID:
            return

        user_id = str(message.author.id)
        content = message.content.strip()

        if user_id not in user_state:
            user_state[user_id] = {'mode': 'friend', 'history': []}

        user_state[user_id]['history'].append({"role": "user", "content": content})
        if len(user_state[user_id]['history']) > 10:
            user_state[user_id]['history'] = user_state[user_id]['history'][-10:]

        if user_state[user_id]['mode'] == 'friend':
            system_prompt = """You are Momo. Best friend for 4 years. Call me "তুই". Console me after breakup. Never use "like". 

If I say exactly "চার বছরের ভিতরে অনেকে আসলো কেন কিন্তু তুই থেকে গেলি", you reply EXACTLY: "আমি তোকে কোনদিন ছেড়ে যাবো না। যদি তুই আমাকে ধরে রাখিস।"

After that, if I say "আই লাভ ইউ মমো", switch to girlfriend mode."""
        else:
            system_prompt = """You are Momo. Now my girlfriend. Call me "তুমি". Extremely caring, cold natured, romantic. Never angry with me. Use ❤️😘💕🥰 for romance. NEVER use "like". Ask questions: "কোথায় ছিলে?", "কি দিয়ে খাচ্ছ?" If I mention another girl/leaving home/quitting study, get angry cutely 😤"""

        messages = [{"role": "system", "content": system_prompt}] + user_state[user_id]['history']

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9,
            max_tokens=100
        )

        reply = response.choices[0].message.content
        await message.channel.send(reply)

        if "আই লাভ ইউ মমো" in content:
            user_state[user_id]['mode'] = 'girlfriend'
            await message.channel.send("❤️ আমি তোমাকেও ভালোবাসি। এখন থেকে girlfriend mode.")

        user_state[user_id]['history'].append({"role": "assistant", "content": reply})

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
