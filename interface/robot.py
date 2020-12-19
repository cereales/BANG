import logging
logger = logging.getLogger(__name__)


class Robot:
    """
    Provides specific discord oriented tools to interact with discord users.
    """
    def __init__(self, client, channel):
        self.client = client # bot account, virtual identity
        self.channel = channel # place of the game instance
        self.message = None # previous message from bot

    async def send(self, message_content):
        """
        Send a new message.
        """
        self.message = await self.channel.send(message_content)

    async def refresh(self, message_content):
        """
        Change previous sent message with new content.
        """
        if self.message is not None:
            await self.message.edit(content=message_content)
        else:
            await self.send(message_content)

    async def add(self, sub_message):
        """
        Add content to existing message, keeping old part.
        """
        if self.message is not None:
            await self.message.edit(content=self.message.content + '\n' + sub_message)
        else:
            await self.send(sub_message)

    def forget(self):
        """
        Cut out link to sent message.
        """
        self.message = None
