import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import json, re
from game.Card import Type, Range


def attribute(card, key, value_type):
    assert key in card, "Missing attribute '{}' on card {}.".format(key, card)
    assert type(card[key]) == value_type, "Value of attribute '{}' is not of expected type <{}> : {}".format(key, value_type, card)
    return card[key]


## Check syntax for roles
with open("resources/roles.json") as file:
    data = json.load(file)
    for id, card in data.items():
        value = attribute(card, "name", str)
        value = attribute(card, "desc", str)


## Check syntax for cards
with open("resources/cards.json") as file:
    data = json.load(file)
    db = {"C": 0, "H": 0, "S": 0, "D": 0}
    for id, card in data.items(): # cannot check unique key
        value = attribute(card, "id", str)
        assert re.match(r"[0-9VDR][CSHD]$", value), "Error with value '{}' of attribute '{}' of card : {}".format(value, "id", card)
        db[value[1]] += 1
        value = attribute(card, "name", str)
        assert re.match(r"[a-z ]+$", value), "Error with value '{}' of attribute '{}' of card : {}".format(value, "name", card)
        activation = attribute(card, "activation", int)
        effects = attribute(card, "effects", list)
        for effect in effects:
            value = attribute(effect, "id", int)
            if value == Type.WEAPON:
                value = attribute(effect, "weapon_range", int)
            value = attribute(effect, "range", int)
            if value == Range.IN_RANGE_CUSTO:
                value = attribute(effect, "max_range", int)
            value = attribute(effect, "targets", int)
    logger.info(db)


## Check syntax for roles
with open("resources/characters.json") as file:
    data = json.load(file)
    for id, card in data.items():
        value = attribute(card, "name", str)
        assert re.match(r"[A-Z][a-zA-Z ]+$", value), "Error with name value '{}' of character : {}".format(value, card)
        value = attribute(card, "life", int)
        effects = attribute(card, "effect", int)
        value = attribute(card, "desc", str)
