import logging
logger = logging.getLogger(__name__)

import unicodedata as u


class EmojiDatabase:
    def __init__(self):
        logger.warning("Create EmojiDatabase")
        self.data = {
        "abort": [":no_entry_sign:", "\U0001f6ab"],
        "door": [":door:", "\U0001f6aa"],
        "play": [":arrow_forward:", "\u25b6\ufe0f"],
        "point_up": [":point_up:", "\U0001f446"],
        0: [":zero:"],
        1: [":one:"],
        2: [":two:"],
        3: [":three:"],
        4: [":four:"],
        5: [":five:"],
        6: [":six:"],
        7: [":seven:"],
        8: [":eight:"],
        9: [":nine:"],
        10: [":ten:"],
        "unknown": [":question:", "\u2753"]
        }
        self.aliases = {
        "discard": "abort",
        "unknown": "unknown"
        }

    def get_emoji(self, emoji_registered_name, data_index):
        if emoji_registered_name in self.data:
            try:
                return self.data[emoji_registered_name][data_index]
            except:
                pass
        logger.warning("Emoji {} is not known.".format(emoji_registered_name))
        return self.data["unknown"][data_index]

    def equals(self, emoji_registered_name, emoji_code):
        if emoji_registered_name in self.data:
            if emoji_code == self.data[emoji_registered_name][0]:
                logger.debug("Emoji matches '{}'.".format(emoji_registered_name))
                return True
            if len(self.data[emoji_registered_name]) < 2:
                return False
            unicode = self.data[emoji_registered_name][1]
            if u.normalize("NFD", u.normalize("NFD", emoji_code).casefold()) == u.normalize("NFD", u.normalize("NFD", unicode).casefold()):
                logger.debug("Emoji matches '{}'.".format(emoji_registered_name))
                return True
            return False
        elif emoji_registered_name in self.aliases:
            return self.equals(self.aliases[emoji_registered_name], emoji_code)
        else:
            logger.warning("Emoji {} is not known.".format(emoji_registered_name))
            return False


class Emoji:
    data = EmojiDatabase()

    @staticmethod
    def get_unicode_emoji(emoji_registered_name):
        return Emoji.data.get_emoji(emoji_registered_name, 1)

    @staticmethod
    def get_discord_emoji(emoji_registered_name):
        return Emoji.data.get_emoji(emoji_registered_name, 0)

    @staticmethod
    def equals(emoji_registered_name, emoji_code):
        return Emoji.data.equals(emoji_registered_name, emoji_code)
