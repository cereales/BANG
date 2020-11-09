from actions.action import AbstractAction
from actions.action_list import ActionList
import configparser


CONFIG_PATH = "ressources/config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
prefix_command = config["COMMON"]["prefix_command"]


class Help(AbstractAction):

    @staticmethod
    def command():
        return "help"

    @staticmethod
    def command_short():
        return "h"

    @staticmethod
    def help_description():
        return "Afficher cet ecran d'aide"

    @staticmethod
    def help_args():
        return [""]

    @staticmethod
    async def on_call(message, client):
        help_txt = "```"
        shorts = []
        fulls = []
        descriptions = []
        for action in ActionList.actions:
            shorts.append(prefix_command + action.command_short() if action.command_short() is not None else "")

            full = prefix_command + action.command()
            if len(action.help_args()) > 1:
                full += " ["
                for arg_possibility in action.help_args():
                    full += arg_possibility + ", "
                full = full[:-2] + "]"
            elif action.help_args()[0] != "":
                full += " " + action.help_args()[0]
            fulls.append(full)

            descriptions.append(action.help_description())

        longest_short = max(len(txt) for txt in shorts)
        longest_full = max(len(txt) for txt in fulls)
        for i in range(len(shorts)):
            help_txt += "{} | {} - {}\n".format(
                shorts[i] + ((longest_short - len(shorts[i])) * " "),
                fulls[i] + ((longest_full - len(fulls[i])) * " "),
                descriptions[i]
            )
        help_txt += "```"

        await message.channel.send(help_txt)

