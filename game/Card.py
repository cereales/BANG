import logging
logger = logging.getLogger(__name__)


class Activation:
    ONCE = 1 # brown/blue edge card
    REACT = 2 # can be played during other's turn as reaction


class Type:
    DAMAGE = 0
    # HEAL = 1
    MISS = 2
    # DRAW = 3
    # DISCARD = 4
    WEAPON = 5
    # MAGASIN = 6
    # INDIENS = 7
    # DUEL = 8
    # MUSTANG = 9
    # LUNETTE = 10
    # PLANQUE = 11
    # PRISON = 12
    # DYNAMITE = 13
    # UNLIMITED_BANG = 14
    # DRAW_FIRST_IN_HAND = 15
    # DRAW_FIRST_IN_RACK = 23
    # DRAW_MORE_ON_SECOND_RED = 16
    # DRAW_CHOOSE_OVER_THREE = 17
    # DRAW_ON_EMPTY_HAND = 24
    # DRAW_ON_DAMAGE = 25
    # DRAW_IN_HAND_ON_DAMAGE = 26
    # BANG_IS_MISS = 20
    # DOUBLE_MISS = 19
    # DEGAINE_CHOOSE_OVER_TWO = 21
    # DISCARD_TWO_TO_HEAL = 22
    # STILL_CARDS_ON_DEATH = 18

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
    def __init__(self, id, symbol, name, activation, effects):
        self.id = id
        self.symbol = symbol
        self.name = name
        self.activation = activation
        self.effects = effects

    def get_id(self):
        return self.id

    def is_type_card_immediate(self):
        return self.activation & Activation.ONCE
    def is_type_card_react(self):
        return self.activation & Activation.REACT
    def get_weapon_range(self):
        assert self.effects[0]["id"] == Type.WEAPON
        return self.effects[0]["weapon_range"]

    def possible_targets(self, player, target_player=None, target_card=None):
        """
        Run a check on targets of card.
        Returns a list of targeted player id for each effect of the card :
            [targets_effect1, targets_effect2, ...]
            with targets_effectI : [player_id1, player_id2, ...]
        Returns None on error.
        """
        logger.debug('Play {} "{}" id={}'.format(self.symbol, self.name, self.id))
        # limit to one bang per turn
        if self.name == "bang":
            if player.nb_bang_used > 0:
                logger.error("Reached limit of 1 bang per turn.")
                return None

        logger.debug("Checking effects {}".format(self.effects))
        target_players = []
        for effect in self.effects:
            local_target_players = [target_player]
            targets = effect["targets"]

            range_type = effect["range"]
            if (range_type == Range.CASTER):
                local_target_players = [player]
            if (range_type == Range.IN_RANGE) and (target_player is None or not player.has_in_range(target_player)):
                logger.error("Cannot target {} because he is not in range (or inexistant).".format(target_player.id if target_player is not None else None))
                return None
            if (range_type == Range.IN_RANGE_CUSTO) and (target_player is None or not player.has_in_range(target_player, effect["max_range"])):
                logger.error("Cannot target {} because he is not in range {} (or inexistant).".format(target_player.id if target_player is not None else None, effect["max_range"]))
                return None
            if (range_type == Range.ALL_OTHERS):
                local_target_players = []
                local_player = player.get_left_player()
                while local_player != player:
                    if can_affect(local_player, targets, player):
                        local_target_players.append(local_player)
                    local_player = local_player.get_left_player()
            logger.debug("Try to use on {}".format([p.id for p in local_target_players]))

            if len(local_target_players) == 0:
                logger.error("Nobody to target to.")
                return None
            for local_player in local_target_players:
                if not can_affect(local_player, targets, player):
                    return None
            target_players.append(local_target_players)
        logger.debug("Targets are {}".format([[p.id for p in t] for t in target_players]))
        return target_players

    def execute(self, p_stack, player, target_player=None, target_card=None, in_reaction_to=None):
        """
        Run a check on given targets, then execute effects of card.
        For brown card and reactions.
        Returns execution status of type ExecuteEffect.
        """
        execution_result = ExecuteEffect.FAIL
        # Check type reaction
        if in_reaction_to and not self.is_type_card_react():
            logger.error("Cannot play in reaction a card that is not of type REACT.")
            return ExecuteEffect.FAIL
        # Check targets
        targets_by_effect = self.possible_targets(player, target_player, target_card)
        if targets_by_effect is None:
            return ExecuteEffect.FAIL
        # limit to one bang per turn
        if self.name == "bang":
            player.nb_bang_used += 1

        # Execute effects
        for effect, local_target_players in zip(self.effects, targets_by_effect):
            type = effect["id"]
            for local_player in local_target_players:
                if type == Type.DAMAGE:
                    execution_result |= local_player.lose_health(p_stack, player)
                if type == Type.MISS:
                    if in_reaction_to:
                        react_to_damage = False
                        for react_to_effect in in_reaction_to.effects:
                            if react_to_effect["id"] == Type.DAMAGE:
                                react_to_damage = True
                        if react_to_damage:
                            execution_result |= ExecuteEffect.IS_SUCCESS
        return execution_result # return fail if nothing to do

    def apply_effects(self, p_stack, player, target_player=None, target_card=None):
        """
        Run a check on given targets, then wear card to the player targeted by 1st effect.
        For blue card.
        Returns execution status of type ExecuteEffect.
        """
        # Check targets
        execution_result = ExecuteEffect.FAIL
        targets_by_effect = self.possible_targets(player, target_player, target_card)
        if targets_by_effect is None:
            return ExecuteEffect.FAIL, None

        # Wear card
        player_with_card_in_game = None
        for effect, local_target_players in zip(self.effects, targets_by_effect):
            type = effect["id"]
            for local_player in local_target_players:
                if player_with_card_in_game is None:
                    # Only target of the 1st effect wears the card
                    assert len(local_target_players) == 1
                    player_with_card_in_game = local_player
                    if local_player.has_card_in_game(self.name):
                        logger.error("Player {} already has card {} in game.".format(local_player.id, self.name))
                        return ExecuteEffect.FAIL, None

                if type == Type.WEAPON:
                    local_player.set_weapon(self, p_stack)
                    execution_result |= ExecuteEffect.IS_SUCCESS

        return execution_result, player_with_card_in_game


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
