from __future__ import annotations
import random
from collections import deque

from piece import Rotation, PieceColor, Piece, DEFAULT_PIECES
from wallkick import get_wallkicks

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
    
    def clear_lines(self) -> int:
        lines_cleared = 0
        for y in range(40):
            if all(self.board[y][x][0] != PieceColor.EMPTY for x in range(10)):
                for y2 in range(y, 0, -1):
                    self.board[y2] = self.board[y2 - 1]
                self.board[0] = [PieceColor.EMPTY] * 10
                lines_cleared += 1
        return lines_cleared

class Game(object):
    def __init__(self):
        self.board = Board()
        self.bag = deque()
        self._refill_bag()

        self.set_curr_piece(self._next_piece())

        self.swap_piece = None
        self.game_over = False
    
    def _refill_bag(self):
        while len(self.bag) <= len(DEFAULT_PIECES.keys()):
            self.bag.append(random.shuffle(list(DEFAULT_PIECES.values())))
    
    def _next_piece(self) -> Piece:
        self._refill_bag()
        return self.bag.popleft()

    # spawns the current piece at the top of the board
    def _set_curr_piece(self, piece: Piece):
        self.curr_piece = piece
        self.curr_piece_x = 5 - (piece.size + 1) // 2
        self.curr_piece_y = 20 if piece.size == 2 else 19
        self.curr_piece_rotation = 0

        if self.board.check_collision(self.curr_piece, self.curr_piece_x, self.curr_piece_y):
            self.game_over = True
    
    def rotate(self, rotation: Rotation) -> bool:
        if self.game_over:
            print("game over")
            return False

        wallkicks = get_wallkicks(self.curr_piece.shape, rotation, self.curr_piece_rotation)
        
        new_piece = self.curr_piece.rotate(rotation)
        new_rotation = (self.curr_piece_rotation + 4 + rotation.value) % 4
        
        for wallkick in wallkicks[new_rotation]:
            if not self.board.check_collision(new_piece, self.curr_piece_x + wallkick[0], self.curr_piece_y + wallkick[1]):
                self.curr_piece_x += wallkick[0]
                self.curr_piece_y += wallkick[1]
                self.curr_piece_rotation = new_rotation
                self.curr_piece = new_piece
                return True

        return False
    
    def move(self, dx: int, dy:int) -> bool:
        if self.game_over:
            print("game over")
            return False

        if not self.board.check_collision(self.curr_piece, self.curr_piece_x + dx, self.curr_piece_y + dy):
            self.curr_piece_x += dx
            self.curr_piece_y += dy
            return True
        return False
    
    def hard_drop(self):
        while self.move(0, 1):
            pass

        self.board.freeze(self.curr_piece, self.curr_piece_x, self.curr_piece_y)
        self.board.clear_lines()
        self.set_curr_piece(self._next_piece())

for piece in DEFAULT_PIECES.values():
    piece.rotate(Rotation.CCW).print()
    piece.print()