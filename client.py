import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

token = open('token_DO-NOT-SUBMIT').read().strip()
bot.run(token)
