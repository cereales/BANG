import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from Bang import Bang, TurnStep

def main(player):
    logger.info("{}\t{}HP ({})".format(player.id, player.get_life(), player.role.name))
    for card in player.hand:
        logger.info("- {} ({})".format(card.symbol, card.name))
def changePlayer(player):
    assert game.turn_step_end(player.id)
    while not game.turn_step_next_player(player.id):
        assert game.turn_step_discard_card(player.id, player.hand[0].id)
    player = player.get_left_player()
    assert game.turn_step_draw(player.id)
    return player
def findPlayerWith(player, card_name, doubleCard=False):
    ids = [c.id for c in player.hand if c.name == card_name]
    while len(ids) <= doubleCard:
        player = changePlayer(player)
    for p in game.alive_players():
        main(p)
    return player, ids[0]


game = Bang(["Alain", "Bernard", "Charlie", "Dede"])

player = game.first_player
assert game.turn_step_draw(player.id)

player, card_id = findPlayerWith(player, "bang", True)
assert game.turn_step_play_card(player.id, card_id, player.get_right_player().id)
player, card_id = findPlayerWith(player, "bang")
assert not game.turn_step_play_card(player.id, card_id, player.get_right_player().id)

for p in game.alive_players():
    main(p)
"""
while game.current_turn_step != TurnStep.END_OF_GAME and compteur < 10:
    for p in game.alive_players():
        logger.info("[ {}\t{}HP ]".format(p.id, p.life))
    for p in game.players:
        logger.info("- {} <- {} ({}) -> {}".format(p.left_player.id, p.id, p.role.name, p.right_player.id))
    main(player)
    main(player)
    if game.current_turn_step == TurnStep.ACTION:
        assert game.turn_step_end(player.id)
        while not game.turn_step_next_player(player.id):
            assert game.turn_step_discard_card(player.id, player.hand[0].id)
        main(player)
        logger.info("pile {}".format(game.cards.sorted_card_id))
        logger.info("rack {}".format(game.cards.rack_sorted_card_id))

    compteur += 1
"""
