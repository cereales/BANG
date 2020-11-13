import logging
from Pile import Pile
from Role import Role
from Character import Character
from Card import Card
from Player import Player
import json
logger = logging.getLogger(__name__)


MIN_NB_PLAYERS = 4
MAX_NB_PLAYERS = 7

class TurnStep:
    DRAW = 0
    ACTION = 1
    DISCARD = 2
    END = 3
    END_OF_GAME = 4


class Bang:
    """
    Represent one instance of BANG! game.
    """
    def __init__(self, players_id):
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
        self.current_player = None
        self.current_turn_step = TurnStep.DRAW

        # Initiate types of cards
        self.roles = Pile()
        with open("ressources/roles.json") as file:
            data = json.load(file)
            for id in data:
                if (self.nb_players < int(id)):
                    break # limit the number of role card to the number of players
                role = data[id]
                self.roles.declare_card(int(id), Role(role["name"]))
        self.cards = Pile()
        with open("ressources/cards.json") as file:
            data = json.load(file)
            for id in data:
                card = data[id]
                self.cards.declare_card(id, Card(id, card["name"], card["effects"]))
        self.characters = Pile()
        with open("ressources/characters.json") as file:
            data = json.load(file)
            for id in data:
                character = data[id]
                self.characters.declare_card(id, Character())

        # Distribute roles
        self.roles.shuffle()
        for player in self.players:
            role = self.roles.draw_card()
            if role.is_sherif():
                self.first_player = player
            player.set_role(role)
        self.current_player = self.first_player

        # Distribute characters
        self.characters.shuffle()
        for player in self.players:
            player.set_character(self.characters.draw_card())

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
            return []

        first = self.players[index]
        yield first
        player = first.get_left_player()
        while player is not first:
            yield player
            player = player.get_left_player()


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
        if card.execute(self.current_player, target_player, target_card):
            self.cards.discard_card_from_player(self.current_player, card)

        # Check victory
        # tmp : victory is to kill everybody
        if self.current_player.get_left_player() == self.current_player:
            logger.info("VICTORY of {}".format(player_id))
            self.current_turn_step = TurnStep.END_OF_GAME
            
        return True


    def turn_step_end(self, player_id):
        if not self.current_player.is_id(player_id) or self.current_turn_step != TurnStep.ACTION:
            logger.error("It is not turn to {} to stop playing cards.".format(player_id))
            return False

        # End turn
        if self.current_player.has_to_many_cards():
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
        self.cards.discard_card_from_player(self.current_player, card)

        # End turn
        if not self.current_player.has_to_many_cards():
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
