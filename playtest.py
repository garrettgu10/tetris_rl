from tetris import Game
from piece import Rotation

game = Game()
while not game.game_over:
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