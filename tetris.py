import enum
from typing import List, Tuple, Set

class PieceColor(enum.Enum):
    YELLOW = 93
    CYAN = 36
    PURPLE = 35
    ORANGE = 33
    BLUE = 34
    GREEN = 32
    RED = 31

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
    
    def rotate(self, rotation: Rotation):
        new_points = set()
        if rotation == Rotation.CW:
            # rotate clockwise
            for point in self.points:
                new_points.add((point[1], self.size - 1 - point[0]))

            return PieceShape(self.size, new_points)

        elif rotation == Rotation.CCW:
            # rotate counterclockwise
            for point in self.points:
                new_points.add((self.size - 1 - point[1], point[0]))
            
            return PieceShape(self.size, new_points)

class PieceType(object):
    def __init__(self, color: PieceColor, shape: PieceShape):
        self.color = color
        self.shape = shape

    def print(self):
        print(PieceColor.ansi_code(self.color.value))
        self.shape.print()

pieces = [
    PieceType(PieceColor.YELLOW, PieceShape(2, {(0, 0), (0, 1), (1, 0), (1, 1)})),
    PieceType(PieceColor.CYAN, PieceShape(4, {(0, 2), (1, 2), (2, 2), (3, 2)})),
    PieceType(PieceColor.PURPLE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (1, 2)})),
    PieceType(PieceColor.ORANGE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (2, 2)})),
    PieceType(PieceColor.BLUE, PieceShape(3, {(0, 1), (1, 1), (2, 1), (0, 2)})),
    PieceType(PieceColor.GREEN, PieceShape(3, {(0, 1), (1, 1), (1, 2), (2, 2)})),
    PieceType(PieceColor.RED, PieceShape(3, {(0, 2), (1, 2), (1, 1), (2, 1)})),
]

for piece in pieces:
    piece.print()