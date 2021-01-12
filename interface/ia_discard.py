import logging, utils.Tools as Tools
logger = logging.getLogger(__name__)


class IADiscard:
    def __init__(self, player_id, robot):
        self.display_name = player_id
        self.id = player_id
        self.action = robot

    async def main(self, game): # TEMP: game is temporary. Must have defined methods in robot -> game
        assert await self.action.turn_step_draw(self.id)
        for card in game.current_player.hand:
            logger.info("- {} ({}) id={}".format(card.symbol, card.name, card.id))
        assert await self.action.turn_step_end(self.id)
        while not game.turn_step_next_player(self.id):
            assert await self.action.turn_step_discard_card(self.id, 0)
        await self.action.send_next_player(game.current_player.id)
