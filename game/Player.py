import logging
logger = logging.getLogger(__name__)
from Card import ExecuteEffect


class Player:
    def __init__(self, id, right_player):
        # Place around the table
        self.right_player = right_player
        if right_player is not None:
            right_player.set_left_player(self)
        self.left_player = None
        # Real person id
        self.id = id
        # Played role
        self.role = None
        # Played character informations
        self.name = None
        self.life = 0
        self.effects = []
        self.weapon = None
        # cards
        self.hand = []
        self.in_game = []
        # Turn play
        self.nb_bang_used = 0


    ## GETTERS

    ## Direct getters
    # Place around the table
    def get_left_player(self):
        return self.left_player
    def get_right_player(self):
        return self.right_player
    # Played role & character
    def get_role(self):
        return self.role
    def get_life(self):
        return self.life

    ## Indirect getters
    # Place around the table
    def has_in_range(self, player, max_range=None):
        range_value = (self.weapon.get_weapon_range() if self.weapon is not None else 1) if max_range is None else max_range
        return self.distance_to(player) <= range_value
    def distance_to(self, player):
        # we assume we do not look for distance to self.
        assert self != player
        left_player = self.get_left_player()
        right_player = self.get_right_player()
        distance = 1
        while left_player != self:
            if left_player == player or right_player == player:
                return distance
            left_player = left_player.get_left_player()
            right_player = right_player.get_right_player()
            distance += 1
        raise ValueError("Given player is not part of alive players.")
    # Real person id
    def is_id(self, id):
        return self.id == id
    # Played role & character
    def is_sherif(self):
        return self.role.is_sherif()
    def is_dead(self):
        return self.get_life() <= 0
    # Cards
    def has_card_in_hand(self, card):
        return card in self.hand
    def has_to_many_cards(self):
        return len(self.hand) > self.life
    def has_card_in_game(self, card_name):
        for card in self.in_game:
            if card.name == card_name:
                return True
        return False
    # Turn play


    ## SETTERS

    ## Direct setters
    # Place around the table
    def set_left_player(self, player):
        self.left_player = player
    def set_right_player(self, player):
        self.right_player = player
    # Played role & character
    def set_role(self, role):
        self.role = role
    def set_character(self, character):
        if self.is_sherif():
            character.increase_max_life()
        self.name = character.name
        self.life = character.max_life
    def set_weapon(self, weapon_card, p_stack):
        if self.weapon is not None:
            p_stack.discard_card_from_player_in_game(self, self.weapon)
        self.weapon = weapon_card

    ## Indirect setters
    # Place around the table
    # Played role & character
    def lose_health(self, from_player):
        self.life -= 1
        logger.debug("{} lose 1HP from {}".format(self.id, from_player.id))
        if self.life <= 0:
            self.on_death(from_player)
            return ExecuteEffect.MAKE_DEAD
        return ExecuteEffect.IS_SUCCESS
    # Cards
    def add_card_to_hand(self, card):
        self.hand.append(card)
    def remove_card_from_hand(self, card):
        self.hand.remove(card)
    def add_card_to_in_game(self, card):
        self.in_game.append(card)
    def remove_card_from_in_game(self, card):
        self.in_game.remove(card)
    # Turn play
    def init_turn(self):
        self.nb_bang_used = 0

    def on_death(self, from_player):
        # if (self == from_player):
        #     logger.debug("Detect suicide.")
        #     print("*** Suicide")
        left_player = self.get_left_player()
        right_player = self.get_right_player()
        left_player.set_right_player(right_player)
        right_player.set_left_player(left_player)
        logger.debug("{} has been deadly shot.".format(self.id))
