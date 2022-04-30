import random
from collections import deque

from piece import Rotation, PieceColor, Piece, DEFAULT_PIECES
from scorer import Scorer
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
            
            if self.board[py][px] != PieceColor.EMPTY:
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
        for y in range(39, -1, -1):
            if all(self.board[y][x] != PieceColor.EMPTY for x in range(10)):
                for y2 in range(y, 39):
                    self.board[y2] = self.board[y2 + 1]
                self.board[39] = [PieceColor.EMPTY] * 10
                lines_cleared += 1
        return lines_cleared
    
    def is_empty(self):
        return all(self.board[y][x] == PieceColor.EMPTY for x in range(10) for y in range(40))

class Game(object):
    def __init__(self, scorer = Scorer(), seed = random.random()):
        if seed == None:
            seed = random.random()
        self.random = random.Random(seed)

        self.board = Board()
        self.bag = deque()
        self._refill_bag()

        self._set_curr_piece(self._next_piece())

        self.swap_piece = None
        self.can_swap = True
        self.game_over = False

        if scorer == None:
            scorer = Scorer()
        self.scorer = scorer
    
    def _refill_bag(self):
        while len(self.bag) <= len(DEFAULT_PIECES.keys()):
            new_bag = list(DEFAULT_PIECES.values())
            self.random.shuffle(new_bag)
            self.bag.extend(new_bag)
    
    def _next_piece(self) -> Piece:
        self._refill_bag()
        return self.bag.popleft()

    # spawns the current piece at the top of the board
    def _set_curr_piece(self, piece: Piece):
        self.curr_piece = piece
        self.curr_piece_x = 5 - (piece.shape.size + 1) // 2
        self.curr_piece_y = 18 if piece.shape.size == 2 else 17
        self.curr_piece_rotation = 0

        if self.board.check_collision(self.curr_piece, self.curr_piece_x, self.curr_piece_y):
            self.game_over = True
    
    def rotate(self, rotation: Rotation) -> bool:
        if self.game_over:
            print("game over")
            return False

        wallkicks = get_wallkicks(self.curr_piece, rotation, self.curr_piece_rotation)
        
        new_piece = self.curr_piece.rotate(rotation)
        new_rotation = (self.curr_piece_rotation + 4 + rotation.value) % 4
        
        for wallkick in wallkicks:
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
    
    #must be done before freezing piece in place
    def is_tspin(self):
        curr_piece = self.curr_piece

        if curr_piece.name != "T":
            return False

        x = self.curr_piece_x
        y = self.curr_piece_y
        board = self.board

        for dx in [-1, 1]:
            for dy in [-1, 1]:
                if not board.check_collision(curr_piece, x + dx, y + dy):
                    return False
        
        return True
    
    def hard_drop(self) -> float:
        while self.move(0, -1):
            pass

        is_tspin = self.is_tspin()

        self.board.freeze(self.curr_piece, self.curr_piece_x, self.curr_piece_y)
        lines_cleared = self.board.clear_lines()
        self._set_curr_piece(self._next_piece())
        self.can_swap = True

        is_pclear = self.board.is_empty()

        return self.scorer.score_drop(lines_cleared, is_tspin, is_pclear)
    
    def swap(self) -> bool:
        if not self.can_swap:
            return False
        if self.swap_piece == None:
            self.swap_piece = self.curr_piece.original_orientation
            self._set_curr_piece(self._next_piece())
            self.can_swap = False
            return False
        
        new_piece = self.swap_piece
        self.swap_piece = self.curr_piece.original_orientation
        self._set_curr_piece(new_piece)
        self.can_swap = False
        return True
    
    def print_game_state(self):
        board = [row[:] for row in self.board.board]
        
        for point in self.curr_piece.shape.points:
            px = self.curr_piece_x + point[0]
            py = self.curr_piece_y + point[1]
            board[py][px] = self.curr_piece.color
        
        if self.swap_piece != None:
            print("Swap piece: " + self.swap_piece.name)
        
        print("Next pieces: " + " ".join([self.bag[i].name for i in range(5)]))

        for i in range(19, -1, -1):
            row = board[i]
            for col in row:
                print(PieceColor.ansi_code(PieceColor(col.value)) + "**", end=" ")
            print()
