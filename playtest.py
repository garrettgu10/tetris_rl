from tetris import Game
from piece import Rotation
from gym_env import game_to_observation
from heuristic import AggregateHeightScorer, BumpinessScorer, CompleteLinesScorer, HolesScorer

game = Game()
while not game.game_over:
    game.print_game_state()
    observation = game_to_observation(game)

    print(AggregateHeightScorer().score(observation))
    print(CompleteLinesScorer().score(observation))
    print(HolesScorer().score(observation))
    print(BumpinessScorer().score(observation))

    for position in game.board.find_possible_positions(game.curr_piece, game.curr_piece_x, game.curr_piece_y, game.curr_piece_rotation):
        game.set_curr_position(position[0], position[1], position[2])
        game.print_game_state()

    cmd = input("Command: ")
    if cmd == "c":
        game.swap()
    elif cmd == "a":
        game.move(-1, 0)
    elif cmd == "s":
        game.move(0, -1)
    elif cmd == "d":
        game.move(1, 0)
    elif cmd == "z":
        game.rotate(Rotation.CCW)
    elif cmd == "x" or cmd == "w":
        game.rotate(Rotation.CW)
    elif cmd == " ":
        game.hard_drop()