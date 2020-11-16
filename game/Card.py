import logging
logger = logging.getLogger(__name__)


class Type:
    DAMAGE = 0
    # HEAL = 1
    # MISS = 2
    # DRAW = 3
    # DISCARD = 4

class Range:
    CASTER = 0
    IN_RANGE = 1
    IN_RANGE_CUSTO = 2
    NO_RANGE = 3
    ALL_OTHERS = 4

class Target:
    CASTER = 1
    SHERIF = 2
    OTHERS_EXCEPT_SHERIF = 4

class ExecuteEffect:
    FAIL = 0
    IS_SUCCESS = 1
    MAKE_DEAD = 2


class Card:
    def __init__(self, id, symbol, name, effects):
        self.id = id
        self.symbol = symbol
        self.name = name
        self.effects = effects

    def execute(self, player, target_player=None, target_card=None):
        logger.debug('Play {} "{}" id={}'.format(self.symbol, self.name, self.id))
        # limit to one bang per turn
        if self.name == "bang":
            if player.nb_bang_used > 0:
                logger.error("Reached limit of 1 bang per turn.")
                return ExecuteEffect.FAIL
            player.nb_bang_used += 1

        logger.debug("Using effects {}".format(self.effects))
        execution_result = ExecuteEffect.FAIL
        for effect in self.effects:
            local_target_players = [target_player]
            targets = effect["targets"]

            range_type = effect["range"]
            if (range_type == Range.CASTER):
                local_target_players = [player]
            if (range_type == Range.IN_RANGE) and (target_player is None or not player.has_in_range(target_player)):
                logger.error("Cannot target {} because he is not in range (or inexistant).".format(target_player.id if target_player is not None else None))
                return ExecuteEffect.FAIL
            if (range_type == Range.IN_RANGE_CUSTO) and (target_player is None or not player.has_in_range(target_player, effect["max_range"])):
                logger.error("Cannot target {} because he is not in range {} (or inexistant).".format(target_player.id if target_player is not None else None, effect["max_range"]))
                return ExecuteEffect.FAIL
            if (range_type == Range.ALL_OTHERS):
                local_target_players = []
                local_player = player.get_left_player()
                while local_player != player:
                    if can_affect(local_player, targets, player):
                        local_target_players.append(local_player)
                    local_player = local_player.get_left_player()
            logger.debug("Try to shoot to {}".format([p.id for p in local_target_players]))

            if len(local_target_players) == 0:
                logger.error("Nobody to target to.")
                return ExecuteEffect.FAIL
            for local_player in local_target_players:
                if not can_affect(local_player, targets, player):
                    return ExecuteEffect.FAIL

            # here targets have been checked
            type = effect["id"]
            for local_player in local_target_players:
                if type == Type.DAMAGE:
                    execution_result |= local_player.lose_health(player) & ExecuteEffect.MAKE_DEAD
        return execution_result | ExecuteEffect.IS_SUCCESS


def can_affect(player, targets, caster):
    if not (targets & Target.CASTER) and player == caster:
        logger.warning("Cannot affect caster.")
        return False
    if not (targets & Target.SHERIF) and player.is_sherif():
        logger.warning("Cannot affect sherif.")
        return False
    if not (targets & Target.OTHERS_EXCEPT_SHERIF) and not (player.is_sherif() or player == caster):
        logger.warning("Cannot affect {}.".format(player.id))
        return False
    return True
