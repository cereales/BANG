import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import json, re
from Card import Type


def attribute(card, key, value_type):
    assert key in card
    assert type(card[key]) == value_type
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
    for id, card in data.items(): # cannot check unique key
        value = attribute(card, "id", str)
        assert re.match(r"[0-9VDR][CSHD]$", value)
        value = attribute(card, "name", str)
        assert re.match(r"[a-z]+$", value)
        activation = attribute(card, "activation", int)
        effects = attribute(card, "effects", list)
        for effect in effects:
            value = attribute(effect, "id", int)
            if value == Type.WEAPON:
                value = attribute(effect, "weapon_range", int)
            value = attribute(effect, "range", int)
            value = attribute(effect, "targets", int)


## Check syntax for roles
with open("resources/characters.json") as file:
    data = json.load(file)
    for id, card in data.items():
        value = attribute(card, "name", str)
        value = attribute(card, "life", int)
