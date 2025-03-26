import discord
import yaml
import requests
from discord.ext import commands

# GitHub raw URL for the YAML file
GITHUB_RAW_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uproperty.yml"

def fetch_yaml_from_github():
    """Fetches and loads YAML data from the GitHub raw file."""
    response = requests.get(GITHUB_RAW_URL)

    if response.status_code == 200:
        try:
            return yaml.safe_load(response.text)  # Load YAML content
        except yaml.YAMLError as e:
            print(f"YAML Parsing Error: {e}")
            return None
    else:
        print(f"Failed to fetch YAML file. Status Code: {response.status_code}")
        return None

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def prop(ctx, name: str):
    """Search for an entry with a matching 'name' field in the YAML file."""
    data = fetch_yaml_from_github()

    if not data:
        await ctx.send("Failed to fetch or parse YAML data.")
        return

    # Search for an entry with "name" matching the requested property
    for entry in data:
        if entry.get("name") == name:
            # Format and send the found entry
            formatted_entry = "\n".join([f"**{key}:** {value}" for key, value in entry.items()])
            await ctx.send(f"**Found Property: {name}**\n{formatted_entry}")
            return

    await ctx.send(f"Property `{name}` not found.")

# Run bot
token = open("token_DO-NOT-SUBMIT").read().strip()
bot.run(token)
