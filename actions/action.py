from abc import ABC, abstractmethod


import logging
logger = logging.getLogger(__name__)
##logger.setLevel(logging.DEBUG)


class AbstractAction(ABC):
    def __init__(self):
        super().__init__()

    @staticmethod
    @property
    @abstractmethod
    def command():
        """
        Command to invoke action
        :return: string that needs to be written to call action
        """
        pass

    @staticmethod
    @property
    @abstractmethod
    def command_short():
        """
        Short command to invoke action
        :return: short string that needs to be written to call action
        """
        pass

    @staticmethod
    @property
    @abstractmethod
    def help_description():
        """
        Command description that is written when calling help
        :return: string description
        """
        pass

    @staticmethod
    @property
    @abstractmethod
    def help_args():
        """
        Arguments that the command can take for display when calling !help
        :return: List of strings representing the different argument possibilities.
                 No argument is represented by a list with an empty string
        """
        pass

    @staticmethod
    @abstractmethod
    async def on_call(message, client):
        """
        Method called when action is called using command or command_short
        :param message: Message that called the action
        :param client: Discord client object
        :return: No return value is expected
        """
        pass

