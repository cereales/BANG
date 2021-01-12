import logging
logger = logging.getLogger(__name__)

import discord
from interface.robot_manager import RobotManager
import utils.Tools as Tools
from utils.Emoji import Emoji


class Robot:
    """
    Provides specific discord oriented tools to interact with discord users.
    """
    def __init__(self, client, channel):
        self.client = client # bot account, virtual identity
        self.channel = channel # place of the game instance
        self.message = None # previous message from bot in main channel
        self.DM_players = dict() # message and channel for players ids


    ## Messages manager

    async def send(self, message_content, player=None, player_id=None):
        """
        Send a new message and return it.
        Default to main channel, unless player is given.
        If player object is not available, give player_id.
        """
        if player is None and player_id is None:
            # Send to main channel
            self.message = await self.channel.send(message_content)
            message = self.message
        else:
            player_id = await self.get_player_id(player, player_id)
            if self.is_robot(player_id):
                return None
            channel = self.DM_players[player_id]["channel"]
            self.DM_players[player_id]["message"] = await channel.send(message_content)
            message = self.DM_players[player_id]["message"]
        return message

    async def refresh(self, message_content, player=None, player_id=None):
        """
        Change previous sent message with new content, and return it.
        Default to main channel, unless player is given.
        If player object is not available, give player_id.
        """
        message = await self.get_message(player, player_id)
        logger.debug("Edit message.")
        if message is not None:
            await message.edit(content=message_content)
        else:
            message = await self.send(message_content, player, player_id)
        return message

    async def add(self, sub_message, player=None, player_id=None):
        """
        Add content to existing message, keeping old part, and return it.
        Default to main channel, unless player is given.
        If player object is not available, give player_id.
        """
        message = await self.get_message(player, player_id)
        logger.debug("Add a line to message.")
        if message is not None:
            await message.edit(content=message.content + '\n' + sub_message)
        else:
            message = await self.send(sub_message, player, player_id)
        return message

    async def forget(self, player=None, player_id=None):
        """
        Cut out link to sent message.
        Default to main channel, unless player is given.
        If player object is not available, give player_id.
        """
        if player is None and player_id is None:
            logger.log(Tools.VERBOSE, "Set main message as untracked.")
            self.message = None
        else:
            player_id = await self.get_player_id(player, player_id)
            logger.log(Tools.VERBOSE, "Set private message as untracked. (player_id={})".format(player_id))
            if not self.is_robot(player_id):
                self.DM_players[player_id]["message"] = None

    def is_tracked(self, message_id):
        if self.message is not None and self.message.id == message_id:
            return True
        for dm_obj in self.DM_players.values():
            if not dm_obj["ia"]:
                message = dm_obj["message"]
                if message is not None and message.id == message_id:
                    return True
        logger.warning("Message is not tracked.")
        return False

    def in_guild(self):
        """
        Return True if main channel of game is in a guild.
        """
        return type(self.channel) == discord.TextChannel

    async def clear_reactions(self):
        if self.in_guild() and self.message is not None:
            await self.message.clear_reactions()


    ## Getters

    def get_player(self, player_id):
        if player_id in self.DM_players:
            return self.DM_players[player_id]["player"]
        logger.error("Undeclared player {}.".format(player_id))
        return None


    ## utils

    async def get_player_id(self, player=None, player_id=None):
        """
        Declare player informations if needed.
        Return player identification.
        Only one of the two parameters can be given.
        """
        if player is None and player_id is None:
            raise AttributeError("Need a player to declare.")
        if player is not None:
            if player_id is not None:
                raise AttributeError("Cannot give player AND player_id parameters together.")
            player_id = player.id

        if player_id not in self.DM_players:
            # Need DM channel
            if player is None:
                # Need player object
                if self.in_guild():
                    player = await self.channel.guild.fetch_member(player_id)
                else:
                    player = await self.client.fetch_user(player_id)
            channel = player.dm_channel
            if channel is None:
                channel = await player.create_dm()
                logger.log(Tools.VERBOSE, "Need to create dm {}".format(repr(channel)))
            logger.debug("Declare player {}".format(player_id))
            logger.log(Tools.VERBOSE, "Player object of type {}".format(type(player)))
            self.DM_players[player_id] = {"player": player, "channel": channel, "message": None, "ia": False}
            RobotManager.declare_minor_channel(self.channel.id, channel.id)
        return player_id

    def declare_robot(self, player_id, ia):
        """
        Declare robot if needed.
        Return robot identification.
        """
        if player_id not in self.DM_players:
            logger.debug("Declare robot {}".format(player_id))
            self.DM_players[player_id] = {"ia": True, "player": ia}
        else:
            logger.warning("Cannot declare robot {} because id is already used.".format(player_id))

    def is_robot(self, player_id):
        if player_id in self.DM_players:
            return self.DM_players[player_id]["ia"]
        logger.error("Undeclared robot {}.".format(player_id))
        return None

    async def get_message(self, player=None, player_id=None):
        """
        Return message wether from main channel or private one.
        Declare player if from private channel (if needed).
        """
        if player is None and player_id is None:
            logger.debug("Get main message.")
            message = self.message
        else:
            logger.debug("Get private message.")
            player_id = await self.get_player_id(player, player_id)
            if self.is_robot(player_id):
                message = None
            else:
                message = self.DM_players[player_id]["message"]
        if message is None:
            logger.debug("Found message None.")
        return message

    def emoji_on_message(self, emoji_registered_name, payload, message):
        """
        Return True if reaction has been received on expected message with the expected emoji.
        Message must be provided, wheter it is from main channel or private one.
        In other words, check that emoji is the expected one and reaction was added on main message or the private message in sender channel.
        """
        return Emoji.equals(emoji_registered_name, payload.emoji.name) and message is not None and payload.message_id == message.id
