import logging
logger = logging.getLogger(__name__)

import traceback
from interface.robot import Robot


class RobotManager:
    robots_by_channels = dict()

    ## Manage Robots

    @staticmethod
    def add_robot(robot, channel_id):
        if not channel_id in RobotManager.robots_by_channels:
            RobotManager.robots_by_channels[channel_id] = []
        RobotManager.robots_by_channels[channel_id].append(robot)


    ## Forward events to Robots

    @staticmethod
    async def on_raw_reaction_add(payload):
        channel_id = payload.channel_id
        if channel_id in RobotManager.robots_by_channels:
            for robot in RobotManager.robots_by_channels[channel_id]:
                try:
                    await robot.on_raw_reaction_add(payload)
                except AttributeError: # Could not implement method
                    logger.warning("Methode could not be implemented.")
                    msg = traceback.format_exc()
                    logger.error(msg)
