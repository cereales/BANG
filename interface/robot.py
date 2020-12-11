import logging
logger = logging.getLogger(__name__)


class Robot:
    """
    Provides specific discord oriented tools to interact with discord users.
    """
    def __init__(self, client):
        self.client = client # bot account, virtual identity
