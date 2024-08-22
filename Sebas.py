import requests
import json
import os
import openai
import discord
from settings import version

class Sebas:
    def __init__(self, client):
        self.client = client

        # Bot commands (command_str: command_function)
        self.commands = {
            'help': self.help,
            'version': self.version,
            'say': self.say,
            'quote': self.quote,
            'role': self.assign_role,
            'update_banned_words': self.update_banned_word_list,
            'banned_words': self.check_banned_words,
            'weather': self.weather,
            'clear': self.clear,
            'chatgpt': self.chatgpt,
        }

        # Banned words / phrases
        self.banned_words = []


    async def run(self, command, message):
        if command in self.commands:
            await self.commands[command](message)


    async def help(self, message):
        reply = '''Use $<command> to call the bot\n
        $help: Get a list of commands\n
        $version: Get the version of the bot\n
        $say <message>: Command me to say something\n
        $role <role>: Get the role assigned to yourself\n
        $update_banned_words: Update the list of banned words/phrases for the server\n
        $banned_words: Check the list of banned words/phrases for the server\n

        APIs:
        $quote: Get a random quote from a famous person\n
        $weather <city>: Gives the current weather of the specified city\n
        $chatgpt: Ask ChatGPT a question'''
        await message.channel.send(reply)


    async def version(self, message):
        reply = f'My current version is v{version}'
        await message.channel.send(reply)


    async def say(self, message):
        '''
        Deletes the user's command and says out their text as if it is the bot saying the message itself
        '''
        statement = message.content[len('$say '):]
        await message.delete()
        await message.channel.send(statement)


    async def quote(self, message):
        arg = message.content[7:]

        if arg: # Find quotes based on specific author, key required, specific wording required
            endpoint = f'https://zenquotes.io/api/quotes/author/{arg}'
        else: # Find quotes based on random authors
            endpoint = 'https://zenquotes.io/api/random'
        
        response = requests.get(endpoint)
        json_data = json.loads(response.text)
        quote = json_data[0]['q']
        author = json_data[0]['a']

        print(arg) # debug
        reply = f'{author} - {quote}'

        await message.channel.send(reply)

    
    async def assign_role(self, message):
        '''
        Assigns a role to the user based on the role name provided in the message.
        Usage: $role <role_name>
        '''
        role_name = message.content[len('$role '):].strip()
        server = message.guild
        role = discord.utils.get(server.roles, name=role_name)

        if role:
            try:
                await message.author.add_roles(role)
                reply = f"Role '{role_name}' has been assigned to you, {message.author.mention}."
            except discord.Forbidden:
                reply = "I'm sorry but I don't have permission to manage roles."
            except discord.HTTPException as e:
                reply = f"An error occurred: {e}"
        else:
            reply = f"Role '{role_name}' not found. Please ensure the role name is correct."

        await message.channel.send(reply)


    async def update_banned_word_list(self, message):
        '''
        Takes a sentence input and updates the banned word list to include all words in that
        sentence.
        '''
        words = message.content.split()[1:]

        self.banned_words = words
        reply = f'Banned words/phrases have been updated to: "'

        for word in self.banned_words:
            reply += word + ', '
        
        reply.rstrip(',')
        reply += '"'

        await message.channel.send(reply)
    

    async def check_banned_words(self, message):
        '''
        Gives banned word/phrases list
        '''
        reply = f'Banned words/phrases for this server currently include: "'

        for word in self.banned_words:
            reply += word + ', '
        
        reply.rstrip(',')
        reply += '"'

        await message.channel.send(reply)


    async def weather(self, message):
        '''
        Provides the current weather for the given city
        Usage: $weather <city>
        '''
        city = message.content[len('$weather '):].strip()
        api_key = '8a108c1df19759273302c810a265985f'
        endpoint = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        
        response = requests.get(endpoint)
        json_data = response.json()
        
        if json_data['cod'] != 200:
            await message.channel.send(f"Failed to get weather data for {city}. Check that you inputted a valid city name.")
            return
        
        weather_description = json_data['weather'][0]['description']
        temp = json_data['main']['temp']
        reply = f"Weather in {city}:\n{weather_description.capitalize()}\nTemperature: {temp}°C"
        await message.channel.send(reply)


    async def clear(self, message):
        '''
        Clears the current channel of all messages, or input an int to clear that number 
        '''
        if not message.author.guild_permissions.manage_messages:
            await message.channel.send("I'm sorry but I don't have permission to clear messages.")
            return

        try:
            num_messages = int(message.content[len('$clear '):].strip())

            if num_messages:
                deleted = await message.channel.purge(limit=num_messages + 1)  # +1 to include the $clear command message
            else:
                deleted = await message.channel.purge(limit=101)
            
            await message.channel.send(f"Deleted {len(deleted)-1} messages.", delete_after=5) # Delete this message too after 5 sec

        except ValueError:
            await message.channel.send("Invalid number of messages to be deleted inputted")
        except discord.Forbidden:
            await message.channel.send("I'm sorry but I don't have permission to manage messages.")
        except discord.HTTPException as e:
            await message.channel.send(f"An error occurred: {e}")


    async def chatgpt(self, message):
        '''
        Uses ChatGPT's OpenAI to take user's message as a prompt, 
        then bot replies with ChatGPT's response
        '''
        prompt = message.content[len('$chatgpt '):]

        api_key = os.getenv('OPENAI_API_KEY')
        openai.default_headers = {"x-foo": "true"}
        openai.api_key = api_key

        # From Documentation
        try:
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
            chatgpt_response = completion.choices[0].message.content
        except openai.RateLimitError:
            chatgpt_response = "I'm sorry, but your rate limit for ChatGPT's API has been exceeded"

        await message.channel.send(chatgpt_response)