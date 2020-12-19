import logging
logger = logging.getLogger(__name__)

import discord
import utils.Tools as Tools


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
        if message is not None:
            await message.edit(content=self.message.content + '\n' + sub_message)
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
            self.message = None
        else:
            player_id = await self.get_player_id(player, player_id)
            self.DM_players[player_id]["message"] = None

    def is_tracked(self, message_id):
        if self.message.id == message_id:
            return True
        for dm_obj in self.DM_players.values():
            message = dm_obj["message"]
            if message is not None and message.id == message_id:
                return True
        return False

    def in_guild(self):
        """
        Return True if main channel of game is in a guild.
        """
        return type(self.channel) == discord.TextChannel


    ## Getters

    def get_player(self, player_id):
        if player_id in self.DM_players:
            return self.DM_players[player_id]["player"]
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
                player = await self.client.fetch_user(player_id)
            channel = player.dm_channel
            if channel is None:
                channel = await player.create_dm()
                logger.log(Tools.VERBOSE, "Need to create dm {}".format(repr(channel)))
            self.DM_players[player_id] = {"player": player, "channel": channel, "message": None}
        return player_id

    async def get_message(self, player=None, player_id=None):
        """
        Return message wether from main channel or private one.
        Declare player if from private channel (if needed).
        """
        if player is None and player_id is None:
            message = self.message
        else:
            player_id = await self.get_player_id(player, player_id)
            message = self.DM_players[player_id]["message"]
        return message
