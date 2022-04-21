
from typing import List, Tuple
from piece import Rotation, Piece

class WallKick(object):
    def __init__(self, 
        cw_offsets: List[List[Tuple[int, int]]],
        ccw_offsets: List[List[Tuple[int, int]]]):
        self.cw_offsets = cw_offsets
        self.ccw_offsets = ccw_offsets

NORMAL_WALLKICK = WallKick(
    [
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, -2)]
    ],
    [
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)]
    ]
)

I_WALLKICK = WallKick(
    [
        [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)]
    ],
    [
        [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)]
    ]
)

def get_wallkicks(piece: Piece, direction: Rotation, old_rotation: int) -> List[Tuple[int, int]]:
    if piece.shape.size == 4:
        if direction == Rotation.CW:
            return I_WALLKICK.cw_offsets[old_rotation]
        elif direction == Rotation.CCW:
            return I_WALLKICK.ccw_offsets[old_rotation]
    else:
        if direction == Rotation.CW:
            return NORMAL_WALLKICK.cw_offsets[old_rotation]
        elif direction == Rotation.CCW:
            return NORMAL_WALLKICK.ccw_offsets[old_rotation]