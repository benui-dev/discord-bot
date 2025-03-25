import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

intents = discord.Intents(messages=True)
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('BenBot is ready {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f'Message from {message.author}: {message.content}')

token = open('token_DO-NOT-SUBMIT').read()
client.run(token)
