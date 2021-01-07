import logging, utils.Tools as Tools
logger = logging.getLogger(__name__)

import discord
from interface.robot import Robot
from interface.ia_discard import IADiscard
from utils.Emoji import Emoji
from game.Bang import Bang


class State:
    CREATED = 0
    INITIALIZED = 1
    ABORTED = 2
    PLAYING = 3
    DISCARD = 4
    END = 5


class GameRobot(Robot):
    """
    Represents one instance of a UI for BANG! game.
    """
    def __init__(self, client, channel):
        super().__init__(client, channel)
        self.state = State.CREATED
        self.ordered_player_ids = []
        self.robot_count = 0

    async def init(self):
        assert self.state == State.CREATED
        self.state = State.INITIALIZED
        message = await self.refresh_welcome_message()
        await message.add_reaction(Emoji.get_unicode_emoji("point_up"))
        await message.add_reaction(Emoji.get_unicode_emoji("door"))
        await message.add_reaction(Emoji.get_unicode_emoji("add_robot"))
        await message.add_reaction(Emoji.get_unicode_emoji("remove_robot"))
        await message.add_reaction(Emoji.get_unicode_emoji("play"))
        await message.add_reaction(Emoji.get_unicode_emoji("abort"))


    ## Events

    async def on_raw_reaction_add(self, payload):
        logger.log(Tools.VERBOSE, "reaction")
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
            expected_message = await self.get_message()
            if self.emoji_on_message("point_up", payload, expected_message):
                if payload.user_id not in self.ordered_player_ids:
                    logger.debug("Player {} wants to join".format(payload.user_id))
                    if self.in_guild():
                        # OPTIMIZE: direct access to member object
                        await self.get_player_id(player=payload.member)
                    else:
                        await self.get_player_id(player_id=payload.user_id)
                    self.ordered_player_ids.append(payload.user_id)
                    await self.refresh_welcome_message()
            elif self.emoji_on_message("door", payload, expected_message):
                if payload.user_id in self.ordered_player_ids:
                    logger.debug("Player {} wants to leave".format(payload.user_id))
                    self.ordered_player_ids.remove(payload.user_id)
                    await self.refresh_welcome_message()
            elif self.emoji_on_message("add_robot", payload, expected_message):
                logger.debug("Add IA")
                if self.robot_count < 4:
                    player_id = ["Alain", "Bernard", "Charlie", "Dede"][self.robot_count]
                else:
                    player_id = "IA" + str(self.robot_count)
                self.ordered_player_ids.append(player_id)
                self.robot_count += 1
                self.declare_robot(player_id, IADiscard(player_id))
                await self.refresh_welcome_message()
            elif self.emoji_on_message("remove_robot", payload, expected_message):
                logger.debug("Remove IA")
                if self.robot_count > 0:
                    self.robot_count -= 1
                    if self.robot_count < 4:
                        player_id = ["Alain", "Bernard", "Charlie", "Dede"][self.robot_count]
                    else:
                        player_id = "IA" + str(self.robot_count)
                    self.ordered_player_ids.remove(player_id)
                    await self.refresh_welcome_message()
            elif self.emoji_on_message("play", payload, expected_message):
                logger.debug("Start game")
                try:
                    self.game = Bang(self.ordered_player_ids)
                except ValueError as err:
                    logger.error(err)
                    await self.add(Emoji.get_discord_emoji("error") + " " + str(err))
                    return
                self.state = State.PLAYING
                await self.send_presentation_message()
                await self.send_next_player(self.game.current_player.id)
            elif self.emoji_on_message("abort", payload, expected_message):
                logger.debug("Abort game")
                self.state = State.ABORTED
                await self.get_player_id(player_id=payload.user_id) # to allow no playing users to abort game
                player = self.get_player(payload.user_id)
                assert player is not None
                await self.abort_message_request(player.display_name)
            else:
                logger.debug("Not the expected reaction")
        elif self.state == State.PLAYING:
            expected_message = await self.get_message(player_id=payload.user_id)
            if self.emoji_on_message("draw", payload, expected_message):
                if self.game.turn_step_draw(payload.user_id):
                    await self.send_hand_message(payload.user_id)
                    await self.add_play_card(payload.user_id)
                else:
                    await self.add_wrong_turn(payload.user_id)
            elif self.emoji_on_message("next", payload, expected_message):
                if self.game.turn_step_end(payload.user_id):
                    if self.game.need_to_discard_before_next_player():
                        self.state = State.DISCARD
                        await self.send_discard_card(payload.user_id)
                    else:
                        await self.send_next_player(self.game.current_player.id)
                else:
                    await self.add_wrong_turn(payload.user_id)
            else:
                # Check all card numbers
                found_index = None
                for index in range(1, len(self.game.current_player.hand) + 1):
                    if self.emoji_on_message(index, payload, expected_message):
                        found_index = index - 1
                if found_index is not None and self.game.turn_step_play_card(payload.user_id, found_index):
                    pass # TODO:
                else:
                    await self.add_wrong_turn(payload.user_id)
        elif self.state == State.DISCARD:
            logger.log(Tools.VERBOSE, Emoji.equals("next", payload.emoji.name))
            expected_message = await self.get_message(player_id=payload.user_id)
            if self.emoji_on_message("next", payload, expected_message):
                if self.game.need_to_discard_before_next_player():
                    await self.add(Message.PRIVATE_TOO_MANY_CARDS.format(Emoji.get_discord_emoji("error")))
                else:
                    self.game.turn_step_next_player(payload.user_id)
                    await self.send_next_player(self.game.current_player.id)
            else:
                # Check all card numbers
                found_index = None
                for index in range(1, len(self.game.current_player.hand) + 1):
                    if self.emoji_on_message(index, payload, expected_message):
                        found_index = index - 1
                if found_index is not None:
                    card = self.game.current_player.hand[found_index]
                    if self.game.turn_step_discard_card(payload.user_id, card.id):
                        await self.add_discard_message(payload.user_id, card)
                        await self.send_hand_message(payload.user_id)
                        if self.game.need_to_discard_before_next_player():
                            self.send_discard_card(payload.user_id)
                        else:
                            self.state = State.END
                            message = await self.get_message(player_id=payload.user_id)
                            await message.add_reaction(Emoji.get_unicode_emoji("next"))
                    else:
                        await self.add_wrong_turn(payload.user_id)
                else:
                    await self.add_wrong_turn(payload.user_id)


    ## Messages

    async def refresh_welcome_message(self):
        players_list = "\n".join(["{} {}{}".format(Emoji.get_discord_emoji(order + 1), Emoji.get_discord_emoji("robot") + " " if self.is_robot(player_id) else "", self.get_player(player_id).display_name) for order, player_id in enumerate(self.ordered_player_ids)])
        message = await self.refresh(Message.WELCOME.format(Emoji.get_discord_emoji("point_up"), Emoji.get_discord_emoji("door"), Emoji.get_discord_emoji("add_robot"), Emoji.get_discord_emoji("remove_robot"), Emoji.get_discord_emoji("play"), Emoji.get_discord_emoji("abort")) + "\n" + players_list)
        return message

    async def abort_message_request(self, player_name):
        await self.refresh(Message.ABORT_REQUEST.format(player_name))
        message = await self.get_message()
        await self.clear_reactions()

    async def send_presentation_message(self):
        await self.clear_reactions()
        for player_id in self.ordered_player_ids[:1]:
            game_player = self.game.players_id[player_id]
            await self.send(Message.PRIVATE_DISCOVER.format(game_player.role.name), player_id=player_id)
            await self.send_hand_message(player_id)
        await self.send_main_view()

    async def send_main_view(self):
        await self.forget()
        for player_id in self.ordered_player_ids[:1]:
            player = self.get_player(player_id)
            game_player = self.game.players_id[player_id]
            await self.add("- {} {} {}/{}HP ; {} cartes".format(player.display_name, self.game.show_role_str(player_id), game_player.life, game_player.max_life(), len(game_player.hand)))
        for player_id in self.ordered_player_ids[1:]:
            game_player = self.game.players_id[player_id]
            await self.add("- {} {} {}/{}HP ; {} cartes".format(player_id, self.game.show_role_str(player_id), game_player.life, game_player.max_life(), len(game_player.hand)))

    async def send_next_player(self, player_id):
        name = await self.get_player(player_id).display_name
        await self.add(Message.NEW_TURN.format(Emoji.get_discord_emoji("right_arrow"), player_id))
        message = await self.send(Message.PRIVATE_NEW_TURN, player_id=player_id)
        await message.add_reaction(Emoji.get_unicode_emoji("draw"))

    async def add_wrong_turn(self, player_id):
        await self.add(Message.PRIVATE_WRONG_TURN.format(Emoji.get_discord_emoji("error")), player_id=player_id)

    async def send_hand_message(self, player_id):
        await self.forget(player_id=player_id)
        game_player = self.game.players_id[player_id]
        logger.log(Tools.VERBOSE, [(c.id, c.name) for c in game_player.hand])
        for card in game_player.hand:
            await self.add("- {} {}".format(card.id, card.name), player_id=player_id)

    async def add_play_card(self, player_id):
        message = await self.add(Message.PRIVATE_PLAY, player_id=player_id)
        game_player = self.game.players_id[player_id]
        for index in range(1, len(game_player.hand) + 1):
            await message.add_reaction(Emoji.get_unicode_emoji(index))
        await message.add_reaction(Emoji.get_unicode_emoji("next"))

    async def send_discard_card(self, player_id):
        message = await self.send(Message.PRIVATE_DISCARD, player_id=player_id)
        game_player = self.game.players_id[player_id]
        for index in range(1, len(game_player.hand) + 1):
            await message.add_reaction(Emoji.get_unicode_emoji(index))

    async def add_discard_message(self, player_id, card):
        await self.add(Message.DISCARD_CARD.format(Emoji.get_discord_emoji("abort"), player_id, card.id, card.name))


class Message:
    WELCOME = "Qui veut faire une partie de **BANG!** ?\n{}: rejoindre la partie\n{}: quitter la partie\n{}: ajouter un joueur virtuel\n{}: retirer un joueur virtuel\n{}: lancer le jeu\n{}: abandonner le jeu\n\n__Participants__:"
    ABORT_REQUEST = ":no_entry_sign: La partie a été annulée par {}."
    NEW_TURN = "{} Tour de {}"
    DISCARD_CARD = "{} {} se défausse de {} {}."
    PRIVATE_DISCOVER = "Tu es {}."
    PRIVATE_NEW_TURN = "C'est ton tour."
    PRIVATE_WRONG_TURN = "{} Ce n'est pas ton tour."
    PRIVATE_PLAY = "Jouer une carte :"
    PRIVATE_TOO_MANY_CARDS = "{} Trop de cartes en main."
    PRIVATE_DISCARD = "Se défausser d'une carte :"
