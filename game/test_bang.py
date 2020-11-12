
from Bang import Bang

def main(player):
    print("Main", player.id)
    for card in player.hand:
        print("-", card.id)


game = Bang(["Alain", "Bernard", "Charlie", "Dede"])
for p in game.players:
    print("-", p.left_player.id, "<-", p.id, "({})".format(p.role.name), "->", p.right_player.id)
print(game.roles.cards)
print(game.roles.sorted_card_id)
print(game.cards.cards)
print(game.cards.sorted_card_id)
for p in game.players:
    main(p)
print(game.cards.sorted_card_id)
print(game.cards.rack_sorted_card_id)

player = game.first_player
for _ in range(5):
    assert game.turn_step_draw(player.id)
    main(player)
    assert game.turn_step_play_card(player.id, player.hand[0].id)
    main(player)
    assert game.turn_step_end(player.id)
    assert not game.turn_step_next_player(player.id)
    assert game.turn_step_discard_card(player.id, player.hand[0].id)
    assert game.turn_step_next_player(player.id)
    main(player)
    print("pile", game.cards.sorted_card_id)
    print("rack", game.cards.rack_sorted_card_id)

    player = player.get_left_player()
