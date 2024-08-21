# main.py
import discord
import os
from settings import prefix
from Sebas import Sebas

# Newly added requirement for discord Python
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
sebas = None  # Initialize sebas (brain class) as None

@client.event
async def on_ready():
    global sebas
    sebas = Sebas(client)
    print(f'{client.user} is online!')

@client.event
async def on_message(message):
    # Ignore messages sent by self
    if message.author == client.user:
        return

    if message.content.startswith(prefix):
        words = message.content.split()
        command = words[0][len(prefix):]
        await sebas.run(command, message)

client.run(os.getenv('SebasTian_token'))