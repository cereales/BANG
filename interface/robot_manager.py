import logging
logger = logging.getLogger(__name__)

import traceback
import utils.Tools as Tools


class RobotManager:
    robots_by_channels = dict()
    aliases_channel = dict()

    ## Manage Robots

    @staticmethod
    def add_robot(robot, channel_id):
        if not channel_id in RobotManager.robots_by_channels:
            RobotManager.robots_by_channels[channel_id] = []
        RobotManager.robots_by_channels[channel_id].append(robot)

    @staticmethod
    def declare_minor_channel(major_channel_id, minor_channel_id):
        if major_channel_id in RobotManager.robots_by_channels:
            if minor_channel_id not in RobotManager.aliases_channel:
                RobotManager.aliases_channel[minor_channel_id] = []
            RobotManager.aliases_channel[minor_channel_id].append(major_channel_id)


    ## Forward events to Robots

    @staticmethod
    async def on_raw_reaction_add(payload):
        channel_id = payload.channel_id
        if channel_id in RobotManager.aliases_channel:
            channel_ids = RobotManager.aliases_channel[channel_id]
        else:
            channel_ids = [channel_id]
        for channel_id in channel_ids:
            if channel_id in RobotManager.robots_by_channels:
                for robot in RobotManager.robots_by_channels[channel_id]:
                    try:
                        logger.debug("Forward to robot {}".format(robot))
                        await robot.on_raw_reaction_add(payload)
                    except AttributeError: # Could not implement method
                        logger.warning("Methode could not be implemented.")
                        msg = traceback.format_exc()
                        logger.error(msg)
            else:
                logger.log(Tools.VERBOSE, RobotManager.robots_by_channels)
                logger.log(Tools.VERBOSE, RobotManager.aliases_channel)
                logger.log(Tools.VERBOSE, "No robot concerning {}.".format(payload.channel_id))
