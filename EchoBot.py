
import requests
import discord
from discord import app_commands
from dotenv import load_dotenv
import os

load_dotenv()

echoToken = os.environ['ECHO_TOKEN']
headers = {
    'Authorization': echoToken,
}

def gen_echo():
    response = requests.get('https://api.echo.ac/v1/user/pin', headers=headers).json()
    return response['links']['dayz']

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
async def first_command(interaction):
    echoLink = gen_echo()
    await interaction.response.send_message(whatIsEchoMessage + '\n\nPlease download and run this scan then post the does here.\nDownload link: ' + echoLink)

token = os.environ['DISCORD_TOKEN']
client.run(token)