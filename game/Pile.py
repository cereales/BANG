import logging
import random
logger = logging.getLogger(__name__)


class Pile:
    """
    Represents a card stack.
    Top of the stack is indentified by index.
    Stack is from top (index=0) to bottom (index=None).
    """
    def __init__(self):
        # Declaration
        self.cards = {}
        self.nb_cards = 0
        # Use as sorted stack
        self.sorted_card_id = []
        self.stack_len = 0
        self.index = 0
        self.rack_sorted_card_id = []

    def reset(self, except_card_id=None):
        """
        Rebuild the stack from all declared cards.
        Except for card ids that are in except list.
        Exceptions are put in rack.
        """
        if except_card_id is None:
            except_card_id = []

        self.index = 0
        self.sorted_card_id = []
        self.rack_sorted_card_id = []
        for id in self.cards:
            if id not in except_card_id:
                self.sorted_card_id.append(id)
            else:
                self.rack_sorted_card_id.append(id)
        self.stack_len = len(self.sorted_card_id)

    def declare_card(self, id, card):
        """
        Add a new card to the stack.
        """
        self.cards[id] = card
        self.nb_cards += 1
        self.stack_len += 1
        self.sorted_card_id.append(id)

    def shuffle(self, start_index=None, end_index=None):
        if start_index is None:
            start_index = self.index

        if (start_index == 0 and end_index is None):
            random.shuffle(self.sorted_card_id)
        else:
            if end_index is None:
                end_index = self.stack_len - 1
            copy = self.sorted_card_id[start_index:end_index + 1]
            random .shuffle(copy)
            self.sorted_card_id[start_index:end_index + 1] = copy

    def get_card(self, id):
        """
        Returns the card object from id.
        """
        return self.cards[id]


    ## Draw card

    def draw_card(self):
        """
        Draw card at the top and returns card.
        """
        if self.index >= self.stack_len:
            logger.info("Regenerate stack from shuffled rack.")
            self.sorted_card_id = self.rack_sorted_card_id
            self.rack_sorted_card_id = []
            self.index = 0
            self.stack_len = len(self.sorted_card_id)
            self.shuffle()

        card = self.cards[self.sorted_card_id[self.index]]
        self.index += 1
        return card

    def draw_card_to_rack(self):
        card = self.draw_card()
        self.discard_card(card)
        return card

    def draw_card_to_player(self, player):
        player.add_card_to_hand(self.draw_card())


    ## Discard card

    def discard_card(self, card):
        """
        Throw a card away in the rack.
        """
        self.rack_sorted_card_id.append(card.get_id())

    def discard_card_from_player_hand(self, player, card):
        player.remove_card_from_hand(card)
        self.discard_card(card)

    def discard_card_from_player_in_game(self, player, card):
        player.remove_card_from_in_game(card)
        self.discard_card(card)
