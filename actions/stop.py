### Setup logger 
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import configparser
from actions.action import AbstractAction


admins = []
CONFIG_PATH = "ressources/config.ini"
config = configparser.ConfigParser(default_section='ADMINS')
config.read(CONFIG_PATH)
for admin in config["ADMINS"]:
    admins.append(int(admin))


    
class Stop(AbstractAction):

    @staticmethod
    def command():
        return "stop"

    @staticmethod
    def command_short():
        return None

    @staticmethod
    def help_description():
        return "Arreter le bot"

    @staticmethod
    def help_args():
        return ["*RESTREINT*"]

    @staticmethod
    async def on_call(message, client):
        trusted = message.author.id in admins
        if trusted and not client.is_closed():
            logger.debug("%s is trusted.", message.author.name)
            logger.info("Closing %s.", client.user.name)
            await client.close() # Doesnt work
