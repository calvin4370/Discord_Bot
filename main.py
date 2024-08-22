# main.py
import discord
import os
from settings import prefix, profile_photo
from Sebas import Sebas

# Newly added requirement for discord Python
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
sebas = None  # Initialize sebas (brain class) as None

@client.event
async def on_ready():
    # Initialise bot and turn online, start listening for events in server
    global sebas
    sebas = Sebas(client)

    print(f'{client.user} is online!')

@client.event
async def on_message(message):
    # Ignore messages sent by self
    if message.author == client.user:
        return

    # Auto-kick users who say banned word/phrase
    if any(banned_word in message.content.lower() for banned_word in sebas.banned_words):
        try:
            await message.channel.send(f"{message.author.mention} has been kicked for inappropriate language.")
            await message.author.kick(reason="Inappropriate language")
        except discord.Forbidden:
            await message.channel.send("I don't have permission to kick members.")
        except discord.HTTPException as e:
            await message.channel.send(f"An error occurred: {e}")
        return

    # Run commands if prefix is used correctly
    if message.content.startswith(prefix):
        words = str(message.content).split()
        command = words[0][len(prefix):]
        await sebas.run(command, message)

client.run(os.getenv('SebasTian_token'))