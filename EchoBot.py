#TODO
#Add error handling for gen_echo() [DONE]
#Rework error handling and returns for get_scan() [DONE]
#Check if file can't be sent in get_scan_details_command() and if it can't, retry
#input sanitization
#/details crashes if scan_number is out of index range, not caught by try expect [DONE]
#figure out something like a locales file to get rid of all the text in the code
#standardize naming convention
#add option to make bot response private (interaction.response.send_message(chatMessage, ephemeral=True))
import requests
import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import json

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

load_dotenv()

echoToken = os.environ['ECHO_TOKEN']
headers = {
    'Authorization': echoToken,
}

def gen_echo():
    retMessage = ""
    try:
        rawResponse = requests.get('https://api.echo.ac/v1/user/pin', headers=headers)
        respCode = rawResponse.status_code
        response = rawResponse.json()
        match respCode:
            case 200:
                retMessage = response['links']['dayz']
            case 401:
                retMessage = response['message']
            case 403:
                retMessage = response['message']
            case 429:
                retMessage = response['message']
                retMessage += f'\nMore requests can be sent in <t:{response["resetAt"]}:R>'
    except Exception as e:
        retMessage = f'Unexpected error: {e}'
    return retMessage

def get_scan(pin,ScanNumber):
    retMessage = ""
    scanFound = False
    try:
        rawResponse = requests.get(f'https://api.echo.ac/v1/scan/{pin}', headers=headers)
        respCode = rawResponse.status_code
        response = rawResponse
        match respCode:
            case 200:
                response = rawResponse.json() #find way to move out of case, crashes with response 204 if outside
                uuid = response[ScanNumber]['uuid']
                retMessage = requests.get(f'https://api.echo.ac/v1/scan/{uuid}', headers=headers).json()
                scanFound = True
            case 204:
                retMessage = f'Scan with PIN: {pin} not found'
            case 403:
                response = rawResponse.json() #find way to move out of case, crashes with response 204 if outside
                retMessage = response['message']
            case 429:
                response = rawResponse.json() #find way to move out of case, crashes with response 204 if outside
                retMessage = response['message']
                retMessage += f'\nMore requests can be sent in <t:{response["resetAt"]}:R>'
    except Exception as e:
        retMessage = f'Unexpected error: {e}'
        if type(e).__name__ == 'IndexError' : retMessage = f'Scan with PIN: {pin} not found at inxed {ScanNumber}'
    return retMessage, scanFound
    
def command_details(command):
    chatMessage = ""
    try:
        commandDetails = tree.get_command(command, guild=guild)
        chatMessage = f'/**{commandDetails.name}**\n{commandDetails.description}\n'
        commandParams = commandDetails._params
        if commandParams: #Will return true if there are commad parameters
            chatMessage += "\nCommand parameters:\n"
            for key in commandParams:
                chatMessage += f'{commandParams[key].name}\n\t'
                chatMessage += f'-{commandParams[key].description}\n'
                if not(commandParams[key].required):
                    chatMessage += "\t-*Optional*\n"
                    chatMessage += f'\t-Default: *{commandParams[key].default}*\n'
    except:
        chatMessage = f'Command {command} Not Found'
    return chatMessage

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
@app_commands.describe(info_message = "Should the echo info message be displayed")
async def gen_echo_link_command(interaction: discord.Interaction, info_message: bool = True):
    echoLink = gen_echo()
    #echoLink = "https://test.link/DoNotWantToSpamAPI"
    chatMessage = f'{whatIsEchoMessage}Please download and run this scan then post the pin here.\nDownload link: {echoLink}'
    if not(info_message):
        chatMessage = f'Please download and run this scan then post the pin here.\nDownload link: {echoLink}'
    await interaction.response.send_message(chatMessage)

@tree.command(name="scan", description="Gets the link for a scan done by given pin", guild=guild)
@app_commands.describe(pin = "PIN for the scan", scan_number = "Use to access specific scan done with PIN")
async def get_scan_command(interaction: discord.Interaction, pin: str, scan_number: int = -1):
    chatMessage = ""
    scanResults, scanFound = get_scan(pin, scan_number)
    if scanFound:
        try:
            chatMessage = f'Scan results: {scanResults["detection"]}\nhttps://beta.dash.echo.ac/scan/{scanResults["uuid"]}'
        except Exception as e:
            chatMessage = f'Unexpected error: {e}'
    else:
        chatMessage =  scanResults
    await interaction.response.send_message(chatMessage)

@tree.command(name="details", description="Gets a json file containing the details of a scan by given pin", guild=guild)
@app_commands.describe(pin = "PIN for the scan", scan_number = "Use to access specific scan done with PIN")
async def get_scan_details_command(interaction: discord.Interaction, pin: str, scan_number: int = -1):
    scanResults, scanFound = get_scan(pin, scan_number)
    if scanFound:
        fileName = f'scan_{pin}_{scan_number}.json'
        try:
            with open(fileName, 'w') as outfile:
                json.dump(scanResults, outfile)
            await interaction.response.send_message(file=discord.File(fileName))  #Check for failure to send, also find a way to standradize response like get_scan_command()
        except Exception as e:
            await interaction.response.send_message(f'Unexpected error: {e}')
        if os.path.exists(fileName):
            os.remove(fileName)
    else:
        await interaction.response.send_message(scanResults)

@tree.command(name="help", description="Get a list of commands or help details for a specific command", guild=guild)
@app_commands.describe(command = "Specific command to get extra info about")
async def help_command(interaction: discord.Interaction, command: str = None):
    try:
        chatMessage = "For more detials about a command use */help **command***\n"
        if command:
            chatMessage = command_details(command)
        else:
            for commandDetails in tree.get_commands(guild=guild):
                chatMessage += f'/{commandDetails.name}\n'
    except Exception as e:
        chatMessage = f'Unexpected error: {e}'
    await interaction.response.send_message(chatMessage)

token = os.environ['DISCORD_TOKEN']
client.run(token)