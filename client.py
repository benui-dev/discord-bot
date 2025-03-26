import discord
import yaml
import requests
from discord import app_commands
from discord.ext import commands

# GitHub raw URLs for the YAML files
UPROP_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uproperty.yml"
UCLASS_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uclass.yml"
UENUM_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uenum.yml"
UFUNC_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/ufunction.yml"
MY_LINK = "https://github.com/benui-dev/discord-bot"

# Store the YAML data for each specifier
yaml_data = {
    'uproperty': None,
    'uclass': None,
    'uenum': None,
    'ufunc': None
}


def fetch_yaml_from_github(url):
    """Fetches and loads YAML data from the GitHub raw file."""
    response = requests.get(url)

    if response.status_code == 200:
        try:
            yaml_content = yaml.safe_load(response.text)
            if isinstance(yaml_content, dict) and 'specifiers' in yaml_content:
                specifiers = yaml_content['specifiers']
                if isinstance(specifiers, list) and all(isinstance(item, dict) for item in specifiers):
                    return specifiers
                else:
                    print("Unexpected 'specifiers' format. Ensure it's a list of dictionaries.")
            else:
                print("YAML structure is missing the 'specifiers' key.")
        except yaml.YAMLError as e:
            print(f"YAML Parsing Error: {e}")
    else:
        print(f"Failed to fetch YAML file. Status Code: {response.status_code}")

    return None


def create_embed(name, entry):
    """Create the embed message for displaying the property specifier details."""
    embed = discord.Embed(title=f"**Specifier: {name}**", color=discord.Color(0x3498db))

    # Description
    embed.add_field(name="**Description**", value=f"{entry.get('comment', 'No comment available.')}", inline=False)

    # Examples in a code block
    examples = "\n".join(entry.get("samples", [])) if entry.get("samples") else "*No examples available.*"
    embed.add_field(name="**Examples**", value=f"```cpp\n{examples}\n```", inline=False)

    # Incompatible With list as a code block
    incompatible = entry.get("incompatible", [])
    value = "```\n" + "\n".join([f"{item}" for item in incompatible]) + "\n```" if incompatible else "*None*"
    embed.add_field(name="**Incompatible With**", value=value, inline=False)

    # Documentation Link
    documentation_link = entry.get("documentation", {}).get("source", "No source available.")
    embed.add_field(name="**Documentation Link**", value=f"[Click here for more info]({documentation_link})", inline=False)

    return embed


# Create a bot instance with intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Preload YAML data from GitHub
yaml_data['uproperty'] = fetch_yaml_from_github(UPROP_GITHUB_URL)
yaml_data['uclass'] = fetch_yaml_from_github(UCLASS_GITHUB_URL)
yaml_data['uenum'] = fetch_yaml_from_github(UENUM_GITHUB_URL)
yaml_data['ufunc'] = fetch_yaml_from_github(UFUNC_GITHUB_URL)

# Check if the data was successfully loaded
if all(yaml_data.values()):
    print("BenUI Github YAML files loaded successfully.")
else:
    print("Failed to load some YAML files from Github.")

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


async def fetch_and_display(ctx, specifier_key, name):
    """Fetch YAML data and display in the embed message based on specifier_key."""
    data = yaml_data.get(specifier_key)

    if not data:
        return False  # Fail silently, just return False if no data

    # Search for the entry with the requested 'name'
    for entry in data:
        if entry.get("name") == name:
            embed = create_embed(name, entry)
            await ctx.send(embed=embed)
            return True  # Successfully found the specifier

    return False  # Specifier not found



@bot.hybrid_command()
async def benbot(ctx):
    value = f"[Github]({MY_LINK})"
    await ctx.author.send(f"Hello! I'm open source! Please feel free to submit an issue or a PR :) {value}")



@bot.hybrid_command()
async def specifier(ctx, name: str):
    """Search across all specifier YAML files."""
    found = False  # Flag to track if the specifier was found

    for key in yaml_data:
        if await fetch_and_display(ctx, key, name):
            found = True  # Specifier found, set the flag to True
            break  # Stop searching after finding the specifier

    # If no specifier was found after searching all files, send a "not found" message
    if not found:
        await ctx.send(f"Specifier `{name}` not found in any of the specifier files.")


@bot.hybrid_command()
async def uprop(ctx, name: str):
    """Search for a property in the UPROPERTY YAML file."""
    found = await fetch_and_display(ctx, 'uproperty', name)
    if not found:
        await ctx.send(f"Property Specifier`{name}` not found.")


@bot.hybrid_command()
async def uclass(ctx, name: str):
    """Search for a class in the UCLASS YAML file."""
    found = await fetch_and_display(ctx, 'uclass', name)
    if not found:
        await ctx.send(f"Class Specifier`{name}` not found.")


@bot.hybrid_command()
async def uenum(ctx, name: str):
    """Search for an enum in the UENUM YAML file."""
    found = await fetch_and_display(ctx, 'uenum', name)
    if not found:
        await ctx.send(f"Enum Specifier`{name}` not found.")


@bot.hybrid_command()
async def ufunc(ctx, name: str):
    """Search for a function in the UFUNC YAML file."""
    found = await fetch_and_display(ctx, 'ufunc', name)
    if not found:
        await ctx.send(f"Function Specifier`{name}` not found.")


# Run the bot
token = open("token_DO-NOT-SUBMIT").read().strip()
bot.run(token)
