### Setup logger
import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import sys, configparser, traceback
import asyncio, discord
from actions.action_list import ActionList
from actions.help import Help



# Read context from input argument
if len(sys.argv) < 2:
    print("Use:\t{} context".format(sys.argv[0]))
    exit(1)

# Global variables
CONTEXT = sys.argv[1]
COMMON = "COMMON"
CONFIG_PATH = "ressources/config.ini"

# Read config file
try:
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    prefix_command = config[COMMON]["prefix_command"]

    TOKEN = config[CONTEXT]["token"]
    allowed_channels = []
    allowed_channels.append(int(config[CONTEXT]["target_channel"]))
    allowed_channels.append(int(config[CONTEXT]["private_channel"]))
    error_channel = int(config[CONTEXT]["error_channel"])
except:
    logger.error("Cannot read properly config file.")
    raise


client = discord.Client()

ActionList.add_action(Help)


def action_called(action, message_content):
    first_word = message_content.split()[0]
    full = first_word == action.command()
    short = first_word == action.command_short()
    return full or short


async def parse_command(message):
    if message.content[0] != prefix_command:
        return
    logger.debug("Command prefix detected : %s", message.content)
    for action in ActionList.actions:
        if action_called(action, message.content[1:]):
            logger.debug("Command detected.")
            await action.on_call(message, client)


async def displayMessage(message):
    message_content = message.content
    isPrivateMessage = message.guild is None
    if isPrivateMessage:
        logger.debug("In private message.")
        serverNameOrPrivate = "PRIVATE"
        channelName = ""
        authorName = message.author.name
    else:
        logger.debug("In server : %s", message.guild)
        serverNameOrPrivate = message.guild.name
        channelName = message.channel.name
        authorHasNickname = message.author.nick is not None
        authorName = message.author.nick if authorHasNickname else message.author.name
    logger.info("(%s) [%s] %s : %s", serverNameOrPrivate, channelName, authorName, message_content)


@client.event
async def on_raw_reaction_add(payload):
    logger.debug("Reaction %s detected.", payload.emoji)


@client.event
async def on_message(message):
    try:
        if message.channel.id not in allowed_channels:
            return
        await displayMessage(message)
        if message.author == client.user:
            return

        logger.debug("Message %s to parse is :\"%s\"", message.id, message.content)
        await parse_command(message)

    except Exception as e:
        msg = traceback.format_exc()
        logger.error(msg)
        channel = client.get_channel(error_channel)
        await channel.send(msg)


@client.event
async def on_ready():
    logger.debug("%s connected.", client.user.name)
    helpMessage = discord.Game(prefix_command + "help for help")
    await client.change_presence(activity=helpMessage)


"""
@client.event
async def on_error(event, *args, **kwargs):
    channel = client.get_channel(error_channel)
    try:
        await channel.send("Error in method *"+ str(event) + "* on message : `" + str(args[0]) + "`.")
    except:
        await channel.send("Error in %s.", event)
"""


try:
    client.run(TOKEN)
except KeyboardInterrupt:
    pass
