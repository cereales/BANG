import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from game.Bang import Bang, TurnStep

def main(player, current):
    logger.info("{}\t{}HP ({})  {} {}".format(player.id, player.get_life(), player.role.name, [c.name for c in player.in_game], "<--" if current == player else ""))
    for card in player.hand:
        logger.info("- {} ({})".format(card.symbol, card.name))
def changePlayer(player, prefered_card_id_to_discard=None, prefered_card_id_to_keep=None):
    logger.debug("Switching player...")
    assert not (prefered_card_id_to_discard and prefered_card_id_to_keep) # cannot discard and keep simultaneous
    assert game.turn_step_end(player.id) or player.is_dead()
    if game.current_turn_step == TurnStep.DISCARD:
        while not game.turn_step_next_player(player.id):
            if prefered_card_id_to_discard is not None:
                assert game.turn_step_discard_card(player.id, prefered_card_id_to_discard)
                prefered_card_id_to_discard = None
            elif prefered_card_id_to_keep is not None:
                assert game.turn_step_discard_card(player.id, player.hand[0].id if prefered_card_id_to_keep != player.hand[0].id else player.hand[1].id)
            else:
                assert game.turn_step_discard_card(player.id, player.hand[0].id)
    player = player.get_left_player()
    assert game.turn_step_draw(player.id)
    return player
def findPlayerWith(player, card_name, doubleCard=False, forcePlayer=None, prefered_card_id_to_keep=None, timeout=30):
    logger.debug("Looking for '{}' card.".format(card_name))
    ids = [c.id for c in player.hand if c.name == card_name]
    while (len(ids) <= doubleCard or (forcePlayer is not None and forcePlayer != player)) and timeout > 0:
        logger.warning("{} matchs ; playerForced={} ; player={}\ttimeout={}".format(len(ids), forcePlayer.id if forcePlayer is not None else None, player.id, timeout))
        if len(ids) > 0: # meaning player is forced and not on the current one
            logger.debug("Opti: Discard targeted card.")
            player = changePlayer(player, ids[0])
        else:
            player = changePlayer(player, prefered_card_id_to_keep=prefered_card_id_to_keep)
        ids = [c.id for c in player.hand if c.name == card_name]
        timeout -= 1
    logger.warning("{} matchs ; playerForced={} ; player={}\ttimeout={}".format(len(ids), forcePlayer.id if forcePlayer is not None else None, player.id, timeout))
    logger.warning("{} and ({} or {})".format(len(ids) > doubleCard, forcePlayer is None, forcePlayer == player))
    if timeout <= 0:
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
def playCard(player_id, card_id, target_player=None, target_card=None):
    res = game.turn_step_play_card(player_id, card_id, target_player, target_card)
    assert game.turn_step_dont_react(target_player) or targetedSelf(game.players_id[player_id])
    return res
def targetedSelf(player):
    return game.next_react_players[0] == player and game.turn_step_dont_react(player.id)


game = Bang(["Alain", "Bernard", "Charlie", "Dede"])

player = game.first_player
assert game.turn_step_draw(player.id)

player, card_id = findPlayerWith(player, "bang", doubleCard=True) # force double card to avoid turn change
assert playCard(player.id, card_id, player.get_right_player().id)
player, card_id = findPlayerWith(player, "bang") # don't need to force player thanks to previous double card
assert not game.turn_step_play_card(player.id, card_id, player.get_right_player().id)
player = changePlayer(player) # force new player
player, card_id = findPlayerWith(player, "remington")
assert game.turn_step_play_card(player.id, card_id)
player, card_id = findPlayerWith(player, "bang", forcePlayer=player)
assert playCard(player.id, card_id, player.get_right_player().get_right_player().id)
player, card_id = findPlayerWith(player, "colt", forcePlayer=player)
assert game.turn_step_play_card(player.id, card_id)
miss_player, miss_card_id = findPlayerWith(player, "rate")
player = changePlayer(miss_player, prefered_card_id_to_keep=miss_card_id) # force new player
player, card_id = findPlayerWith(player, "bang", forcePlayer=player, prefered_card_id_to_keep=miss_card_id)
assert miss_card_id in [c.id for c in miss_player.hand]
assert game.turn_step_play_card(player.id, card_id, miss_player.id)
assert game.turn_step_react_play_card(miss_player.id, miss_card_id) or targetedSelf(game.players_id[player.id])

for p in game.alive_players():
    main(p, player)
assertPileCount(game.cards)
