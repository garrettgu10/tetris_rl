from __future__ import annotations
import enum
from typing import Tuple, Set

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

DEFAULT_PIECES = {
    "O": Piece(PieceColor.YELLOW, PieceShape(2, {(0, 0), (0, 1), (1, 0), (1, 1)})),
    "I": Piece(PieceColor.CYAN, PieceShape(4, {(0, 2), (1, 2), (2, 2), (3, 2)})),
    "T": Piece(PieceColor.PURPLE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (1, 2)})),
    "L": Piece(PieceColor.ORANGE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (2, 2)})),
    "J": Piece(PieceColor.BLUE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (0, 2)})),
    "S": Piece(PieceColor.GREEN, PieceShape(3, {(0, 1), (1, 1), (1, 2), (2, 2)})),
    "Z": Piece(PieceColor.RED, PieceShape(3, {(0, 2), (1, 2), (1, 1), (2, 1)})),
}

for piece_name in DEFAULT_PIECES.keys():
    DEFAULT_PIECES[piece_name].name = piece_name
