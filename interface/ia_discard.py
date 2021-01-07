import logging, utils.Tools as Tools
logger = logging.getLogger(__name__)


class IADiscard:
    def __init__(self, player_id):
        self.display_name = player_id
