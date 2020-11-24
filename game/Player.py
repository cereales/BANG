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
        self.character = None
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
    def is_adjoint(self):
        return self.role.is_adjoint()
    def is_renegat(self):
        return self.role.is_renegat()
    def is_outlaw(self):
        return self.role.is_outlaw()
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
    def max_life(self):
        return self.character.max_life + self.is_sherif()


    ## SETTERS

    ## Direct setters
    # Place around the table
    def set_left_player(self, player):
        self.left_player = player
    def set_right_player(self, player):
        self.right_player = player
    # Played role & character
    def reset(self):
        self.hand = []
        self.in_game = []
        self.effects = []
        self.weapon = None
    def set_role(self, role):
        self.role = role
    def set_character(self, character):
        self.character = character
        self.life = self.max_life()
    def set_weapon(self, weapon_card, p_stack):
        if self.weapon is not None:
            p_stack.discard_card_from_player_in_game(self, self.weapon)
        self.weapon = weapon_card

    ## Indirect setters
    # Place around the table
    # Played role & character
    def lose_health(self, p_stack, from_player):
        self.life -= 1
        logger.debug("{} lose 1HP from {}".format(self.id, from_player.id))
        if self.life <= 0:
            self.on_death(p_stack, from_player)
            return ExecuteEffect.MAKE_DEAD
        return ExecuteEffect.IS_SUCCESS
    # Cards
    def add_card_to_hand(self, card):
        self.hand.append(card)
    def remove_card_from_hand(self, card):
        self.hand.remove(card)
        logger.debug("{} : Remove card id={} from hand.".format(self.id, card.id))
    def remove_all_cards_from_hand(self, p_stack):
        for card in self.hand.copy():
            p_stack.discard_card_from_player_hand(self, card)
    def add_card_to_in_game(self, card):
        self.in_game.append(card)
    def remove_card_from_in_game(self, card):
        self.in_game.remove(card)
        logger.debug("{} : Remove card id={} from game.".format(self.id, card.id))
    def remove_all_cards_from_in_game(self, p_stack):
        for card in self.in_game.copy():
            p_stack.discard_card_from_player_in_game(self, card)
    # Turn play
    def init_turn(self):
        self.nb_bang_used = 0

    def on_death(self, p_stack, from_player):
        is_suicide = False
        if (self == from_player):
            is_suicide = True
            logger.debug("Detect suicide.")
            # logger.debug("************************************************************")
            # print("*** Suicide")
        left_player = self.get_left_player()
        right_player = self.get_right_player()
        left_player.set_right_player(right_player)
        right_player.set_left_player(left_player)
        self.remove_all_cards_from_hand(p_stack)
        self.remove_all_cards_from_in_game(p_stack)
        logger.debug("{} has been deadly shot.".format(self.id))

        # Penalty
        if self.is_adjoint() and from_player.is_sherif():
            from_player.remove_all_cards_from_hand(p_stack)
            from_player.remove_all_cards_from_in_game(p_stack)
        # Reward
        if self.is_outlaw() and not is_suicide:
            p_stack.draw_card_to_player(from_player)
            p_stack.draw_card_to_player(from_player)
            p_stack.draw_card_to_player(from_player)
