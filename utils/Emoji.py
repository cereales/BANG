import logging
logger = logging.getLogger(__name__)

import unicodedata as u


class EmojiDatabase:
    def __init__(self):
        logger.warning("Create EmojiDatabase")
        self.data = {
        "abort": [":no_entry_sign:", "\U0001f6ab"],
        "door": [":door:", "\U0001f6aa"],
        "draw": [":outbox_tray:", "\U0001f4e4"],
        "error": [":x:", "\u0078"],
        "next": [":next_track:", "\u23ed\ufe0f"],
        "play": [":arrow_forward:", "\u25b6\ufe0f"],
        "point_up": [":point_up:", "\U0001f446"],
        "remove_robot": [":rocket:", "\U0001f680"],
        "right_arrow": [":arrow_right:", "\u27a1\ufe0f"],
        "robot": [":robot:", "\U0001f916"],
        0: [":zero:", "\u0030"],
        1: [":one:", "\u0031\ufe0f\u20e3"],
        2: [":two:", "\u0032\ufe0f\u20e3"],
        3: [":three:", "\u0033\ufe0f\u20e3"],
        4: [":four:", "\u0034\ufe0f\u20e3"],
        5: [":five:", "\u0035\ufe0f\u20e3"],
        6: [":six:", "\u0036\ufe0f\u20e3"],
        7: [":seven:", "\u0037\ufe0f\u20e3"],
        8: [":eight:", "\u0038\ufe0f\u20e3"],
        9: [":nine:", "\u0039\ufe0f\u20e3"],
        10: [":keycap_ten:", "\U0001f51f"],
        "unknown": [":question:", "\u2753"]
        }
        self.aliases = {
        "add_robot": "robot",
        "discard": "abort",
        "unknown": "unknown"
        }

    def get_emoji(self, emoji_registered_name, data_index):
        if emoji_registered_name in self.data:
            try:
                return self.data[emoji_registered_name][data_index]
            except:
                pass
        elif emoji_registered_name in self.aliases:
            return self.get_emoji(self.aliases[emoji_registered_name], data_index)
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
