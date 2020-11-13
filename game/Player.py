import logging
logger = logging.getLogger(__name__)


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
    def has_in_range(self, player):
        range_value = self.weapon.get_range() if self.weapon is not None else 1
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
    # Cards
    def has_card_in_hand(self, card):
        return card in self.hand
    def has_to_many_cards(self):
        return len(self.hand) > self.life
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
        self.life = 1

    ## Indirect setters
    # Place around the table
    # Played role & character
    def lose_health(self):
        self.life -= 1
        if self.life <= 0:
            self.on_death()
    # Cards
    def add_card_to_hand(self, card):
        self.hand.append(card)
    def remove_card_from_hand(self, card):
        self.hand.remove(card)
    # Turn play
    def init_turn(self):
        self.nb_bang_used = 0

    def on_death(self):
        left_player = self.get_left_player()
        right_player = self.get_right_player()
        left_player.set_right_player(right_player)
        right_player.set_left_player(left_player)
        logger.debug("{} has been deadly shot.".format(self.id))
