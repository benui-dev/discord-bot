import discord
from discord.ext import commands
from discord import app_commands
import yaml
import requests

# GitHub raw URLs for the YAML files
UPROP_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uproperty.yml"
UCLASS_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uclass.yml"
UENUM_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/uenum.yml"
UFUNC_GITHUB_URL = "https://raw.githubusercontent.com/benui-dev/UE-Specifier-Docs/main/yaml/ufunction.yml"

# Store the YAML data for each specifier
yaml_data = {
    'uproperty': None,
    'uclass': None,
    'uenum': None,
    'ufunc': None
}

# Fetch YAML data function as before

def fetch_yaml_from_github(url):
    """Fetches and loads YAML data from the GitHub raw file."""
    response = requests.get(url)
    if response.status_code == 200:
        try:
            yaml_content = yaml.safe_load(response.text)
            if isinstance(yaml_content, dict) and 'specifiers' in yaml_content:
                return yaml_content['specifiers']
        except yaml.YAMLError as e:
            print(f"YAML Parsing Error: {e}")
    return []

# Preload YAML data from GitHub
yaml_data['uproperty'] = fetch_yaml_from_github(UPROP_GITHUB_URL)
yaml_data['uclass'] = fetch_yaml_from_github(UCLASS_GITHUB_URL)
yaml_data['uenum'] = fetch_yaml_from_github(UENUM_GITHUB_URL)
yaml_data['ufunc'] = fetch_yaml_from_github(UFUNC_GITHUB_URL)

# Create a bot instance with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Auto-complete function
async def specifier_autocomplete(interaction: discord.Interaction, current: str):
    """Autocomplete specifier names for slash commands."""
    specifiers = set()  # Use a set to avoid duplicates
    for key in yaml_data:
        for entry in yaml_data[key]:
            if entry.get("name").lower().startswith(current.lower()):
                specifiers.add(entry.get("name"))
    return [app_commands.Choice(name=name, value=name) for name in sorted(specifiers)]


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")

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


# Define slash commands
@bot.tree.command(name="specifier", description="Search across all specifier YAML files")
@app_commands.describe(name="The name of the specifier to search for")
@app_commands.autocomplete(name=specifier_autocomplete)
async def specifier(interaction: discord.Interaction, name: str):
    """Search across all specifier YAML files with auto-completion."""
    found = False  # Flag to track if the specifier was found
    for key in yaml_data:
        for entry in yaml_data[key]:
            if entry.get("name") == name:
                embed = create_embed(name, entry)
                await interaction.response.send_message(embed=embed)
                found = True
                break
        if found:
            break

    # If no specifier was found, send a "not found" message
    if not found:
        await interaction.response.send_message(f"Specifier `{name}` not found in any of the specifier files.")


@bot.tree.command(name="uprop", description="Search for a property in the UPROPERTY YAML file")
@app_commands.describe(name="The name of the property")
@app_commands.autocomplete(name=specifier_autocomplete)
async def uprop(interaction: discord.Interaction, name: str):
    """Search for a property in the UPROPERTY YAML file."""
    found = False
    for entry in yaml_data['uproperty']:
        if entry.get("name") == name:
            embed = create_embed(name, entry)
            await interaction.response.send_message(embed=embed)
            found = True
            break

    if not found:
        await interaction.response.send_message(f"Property Specifier `{name}` not found.")


@bot.tree.command(name="uclass", description="Search for a class in the UCLASS YAML file")
@app_commands.describe(name="The name of the class")
@app_commands.autocomplete(name=specifier_autocomplete)
async def uclass(interaction: discord.Interaction, name: str):
    """Search for a class in the UCLASS YAML file."""
    found = False
    for entry in yaml_data['uclass']:
        if entry.get("name") == name:
            embed = create_embed(name, entry)
            await interaction.response.send_message(embed=embed)
            found = True
            break

    if not found:
        await interaction.response.send_message(f"Class Specifier `{name}` not found.")


@bot.tree.command(name="uenum", description="Search for an enum in the UENUM YAML file")
@app_commands.describe(name="The name of the enum")
@app_commands.autocomplete(name=specifier_autocomplete)
async def uenum(interaction: discord.Interaction, name: str):
    """Search for an enum in the UENUM YAML file."""
    found = False
    for entry in yaml_data['uenum']:
        if entry.get("name") == name:
            embed = create_embed(name, entry)
            await interaction.response.send_message(embed=embed)
            found = True
            break

    if not found:
        await interaction.response.send_message(f"Enum Specifier `{name}` not found.")


@bot.tree.command(name="ufunc", description="Search for a function in the UFUNC YAML file")
@app_commands.describe(name="The name of the function")
@app_commands.autocomplete(name=specifier_autocomplete)
async def ufunc(interaction: discord.Interaction, name: str):
    """Search for a function in the UFUNC YAML file."""
    found = False
    for entry in yaml_data['ufunc']:
        if entry.get("name") == name:
            embed = create_embed(name, entry)
            await interaction.response.send_message(embed=embed)
            found = True
            break

    if not found:
        await interaction.response.send_message(f"Function Specifier `{name}` not found.")

# Run the bot
token = open("token_DO-NOT-SUBMIT").read().strip()
bot.run(token)
