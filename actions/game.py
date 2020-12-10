import logging
logger = logging.getLogger(__name__)

from actions.action import AbstractAction
from interface.robot_manager import RobotManager
from interface.game_robot import GameRobot


class Game(AbstractAction):

    @staticmethod
    def command():
        return "bang"

    @staticmethod
    def command_short():
        return None

    @staticmethod
    def help_description():
        return "Lance une partie de BANG!"

    @staticmethod
    def help_args():
        return [""]

    @staticmethod
    async def on_call(message, client):
        robot = GameRobot(client, message.channel)
        await robot.init()
        RobotManager.add_robot(robot, message.channel.id)
