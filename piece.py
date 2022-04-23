from __future__ import annotations
import enum
from typing import Tuple, Set

class PieceColor(enum.Enum):
    YELLOW = 7
    CYAN = 6
    PURPLE = 5
    ORANGE = 4
    BLUE = 3
    GREEN = 2
    RED = 1
    EMPTY = 0

    def ansi_code(color: PieceColor) -> str:
        return {
            PieceColor.YELLOW: '\033[93m',
            PieceColor.CYAN: '\033[36m',
            PieceColor.PURPLE: '\033[35m',
            PieceColor.ORANGE: '\033[33m',
            PieceColor.BLUE: '\033[34m',
            PieceColor.GREEN: '\033[32m',
            PieceColor.RED: '\033[31m',
            PieceColor.EMPTY: '\033[0m'
        }[color]

class Rotation(enum.Enum):
    CW = 1
    CCW = -1

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
        if rotation == Rotation.CW:
            for point in self.points:
                new_points.add((point[1], self.size - 1 - point[0]))

            return PieceShape(self.size, new_points)

        elif rotation == Rotation.CCW:
            for point in self.points:
                new_points.add((self.size - 1 - point[1], point[0]))
            
            return PieceShape(self.size, new_points)

class Piece(object):
    def __init__(self, color: PieceColor, shape: PieceShape, name: str = "No name", original_orientation = None):
        self.color = color
        self.shape = shape
        self.name = name
        if original_orientation == None:
            self.original_orientation = self
        else:
            self.original_orientation = original_orientation

    def print(self):
        print(PieceColor.ansi_code(self.color.value))
        self.shape.print()
    
    def rotate(self, rotation: Rotation):
        return Piece(self.color, self.shape.rotate(rotation), self.name, self.original_orientation)

DEFAULT_PIECES = {
    "O": Piece(PieceColor.YELLOW, PieceShape(2, {(0, 0), (0, 1), (1, 0), (1, 1)})),
    "I": Piece(PieceColor.CYAN, PieceShape(4, {(0, 2), (1, 2), (2, 2), (3, 2)})),
    "T": Piece(PieceColor.PURPLE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (1, 2)})),
    "L": Piece(PieceColor.ORANGE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (2, 2)})),
    "J": Piece(PieceColor.BLUE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (0, 2)})),
    "S": Piece(PieceColor.GREEN, PieceShape(3, {(0, 1), (1, 1), (1, 2), (2, 2)})),
    "Z": Piece(PieceColor.RED, PieceShape(3, {(0, 2), (1, 2), (1, 1), (2, 1)})),
}

DEFAULT_PIECES_BY_COLOR = {}

for piece_name in DEFAULT_PIECES.keys():
    DEFAULT_PIECES[piece_name].name = piece_name

for piece_name in DEFAULT_PIECES.keys():
    DEFAULT_PIECES_BY_COLOR[DEFAULT_PIECES[piece_name].color] = DEFAULT_PIECES[piece_name]