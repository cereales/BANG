
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

    def get_left_player(self):
        return self.left_player
    def get_right_player(self):
        return self.right_player
    def get_role(self):
        return self.role
    def get_life(self):
        return self.life

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

    def set_left_player(self, player):
        self.left_player = player
    def set_right_player(self, player):
        self.right_player = player
    def set_role(self, role):
        self.role = role
    def set_character(self, character):
        self.life = 1

    def init_turn(self):
        self.nb_bang_used = 0

    def add_card_to_hand(self, card):
        self.hand.append(card)
    def remove_card_from_hand(self, card):
        self.hand.remove(card)
