import discord
from discord.ext import commands

client = discord.Client()

@client.event
async def on_ready():
    print('BenBot is ready {0.user}'.format(client))

client.run("TOKEN")


@client.event
async def on_message(message):
    if message.author == client.user:
        return