
import requests
import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import json

load_dotenv()

echoToken = os.environ['ECHO_TOKEN']
headers = {
    'Authorization': echoToken,
}

def gen_echo():
    response = requests.get('https://api.echo.ac/v1/user/pin', headers=headers).json()
    return response['links']['dayz']

def get_scan(pin,ScanNumber):
    try:
        uuid = requests.get(f'https://api.echo.ac/v1/scan/{pin}', headers=headers).json()[ScanNumber]['uuid']
        response = requests.get(f'https://api.echo.ac/v1/scan/{uuid}', headers=headers).json()
        for item in response:
            print(item)
        return response
    except Exception as e:
        print(type(e))
        return e

whatIsEchoMessage = """What is Echo?
Echo is a security tool we use to help verify the integrity of a player’s setup during specific checks or investigations. It’s not an in-game monitoring system — it's used externally by our team when needed.

How does it work?
With player consent, Echo allows us to run a PC check that helps identify potential cheats, third-party tools, or configurations that break our server rules. It’s only used when there's a valid reason, such as a report or suspicious activity, and it’s never active without your knowledge or permission.

What does it do?

Scans for known cheat software or tools that violate server rules,
Helps validate the fairness of gameplay when questions arise,
Gives admins insight during investigations to make accurate decisions,

Why do we use it?
We use Echo to maintain a fair and competitive environment. It helps us avoid false bans and makes sure we're enforcing rules based on real evidence, not just player reports.

Player Rights & Transparency
Echo is only used with your consent and for legitimate checks. You always have the right to decline, though refusal may affect the outcome of an investigation. If you ever feel something was done unfairly, you're welcome to submit a ticket and ask for a review by our lead team."""


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        try:
            syncedCommands = await tree.sync(guild=guild)
            print(f'{len(syncedCommands)} commands synced successfully to {guild.id}!')
        except Exception as e:
            print(f'Command sync failed: {e}')

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)
guildId = os.environ['GUILD_ID']
guild=discord.Object(id=guildId)

@tree.command(name="echo", description="Generates an echo link", guild=guild)
async def gen_echo_link_command(interaction):
    echoLink = gen_echo()
    await interaction.response.send_message(f'{whatIsEchoMessage}\n\nPlease download and run this scan then post the does here.\nDownload link: {echoLink}')

@tree.command(name="scan", description="Gets the link for a scan done by given pin", guild=guild)
async def get_scan_command(interaction: discord.Interaction, pin: str, scan_number: int = -1):
    scanResults = get_scan(pin, scan_number)
    try:
        await interaction.response.send_message(f'Scan results: {scanResults["detection"]}\nhttps://beta.dash.echo.ac/scan/{scanResults["uuid"]}')
    except Exception as e:
        await interaction.response.send_message(f'Unexpected error: {e}')

@tree.command(name="details", description="Gets a json file containing the details of a scan byy given pin", guild=guild)
async def get_scan_details_command(interaction: discord.Interaction, pin: str, scan_number: int = -1):
    scanResults = get_scan(pin, scan_number)
    with open(f'scan_{pin}_{scan_number}.json', 'w') as outfile:
        json.dump(scanResults, outfile)
    try:
        await interaction.response.send_message(file=discord.File(f'scan_{pin}_{scan_number}.json'))
    except Exception as e:
        await interaction.response.send_message(f'Unexpected error: {e}')
    if os.path.exists(f'scan_{pin}_{scan_number}.json'):
        os.remove(f'scan_{pin}_{scan_number}.json')

token = os.environ['DISCORD_TOKEN']
client.run(token)