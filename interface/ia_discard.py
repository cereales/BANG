import logging, utils.Tools as Tools
logger = logging.getLogger(__name__)


class IADiscard:
    def __init__(self, player_id):
        self.display_name = player_id
        self.id = player_id

    def turn_step_draw(self, game):
        assert game.turn_step_draw(self.id)
        for card in game.current_player.hand:
            logger.info("- {} ({}) id={}".format(card.symbol, card.name, card.id))

    def turn_step_play_card(self, game):
        assert game.turn_step_end(self.id)

    async def turn_step_end(self, game, robot):
        while not game.turn_step_next_player(self.id):
            await robot.add_discard_message(self.id, game.current_player.hand[0])
            assert game.turn_step_discard_card(self.id, game.current_player.hand[0].id)
