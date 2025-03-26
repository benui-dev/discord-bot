import discord
import yaml
import requests
from discord.ext import commands

# GitHub raw URLs for the YAML files
UPROP_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uproperty.yml"
UCLASS_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uclass.yml"
UENUM_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uenum.yml"
UFUNC_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/ufunction.yml"


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
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


async def fetch_and_display(ctx, url, name):
    """Fetch YAML data and display in the embed message."""
    data = fetch_yaml_from_github(url)

    if not data:
        await ctx.send("Failed to fetch or parse YAML data.")
        return

    # Search for the entry with the requested 'name'
    for entry in data:
        if entry.get("name") == name:
            embed = create_embed(name, entry)
            await ctx.send(embed=embed)
            return

    await ctx.send(f"Property `{name}` not found.")


@bot.command()
async def prop(ctx, name: str):
    """Search for a property in the UPROPERTY YAML file."""
    await fetch_and_display(ctx, UPROP_GITHUB_URL, name)


@bot.command()
async def uclass(ctx, name: str):
    """Search for a class in the UCLASS YAML file."""
    await fetch_and_display(ctx, UCLASS_GITHUB_URL, name)


@bot.command()
async def uenum(ctx, name: str):
    """Search for an enum in the UENUM YAML file."""
    await fetch_and_display(ctx, UENUM_GITHUB_URL, name)


@bot.command()
async def ufunc(ctx, name: str):
    """Search for a function in the UFUNC YAML file."""
    await fetch_and_display(ctx, UFUNC_GITHUB_URL, name)


# Run the bot
token = open("token_DO-NOT-SUBMIT").read().strip()
bot.run(token)
