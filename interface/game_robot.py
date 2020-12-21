import logging, utils.Tools as Tools
logger = logging.getLogger(__name__)

import discord
from interface.robot import Robot
from utils.Emoji import Emoji


class State:
    CREATED = 0
    INITIALIZED = 1
    ABORTED = 2


class GameRobot(Robot):
    """
    Represents one instance of a UI for BANG! game.
    """
    def __init__(self, client, channel):
        super().__init__(client, channel)
        self.state = State.CREATED
        self.ordered_player_ids = []

    async def init(self):
        assert self.state == State.CREATED
        self.state = State.INITIALIZED
        message = await self.refresh_welcome_message()
        await message.add_reaction(Emoji.get_unicode_emoji("point_up"))
        await message.add_reaction(Emoji.get_unicode_emoji("door"))
        await message.add_reaction(Emoji.get_unicode_emoji("play"))
        await message.add_reaction(Emoji.get_unicode_emoji("abort"))


    ## Events

    async def on_raw_reaction_add(self, payload):
        # TODO: catch asserts
        # ignore reactions added by me
        if payload.user_id == self.client.user.id:
            return
        # ignore reactions to others messages than the waiting one
        if not self.is_tracked(payload.message_id):
            return
        # NOTE: self.channel.id == payload.channel_id  in case of reaction in main channel (from the way robot is added)

        logger.debug("Reaction {} {} detected by robot.".format(type(payload.emoji), payload.emoji))
        if self.state == State.INITIALIZED:
            # In initialisation, only main channel has been declared.
            # payload.emoji.name is not None because not in case of _removing_ reaction of deleted emoji
            if self.emoji_on_message("point_up", payload):
                if payload.user_id not in self.ordered_player_ids:
                    logger.debug("Player {} wants to join".format(payload.user_id))
                    if self.in_guild():
                        # OPTIMIZE: direct access to member object
                        await self.get_player_id(player=payload.member)
                    else:
                        await self.get_player_id(player_id=payload.user_id)
                    self.ordered_player_ids.append(payload.user_id)
                    await self.refresh_welcome_message()
            elif self.emoji_on_message("door", payload):
                if payload.user_id in self.ordered_player_ids:
                    logger.debug("Player {} wants to leave".format(payload.user_id))
                    self.ordered_player_ids.remove(payload.user_id)
                    await self.refresh_welcome_message()
            elif self.emoji_on_message("play", payload):
                logger.debug("Start game")
            elif self.emoji_on_message("abort", payload):
                logger.debug("Abort game")
                self.state = State.ABORTED
                await self.get_player_id(player_id=payload.user_id) # to allow no playing users to abort game
                player = self.get_player(payload.user_id)
                assert player is not None
                await self.abort_message_request(player.display_name)
            else:
                logger.debug("Not the expected reaction")


    ## Messages

    async def refresh_welcome_message(self):
        players_list = "\n".join(["{} {}".format(Emoji.get_discord_emoji(order + 1), self.get_player(player_id).display_name) for order, player_id in enumerate(self.ordered_player_ids)])
        await self.refresh(Message.WELCOME.format(Emoji.get_discord_emoji("point_up"), Emoji.get_discord_emoji("door"), Emoji.get_discord_emoji("play"), Emoji.get_discord_emoji("abort")) + "\n" + players_list)

    async def abort_message_request(self, player_name):
        await self.refresh(Message.ABORT_REQUEST.format(player_name))
        message = await self.get_message()
        if self.in_guild():
            await message.clear_reactions()


class Message:
    WELCOME = "Qui veut faire une partie de **BANG!** ?\n{}: rejoindre la partie\n{}: quitter la partie\n{}: lancer le jeu\n{}: abandonner le jeu\n\n__Participants__:"
    ABORT_REQUEST = ":no_entry_sign: La partie a été annulée par {}."
