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
            yaml_content = yaml.safe_load(response.text)

            # Ensure the structure contains 'specifiers' as a list of dictionaries
            if isinstance(yaml_content, dict) and 'specifiers' in yaml_content:
                specifiers = yaml_content['specifiers']
                if isinstance(specifiers, list) and all(isinstance(item, dict) for item in specifiers):
                    return specifiers
                else:
                    print("Unexpected 'specifiers' format. Ensure it's a list of dictionaries.")
                    return None
            else:
                print("YAML structure is missing the 'specifiers' key or has unexpected format.")
                return None
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
    """Search for an entry with a matching 'name' field in the YAML file and display it in an embedded message."""
    data = fetch_yaml_from_github()

    if not data:
        await ctx.send("Failed to fetch or parse YAML data.")
        return

    # Search for an entry with "name" matching the requested property
    for entry in data:
        if entry.get("name") == name:
            # Create the embedded message with a customized color
            embed = discord.Embed(title=f"**UPROPERTY Specifier: {name}**", color=discord.Color(0x3498db))  # Blue color

            # Add Description field with a nice markdown style
            embed.add_field(
                name="**Description**",
                value=f"{entry.get('comment', 'No comment available.')}",
                inline=False
            )

            # Format the examples in a code block for better readability
            examples = "\n".join(entry.get("samples", [])) if entry.get("samples") else "*No examples available.*"
            embed.add_field(
                name="**Examples**",
                value=f"```cpp\n{examples}\n```",
                inline=False
            )

            # Add a highlighted field for "Incompatible With" using code block formatting
            incompatible = entry.get("incompatible", [])
            if incompatible:
                # Format the incompatible list as a single code block for better readability
                value = "```\n" + "\n".join([f"{item}" for item in incompatible]) + "\n```"
            else:
                value = "*None*"

            embed.add_field(
                name="**Incompatible With**",
                value=value,
                inline=False
            )

            # Add Documentation with a clean and informative markdown link
            documentation_link = entry.get("documentation", {}).get("source", "No source available.")
            embed.add_field(
                name="**Documentation Link**",
                value=f"[Click here for more info]({documentation_link})",
                inline=False
            )

            image = entry.get("image", {}).get("source", "No source available.")
            embed.add_field(
            name="**Image**",
                value=f"[Click here for more info]({image})",
                inline=False
            )

            # Send the embed to the channel
            await ctx.send(embed=embed)
            return

    await ctx.send(f"Property `{name}` not found.")

# Run bot
token = open("token_DO-NOT-SUBMIT").read().strip()
bot.run(token)
