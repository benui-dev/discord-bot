import discord
import yaml
import os
import requests
import random
from typing import List
from discord import app_commands
from discord.ext import commands

REQUIRED_ROLES = ["bot-team", "Mod"]  # Add any roles you need here


# GitHub raw URLs for the YAML files
UPROP_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uproperty.yml"
UCLASS_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uclass.yml"
UENUM_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uenum.yml"
UFUNC_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/ufunction.yml"
MY_LINK = "https://github.com/benui-dev/discord-bot"

JOKE_FILE_PATH = "dad_jokes.yaml"

# Store the YAML data for each specifier
yaml_data = {
    'uproperty': None,
    'uclass': None,
    'uenum': None,
    'ufunc': None
}

# Helper function to check if the user has a required role
def has_required_role(user):
    # Check if any role in the REQUIRED_ROLES list is assigned to the user
    return any(role.name in REQUIRED_ROLES for role in user.roles)

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
    description = entry.get('comment', 'No comment available.')
    if description:
        embed.add_field(name="**Description**", value=description, inline=False)

    # Examples in a code block
    examples = "\n".join(entry.get("samples", [])) if entry.get("samples") else "*No examples available.*"
    if examples and examples != "*No examples available.*":
        embed.add_field(name="**Examples**", value=f"```cpp\n{examples}\n```", inline=False)

    # Incompatible With list as a code block
    incompatible = entry.get("incompatible", [])
    if incompatible:
        value = "```\n" + "\n".join([f"{item}" for item in incompatible]) + "\n```"
        embed.add_field(name="**Incompatible With**", value=value, inline=False)
    else:
        embed.add_field(name="**Incompatible With**", value="*None*", inline=False)

    # Documentation Link
    documentation_link = entry.get("documentation", {}).get("source", "No source available.")
    if documentation_link and documentation_link != "No source available.":
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


@bot.command()
async def sync(ctx):
    print("Sync command")

    has_role = has_required_role(ctx.author)

    if not has_role:
        await ctx.send("You do not have the required role to run this command.")
        return

    await bot.tree.sync()
    await ctx.send("Synced")


@bot.hybrid_command()
async def benbot(ctx):
    value = f"[Github]({MY_LINK})"
    await ctx.author.send(f"Hello! I'm open source! Please feel free to submit an issue or a PR :) {value}")

# Autocomplete function for fetching specifier names
async def get_specifier_names(specifier_key):
    """Returns the list of specifier names from the YAML data."""
    data = yaml_data.get(specifier_key, [])
    return [entry['name'] for entry in data if 'name' in entry]


@bot.hybrid_command()
async def specifier(ctx, name: str):
    """Search across all specifier YAML files."""
    found = False  # Flag to track if the specifier was found

    for key in yaml_data:
        if await fetch_and_display(ctx, key, name):
            found = True  # Specifier found, set the flag to True
            break  # Stop searching after finding the specifier

    # If no specifier was found after searching all files.
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


# Function to load jokes from the YAML file
def load_jokes():
    if os.path.exists(JOKE_FILE_PATH):
        with open(JOKE_FILE_PATH, 'r') as file:
            return yaml.safe_load(file) or {}
    return {}

# Function to save jokes to the YAML file
def save_jokes(jokes):
    with open(JOKE_FILE_PATH, 'w') as file:
        yaml.dump(jokes, file, default_flow_style=False)


# Command to add a new dad joke
@bot.hybrid_command()
async def add_dad_joke(ctx, name: str, answer: str):
    jokes = load_jokes()

    has_role = has_required_role(ctx.author)

    if not has_role:
        await ctx.author.send("You do not have the required role to run this command.")
        return

    # Check if the joke already exists
    if name in jokes:
        await ctx.send(f"The joke '{name}' already exists!")
    else:
        jokes[name] = answer
        save_jokes(jokes)
        await ctx.send(f"New dad joke added! '{name}'")


# Command to fetch a dad joke by name or a random joke if no name is provided
@bot.hybrid_command()
async def dad_joke(ctx, name: str = ""):
    jokes = load_jokes()

    if name:  # If a name is provided, return the joke by name
        # Check if the joke exists
        if name in jokes:
            await ctx.send(f"**{name}:** {jokes[name]}")
        else:
            await ctx.send(f"Sorry, I don't have a joke by the name '{name}'.")
    else:  # If no name is provided, return a random joke
        if jokes:
            random_question, random_answer = random.choice(list(jokes.items()))
            await ctx.send(f"**{random_question}:** {random_answer}")
        else:
            await ctx.send("Sorry, I don't have any jokes stored.")


# Command to delete a dad joke by name
@bot.hybrid_command()
async def delete_dad_joke(ctx, name: str):
    jokes = load_jokes()

    has_role = has_required_role(ctx.author)

    if not has_role:
        await ctx.author.send("You do not have the required role to run this command.")
        return


    # Check if the joke exists
    if name in jokes:
        del jokes[name]
        save_jokes(jokes)
        await ctx.send(f"Joke '{name}' has been deleted.")
    else:
        await ctx.send(f"Sorry, I couldn't find a joke by the name '{name}' to delete.")

# Run the bot
token = open("token_DO-NOT-SUBMIT").read().strip()
bot.run(token)
