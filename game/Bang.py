import logging
from Pile import Pile
from Role import Role
from Character import Character
from Card import Card, ExecuteEffect
from Player import Player
import json
logger = logging.getLogger(__name__)


MIN_NB_PLAYERS = 4
MAX_NB_PLAYERS = 7

class TurnStep:
    DRAW = 0
    ACTION = 1
    REACTION = 5
    DISCARD = 2
    END = 3
    END_OF_GAME = 4


class Bang:
    """
    Represent one instance of BANG! game.
    """
    def __init__(self, players_id, sherif=None):
        self.winners = None
        self.loosers = None

        # Check number of player limit
        self.nb_players = len(players_id)
        if (self.nb_players < MIN_NB_PLAYERS or MAX_NB_PLAYERS < self.nb_players):
            raise ValueError("Invalid number of players: {}".format(self.nb_players))

        # Initiate players around table
        self.players = []
        self.players_id = {}
        previous_player = None
        for player_id in players_id:
            previous_player = Player(player_id, previous_player)
            self.players.append(previous_player)
            self.players_id[player_id] = previous_player
        self.players[0].set_right_player(self.players[-1])
        self.players[-1].set_left_player(self.players[0])
        self.first_player = None
        self.renegat = None
        self.current_player = None
        self.current_turn_step = None
        self.next_react_players = None
        self.current_card_to_react = None

        # Initiate types of cards
        self.roles = Pile()
        with open("ressources/roles.json") as file:
            data = json.load(file)
            for id in data:
                if (self.nb_players < int(id)):
                    break # limit the number of role card to the number of players
                role = data[id]
                self.roles.declare_card(int(id), Role(id, role["name"], role["desc"]))
        self.cards = Pile()
        with open("ressources/cards.json") as file:
            data = json.load(file)
            for id in data:
                card = data[id]
                self.cards.declare_card(id, Card(id, card["id"], card["name"], card["activation"], card["effects"]))
        self.characters = Pile()
        with open("ressources/characters.json") as file:
            data = json.load(file)
            for id in data:
                character = data[id]
                self.characters.declare_card(id, Character(id, character["name"], character["life"]))
        self.init(forceSherif=sherif)

    def relaunch(self, players_id_to_keep_character, sherif=None):
        keep_character_ids = []
        skip_character_player = []
        for player_id in players_id_to_keep_character:
            player = self.players_id[player_id]
            if player in self.alive_players():
                skip_character_player.append(player)
                keep_character_ids.append(player.get_character_id())
            else:
                logger.error("Player {} is not alive and cannot keep his character.".format(player_id))

        # Restart Players
        previous_player = self.players[-1]
        for player in self.players:
            # place around the table
            player.set_right_player(previous_player)
            previous_player.set_left_player(player)
            player.reset()
            previous_player = player
        self.roles.reset()
        self.characters.reset(keep_character_ids)
        self.cards.reset()
        self.init(skip_character_player, forceSherif=sherif)

    def init(self, skip_character_player=None, forceSherif=None):
        if skip_character_player is None:
            skip_character_player = []
        if forceSherif is not None:
            # that means we force the sherif role
            logger.debug("Forcing role Sherif to {}".format(forceSherif))
            card = self.roles.draw_card_to_rack()
            assert card.is_sherif()
            # WARNING: *sherif* if the id of player to be sherif
            self.players_id[forceSherif].set_role(card)
            self.roles.discard_card(card)

        self.winners = []
        self.loosers = []

        # Initiate players around table
        self.current_turn_step = TurnStep.DRAW

        # Distribute roles
        self.roles.shuffle()
        for player in self.players:
            if forceSherif is not None and player.is_id(forceSherif):
                self.first_player = player
            else:
                role = self.roles.draw_card_to_rack()
                if role.is_sherif():
                    self.first_player = player
                elif role.is_renegat():
                    self.renegat = player
                player.set_role(role)
        self.current_player = self.first_player

        # Distribute characters
        self.characters.shuffle()
        for player in self.players:
            if player not in skip_character_player:
                player.set_character(self.characters.draw_card_to_rack())
            else:
                player.set_character(player.character) # reset info about character like life.

        # Draw initial cards
        self.cards.shuffle()
        for player in self.players:
            for _ in range(player.get_life()):
                self.cards.draw_card_to_player(player)


    def alive_players(self):
        """
        Starting from sherif, iter through all still alive players.
        """
        # Looking for first player in alive.
        index = 0
        while index < self.nb_players and self.players[index].is_dead():
            index += 1
        if index == self.nb_players:
            return iter([])

        first = self.players[index]
        yield first
        player = first.get_left_player()
        while player is not first:
            yield player
            player = player.get_left_player()


    def get_alive_player_number(self):
        nb_alive_players = 0
        for player in self.alive_players():
            nb_alive_players += 1
        return nb_alive_players


    def check_victory(self):
        assert self.winners == []
        assert self.loosers == []
        # Adapt next player turn if suicide
        # In case of suicide, current player is not anymore.
        if self.current_player.is_dead():
            left_player = self.current_player.get_left_player()
            while self.current_player.is_dead() and self.current_player != left_player:
                self.current_player = left_player
                left_player = left_player.get_left_player()
                self.current_turn_step = TurnStep.DRAW
            logger.debug("Detect suicide. Next player {} will start his turn.".format(self.current_player.id))

        logger.debug("Looking if there is a winner.")
        if self.first_player.is_dead():
            logger.debug("Sherif is dead.")
            nb_alive_players = self.get_alive_player_number()
            logger.debug("Renegat: {} is {}.".format(self.renegat.id, "still alive" if self.renegat in self.alive_players() else "dead"))
            logger.debug("{} players still alive.".format(nb_alive_players))
            if nb_alive_players == 1 and self.renegat in self.alive_players():
                for player in self.players:
                    if player.is_renegat():
                        self.winners.append(player)
                    else:
                        self.loosers.append(player)
            elif nb_alive_players > 0:
                for player in self.players:
                    if player.is_outlaw():
                        self.winners.append(player)
                    else:
                        self.loosers.append(player)
        else:
            for player in self.alive_players():
                if player.is_outlaw() or player.is_renegat():
                    return False
            for player in self.players:
                if player.is_sherif() or player.is_adjoint():
                    self.winners.append(player)
                else:
                    self.loosers.append(player)
        self.current_turn_step = TurnStep.END_OF_GAME
        logger.info("END OF GAME")
        logger.info("winners : {}".format(["{} ({})".format(p.id, self.show_role(p.id).name) for p in self.winners]))
        logger.info("loosers : {}".format(["{} ({})".format(p.id, self.show_role(p.id).name) for p in self.loosers]))
        return True


    ## Turn step actions

    def turn_step_draw(self, player_id):
        if not self.current_player.is_id(player_id) or self.current_turn_step != TurnStep.DRAW:
            logger.error("It is not turn to {} to draw a card.".format(player_id))
            return False
        self.current_player.init_turn()

        # Draw cards
        self.cards.draw_card_to_player(self.current_player)
        self.cards.draw_card_to_player(self.current_player)

        # Start next turn step
        self.current_turn_step = TurnStep.ACTION
        return True


    def turn_step_play_card(self, player_id, card_id, target_player_id=None, target_card_id=None):
        """
        Method to call when it is your turn to play a card from your hand.
        In case of brown card :
        - checks targets and go to react mode
        - discard card from hand
        In case of blue  card :
        - wear card from hand
        """
        if not self.current_player.is_id(player_id) or self.current_turn_step != TurnStep.ACTION:
            logger.error("It is not turn to player {} to play a card.".format(player_id))
            return False
        card = self.cards.get_card(card_id)
        if not self.current_player.has_card_in_hand(card):
            logger.error("Player {} is trying to play a card he does not have.".format(player_id))
            return False

        # Play card from hand
        target_player = self.players_id[target_player_id] if target_player_id is not None else None
        target_card = self.cards.get_card(target_card_id) if target_card_id is not None else None
        if card.is_type_card_immediate():
            # Check possible targets
            self.next_react_players = card.possible_targets(self.current_player, target_player, target_card)
            if self.next_react_players is None:
                return False
            # Remove card from hand
            self.cards.discard_card_from_player_hand(self.current_player, card)

            # Switch to react mode
            assert len(self.next_react_players) == 1 # TODO: support multiple effects
            self.next_react_players = self.next_react_players[0]
            self.current_turn_step = TurnStep.REACTION
            self.current_card_to_react = card
        else:
            # Play card
            execution_result, player_with_card_in_game = card.apply_effects(self.cards, self.current_player, target_player, target_card)
            if not execution_result:
                return False
            # Wear card from hand
            self.current_player.remove_card_from_hand(card)
            player_with_card_in_game.add_card_to_in_game(card)

            if execution_result & ExecuteEffect.MAKE_DEAD:
                self.check_victory()
        return True


    def turn_step_react_play_card(self, player_id, card_id):
        """
        Method to call when it is your turn to react with a card from your hand or your game.
        In case of card from hand (brown card) :
        - execute card (count as a check)
        - discard card from hand
        In case of card from game (blue card) :
        - execute card (count as a check)
        # set card as used for this turn (avoid playing several times the same card)
        """
        if self.next_react_players is None or not self.next_react_players[0].is_id(player_id) or self.current_turn_step != TurnStep.REACTION:
            logger.error("It is not turn to {} to play a card in reaction.".format(player_id))
            return False
        current_react_player = self.next_react_players[0]
        card = self.cards.get_card(card_id)
        if not current_react_player.has_card_in_hand(card):
            logger.error("Player {} is trying to react with a card he does not have.".format(player_id))
            return False

        if current_react_player.has_card_in_hand(card):
            assert card.is_type_card_immediate() # is brown
            # Execute card with check
            execution_result = card.execute(self.cards, current_react_player, self.current_player, in_reaction_to=self.current_card_to_react)
            # Remove card from hand
            if execution_result:
                self.cards.discard_card_from_player_hand(current_react_player, card)
        else:
            assert current_react_player.has_card_in_game(card.name)
            assert not card.is_type_card_immediate() # is blue
            # Execute card with check
            execution_result = card.execute(self.cards, current_react_player, self.current_player, in_reaction_to=self.current_card_to_react)

        self.close_react_step()
        return execution_result


    def turn_step_dont_react(self, player_id):
        """
        Method to call when it is your turn to react, and you do not want to.
        Execute card effect.
        """
        if self.next_react_players is None or not self.next_react_players[0].is_id(player_id) or self.current_turn_step != TurnStep.REACTION:
            logger.error("It is not turn to {} to play a card in reaction.".format(player_id))
            return False

        # Execute card effect
        execution_result = ExecuteEffect.FAIL
        target_player = self.next_react_players[0]
        target_card = None # TODO: support target_card
        card = self.current_card_to_react
        execution_result = card.execute(self.cards, self.current_player, target_player, target_card)
        # player has not card in hand anymore, but can draw it again from rewards for example

        self.close_react_step()
        return execution_result


    def close_react_step(self):
        if len(self.next_react_players) == 1:
            self.next_react_players = None
            self.current_turn_step = TurnStep.ACTION
            self.check_victory()
        else:
            self.next_react_players = self.next_react_players[1:]


    def turn_step_end(self, player_id):
        if not self.current_player.is_id(player_id) or self.current_turn_step != TurnStep.ACTION:
            logger.error("It is not turn to {} to stop playing cards.".format(player_id))
            return False

        # End turn
        if self.current_player.has_too_many_cards():
            self.current_turn_step = TurnStep.DISCARD
        else:
            self.current_turn_step = TurnStep.END
            assert self.turn_step_next_player(player_id)
        return True


    def turn_step_discard_card(self, player_id, card_id):
        if not self.current_player.is_id(player_id) or self.current_turn_step != TurnStep.DISCARD:
            logger.error("It is not turn to {} to discard a card.".format(player_id))
            return False
        card = self.cards.get_card(card_id)
        if not self.current_player.has_card_in_hand(card):
            logger.error("Player {} is trying to discard a card he does not have.".format(player_id))
            return False

        # Discard one over numbered card
        self.cards.discard_card_from_player_hand(self.current_player, card)

        # End turn
        if not self.current_player.has_too_many_cards():
            self.current_turn_step = TurnStep.END
        return True


    def turn_step_next_player(self, player_id):
        if not self.current_player.is_id(player_id) or self.current_turn_step != TurnStep.END:
            logger.error("Player {} cannot end his turn.".format(player_id))
            return False

        # Next player
        self.current_player = self.current_player.get_left_player()
        self.current_turn_step = TurnStep.DRAW
        return True


    ## Out access

    def show_role(self, player_id):
        player = self.players_id[player_id]
        return player.get_role() if player.is_sherif() or player.is_dead() or self.current_turn_step == TurnStep.END_OF_GAME else None

    def show_role_str(self, player_id):
        role = self.show_role(player_id)
        return role.name if role is not None else ""

    def need_to_discard_before_next_player(self):
        return self.current_turn_step == TurnStep.DISCARD

    # def show_character(self, player_id):
    #     player = self.players_id[player_id]
    #     return player
