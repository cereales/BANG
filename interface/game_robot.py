import logging, utils.Tools as Tools
logger = logging.getLogger(__name__)

import discord
from interface.robot import Robot


class State:
    CREATED = 0
    INITIALIZED = 1
    ABORTED = 2


class GameRobot(Robot):
    """
    Represents one instance of a UI for BANG! game.
    """
    def __init__(self, client, channel):
        super().__init__(client)
        self.state = State.CREATED
        self.channel = channel # place of the game instance
        self.message = None # previous message from bot
        self.players = dict() # discord id
        self.ordered_player_ids = []

    async def init(self):
        assert self.state == State.CREATED
        self.state = State.INITIALIZED
        await self.send_welcome_message()


    ## Utils

    async def get_user_from_payload(self, payload, channel=None):
        if channel is not None and type(channel) == discord.TextChannel:
            user = payload.member
        else:
            user = await self.client.fetch_user(payload.user_id)
        return user


    ## Events

    async def on_raw_reaction_add(self, payload):
        # TODO: catch asserts
        # ignore reactions added by me
        if payload.user_id == self.client.user.id:
            return
        # ignore reactions to others messages than the waiting one
        if payload.message_id != self.message.id:
            return
        assert self.channel.id == payload.channel_id # from the way robot is added

        logger.debug("Reaction {} {} detected by robot.".format(type(payload.emoji), payload.emoji))
        if self.state == State.INITIALIZED:
            # payload.emoji.name is not None because not in case of removing reaction of deleted emoji
            if payload.emoji.name == "\U0001f446":
                if payload.user_id not in self.players:
                    logger.debug("Player {} wants to join".format(payload.user_id))
                    player = await self.get_user_from_payload(payload, self.channel)
                    self.players[payload.user_id] = player
                    self.ordered_player_ids.append(payload.user_id)
                    await self.refresh_welcome_message()
            elif payload.emoji.name == "\U0001f6aa":
                if payload.user_id in self.players:
                    logger.debug("Player {} wants to leave".format(payload.user_id))
                    self.players.pop(payload.user_id)
                    self.ordered_player_ids.remove(payload.user_id)
                    await self.refresh_welcome_message()
            elif payload.emoji.name == "\u25b6\ufe0f":
                logger.debug("Start game")
            elif payload.emoji.name == "\U0001f6ab":
                logger.debug("Abort game")
                self.state = State.ABORTED
                player = await self.get_user_from_payload(payload, self.channel)
                await self.abort_message_request(player.display_name)
            else:
                logger.debug("Not the expected reaction")


    ## Messages

    async def send_welcome_message(self):
        self.message = await self.channel.send(Message.WELCOME)
        await self.message.add_reaction("\U0001f446") # TODO: use emoji manager
        await self.message.add_reaction("\U0001f6aa")
        await self.message.add_reaction("\u25b6\ufe0f")
        await self.message.add_reaction("\U0001f6ab")

    async def refresh_welcome_message(self):
        players_list = "\n".join(["{} {}".format(self.getEmoji(order), self.players[player_id].display_name) for order, player_id in enumerate(self.ordered_player_ids)])
        await self.message.edit(content=Message.WELCOME + "\n" + players_list)

    def getEmoji(self, num):
        try:
            return [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:"][num]
        except IndexError:
            return ":question:"

    async def abort_message_request(self, player_name):
        await self.message.edit(content=Message.ABORT_REQUEST.format(player_name))


class Message:
    WELCOME = "Qui veut faire une partie de **BANG!** ?\n:point_up:: rejoindre la partie\n:door:: quitter la partie\n:arrow_forward:: lancer le jeu\n:no_entry_sign:: abandonner le jeu\n\n__Participants__:"
    ABORT_REQUEST = ":no_entry_sign: La partie a été annulée par {}."
