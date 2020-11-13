import logging
logger = logging.getLogger(__name__)


class Type:
    DAMAGE = 0
    # HEAL = 1
    # MISS = 2
    # DRAW = 3
    # DISCARD = 4

class Range:
    # CASTER = 0
    IN_RANGE = 1
    # IN_RANGE_CUSTO = 2
    # NO_RANGE = 3
    # OTHERS = 4

class Target:
    # CASTER = 1
    SHERIF = 2
    # OTHERS = 4


class Card:
    def __init__(self, id, name, effects):
        self.id = id
        self.name = name
        self.effects = effects

    def execute(self, player, target_player=None, target_card=None):
        for effect in self.effects:
            range_type = effect["range"]
            if (range_type & Range.IN_RANGE) and (target_player is None or not player.has_in_range(target_player)):
                logger.error("Cannot target {} because he is not in range (or inexistant).".format(target_player.id if target_player is not None else None))
                return False
            targets = effect["targets"]
            # if not (targets & Target.CASTER) and target_player == player:
            #     return False
            # if not (targets & Target.SHERIF) and target_player.is_sherif():
            #     return False
            # here targets have been checked
            type = effect["id"]
            if type == Type.DAMAGE:
                if range_type & Range.IN_RANGE:
                    target_player.lose_health()
        return True
