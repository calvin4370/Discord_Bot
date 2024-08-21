import requests
from settings import version

class Sebas:
    def __init__(self, client):
        self.client = client

        # Bot commands (command_str: command_function)
        self.commands = {
            'version': self.version,
            'say': self.say,
        }

    async def run(self, command, message):
        if command in self.commands:
            await self.commands[command](message)

    async def version(self, message):
        reply = f'My current version is v{version}'
        await message.channel.send(reply)

    async def say(self, message):
        '''
        Deletes the user's command and says out their text as if it is the bot saying the message itself
        '''
        statement = message.content[len('$say '):]
        await message.channel.send(statement)

    async def quote(self, message):
        arg = message[7:]
        print(arg) # debug
        reply = arg
