import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from Bang import Bang, TurnStep

def main(player):
    logger.info("Main {} {} {}HP".format(player.id, "*" if player.is_sherif() else "", player.get_life()))
    for card in player.hand:
        logger.info("- {} ({})".format(card.symbol, card.name))


game = Bang(["Alain", "Bernard", "Charlie", "Dede"])
for p in game.players:
    logger.info("- {} <- {} ({}) -> {}".format(p.left_player.id, p.id, p.role.name, p.right_player.id))
logger.info(game.roles.cards)
logger.info(game.roles.sorted_card_id)
logger.info(game.cards.cards)
logger.info(game.cards.sorted_card_id)
for p in game.players:
    main(p)
logger.info("pile {}".format(game.cards.sorted_card_id))
logger.info("rack {}".format(game.cards.rack_sorted_card_id))

player = game.first_player
compteur = 0
while game.current_turn_step != TurnStep.END_OF_GAME and compteur < 10:
    for p in game.alive_players():
        logger.info("[ {}\t{}HP ]".format(p.id, p.life))
    for p in game.players:
        logger.info("- {} <- {} ({}) -> {}".format(p.left_player.id, p.id, p.role.name, p.right_player.id))
    assert game.turn_step_draw(player.id)
    main(player)
    if (player.hand[0].name == "bang"):
        assert game.turn_step_play_card(player.id, player.hand[0].id, player.get_right_player().id)
        main(player)
    if game.current_turn_step == TurnStep.ACTION:
        assert game.turn_step_end(player.id)
        while not game.turn_step_next_player(player.id):
            assert game.turn_step_discard_card(player.id, player.hand[0].id)
        main(player)
        logger.info("pile {}".format(game.cards.sorted_card_id))
        logger.info("rack {}".format(game.cards.rack_sorted_card_id))

    player = player.get_left_player()
    compteur += 1
