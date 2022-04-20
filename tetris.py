from __future__ import annotations
import enum
import random
from typing import List, Tuple, Set
from collections import deque

class PieceColor(enum.Enum):
    YELLOW = 93
    CYAN = 36
    PURPLE = 35
    ORANGE = 33
    BLUE = 34
    GREEN = 32
    RED = 31
    EMPTY = 0

    def ansi_code(color: int) -> str:
        return f"\033[{color}m"

class Rotation(enum.Enum):
    CW = 0
    CCW = 1

class PieceShape(object):
    def __init__(self, size: int, points: Set[Tuple[int, int]]):
        self.size = size
        self.points = points
    
    def print(self):
        for y in range(self.size):
            for x in range(self.size):
                if (x, y) in self.points:
                    print("*", end="")
                else:
                    print("-", end="")
            print()
    
    def rotate(self, rotation: Rotation) -> PieceShape:
        new_points = set()
        if rotation == Rotation.CCW:
            for point in self.points:
                new_points.add((point[1], self.size - 1 - point[0]))

            return PieceShape(self.size, new_points)

        elif rotation == Rotation.CW:
            # rotate counterclockwise
            for point in self.points:
                new_points.add((self.size - 1 - point[1], point[0]))
            
            return PieceShape(self.size, new_points)

class Piece(object):
    def __init__(self, color: PieceColor, shape: PieceShape, name: str = "No name"):
        self.color = color
        self.shape = shape
        self.name = name

    def print(self):
        print(PieceColor.ansi_code(self.color.value))
        self.shape.print()
    
    def rotate(self, rotation: Rotation):
        return Piece(self.color, self.shape.rotate(rotation), self.name)

default_pieces = {
    "O": Piece(PieceColor.YELLOW, PieceShape(2, {(0, 0), (0, 1), (1, 0), (1, 1)})),
    "I": Piece(PieceColor.CYAN, PieceShape(4, {(0, 2), (1, 2), (2, 2), (3, 2)})),
    "T": Piece(PieceColor.PURPLE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (1, 2)})),
    "L": Piece(PieceColor.ORANGE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (2, 2)})),
    "J": Piece(PieceColor.BLUE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (0, 2)})),
    "S": Piece(PieceColor.GREEN, PieceShape(3, {(0, 1), (1, 1), (1, 2), (2, 2)})),
    "Z": Piece(PieceColor.RED, PieceShape(3, {(0, 2), (1, 2), (1, 1), (2, 1)})),
}

for piece_name in default_pieces.keys():
    default_pieces[piece_name].name = piece_name

#represents only the matrix, not next pieces, swap pieces, current piece
class Board(object):
    def __init__(self):
        self.board = [[PieceColor.EMPTY] * 10 for _ in range(40)]

    def check_collision(self, piece: Piece, x: int, y: int) -> bool:
        for point in piece.shape.points:
            px = x + point[0]
            py = y + point[1]
            if px < 0 or px >= 10 or py < 0 or py >= 40:
                return True
            
            if self.board[py][px][0] != PieceColor.EMPTY:
                return True
        return False

    # places a piece; assumes piece is in a valid position (no collision and not floating)
    def freeze(self, piece:Piece, x: int, y:int):
        for point in piece.shape.points:
            px = x + point[0]
            py = y + point[1]
            self.board[py][px] = piece.color

class Game(object):
    def __init__(self):
        self.board = Board()
        self.bag = deque()
        self._refill_bag()

        self.set_curr_piece(self._next_piece())

        self.swap_piece = None
        self.game_over = False
    
    def _refill_bag(self):
        while len(self.bag) <= len(default_pieces.keys()):
            self.bag.append(random.shuffle(list(default_pieces.values())))
    
    def _next_piece(self) -> Piece:
        self._refill_bag()
        return self.bag.popleft()

    def _set_curr_piece(self, piece: Piece):
        self.curr_piece = piece
        self.curr_piece_x = 5 - (piece.size + 1) // 2
        self.curr_piece_y = 20 if piece.size == 2 else 19

        if self.board.check_collision(self.curr_piece, self.curr_piece_x, self.curr_piece_y):
            self.game_over = True

for piece in default_pieces.values():
    piece.rotate(Rotation.CCW).print()
    piece.print()