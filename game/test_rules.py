import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from Bang import Bang, TurnStep

def main(player, current):
    logger.info("{}\t{}HP ({})  {} {}".format(player.id, player.get_life(), player.role.name, [c.name for c in player.in_game], "<--" if current == player else ""))
    for card in player.hand:
        logger.info("- {} ({})".format(card.symbol, card.name))
def changePlayer(player):
    assert game.turn_step_end(player.id)
    if game.current_turn_step == TurnStep.DISCARD:
        while not game.turn_step_next_player(player.id):
            assert game.turn_step_discard_card(player.id, player.hand[0].id)
    player = player.get_left_player()
    assert game.turn_step_draw(player.id)
    return player
def findPlayerWith(player, card_name, doubleCard=False, forcePlayer=None):
    ids = [c.id for c in player.hand if c.name == card_name]
    counter = 0
    while (len(ids) <= doubleCard or (forcePlayer is not None and forcePlayer != player)) and counter < 30:
        logger.warning("{} {} {}".format(len(ids), forcePlayer.id if forcePlayer is not None else None, player.id))
        player = changePlayer(player)
        ids = [c.id for c in player.hand if c.name == card_name]
        counter += 1
    logger.warning("{} {} {}".format(len(ids), forcePlayer.id if forcePlayer is not None else None, player.id))
    logger.warning("{} and ({} or {})".format(len(ids) > doubleCard, forcePlayer is  None, forcePlayer == player))
    if counter >= 30:
        raise TimeoutError("Cannot find {}".format(card_name))
    for p in game.alive_players():
        main(p, player)
    return player, ids[0]
def assertPileCount(cards):
    # still in stack
    stack = cards.stack_len - cards.index
    logger.debug("There are {} cards in stack.".format(stack))
    # in rack
    rack = len(cards.rack_sorted_card_id)
    logger.debug("There are {} cards in rack.".format(rack))
    count = stack + rack
    # alive players
    for p in game.alive_players():
        hand = len(p.hand)
        in_game = len(p.in_game)
        logger.debug("There are {} cards in {} hand.".format(hand, p.id))
        logger.debug("There are {} cards in {} game.".format(in_game, p.id))
        count += hand + in_game
    logger.debug("Found {}/{} cards.".format(count, cards.nb_cards))
    assert count == cards.nb_cards


game = Bang(["Alain", "Bernard", "Charlie", "Dede"])

player = game.first_player
assert game.turn_step_draw(player.id)

player, card_id = findPlayerWith(player, "bang", True)
assert game.turn_step_play_card(player.id, card_id, player.get_right_player().id)
player, card_id = findPlayerWith(player, "bang")
assert not game.turn_step_play_card(player.id, card_id, player.get_right_player().id)
player = changePlayer(player) # force new player
player, card_id = findPlayerWith(player, "remington")
assert game.turn_step_play_card(player.id, card_id)
player, card_id = findPlayerWith(player, "bang", False, player)
assert game.turn_step_play_card(player.id, card_id, player.get_right_player().get_right_player().id)
player, card_id = findPlayerWith(player, "colt", False, player)
assert game.turn_step_play_card(player.id, card_id)

for p in game.alive_players():
    main(p, player)
assertPileCount(game.cards)
