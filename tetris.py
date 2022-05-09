import random
from collections import deque

from piece import Rotation, PieceColor, Piece, DEFAULT_PIECES
from scorer import Scorer, ModernScorer
from wallkick import get_wallkicks
from typing import List, Set, Tuple

#represents only the matrix, not next pieces, swap pieces, current piece
class Board(object):
    def __init__(self):
        self.board = [[PieceColor.EMPTY] * 10 for _ in range(40)]
    
    def clone(self):
        clone = Board()
        clone.board = [row[:] for row in self.board]
        return clone

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
    
    def _find_possible_positions(self, piece: Piece, startx: int, starty: int, start_rotation: int) -> Set[Tuple[int, int, int]]:
        orientations = piece.get_rotations()
        
        visited = set()
        queue = deque([(startx, starty, start_rotation)])
        res = set()
        while queue:
            x, y, orientation_index = queue.popleft()
            orientation = orientations[orientation_index]
            if (x, y, orientation_index) in visited:
                continue
            visited.add((x, y, orientation_index))
            
            #move left
            if not self.check_collision(orientation, x - 1, y):
                queue.append((x - 1, y, orientation_index))
            #move right
            if not self.check_collision(orientation, x + 1, y):
                queue.append((x + 1, y, orientation_index))

            #rotate left
            new_orientation_index = (orientation_index + 3) % 4
            new_orientation = orientations[new_orientation_index]
            if not self.check_collision(new_orientation, x, y):
                queue.append((x, y, new_orientation_index))
            
            #rotate right
            new_orientation_index = (orientation_index + 1) % 4
            new_orientation = orientations[new_orientation_index]
            if not self.check_collision(new_orientation, x, y):
                queue.append((x, y, new_orientation_index))
            
            #move all the way down
            newy = y - 1
            while not self.check_collision(orientation, x, newy):
                newy -= 1
            newy += 1
            
            if not self.check_collision(orientation, x, newy):
                res.add((x, newy, orientation_index)) #hard drop
            queue.append((x, newy, orientation_index)) #soft drop
        
        return sorted(list(res))
    
    def add_cheese(self, nlines: int):
        cheese = ([PieceColor.BLUE] * 9) + [PieceColor.EMPTY]
        random.shuffle(cheese)
        self.board = ([cheese for _ in range(nlines)] + self.board)[:40]
    
    def is_empty(self):
        return all(self.board[y][x] == PieceColor.EMPTY for x in range(10) for y in range(40))

PIECE_LIMIT = 200

class Game(object):
    def __init__(self, scorer = ModernScorer(), rand: random.Random = random.Random(), skip=False):
        if skip:
            return

        self.random = random

        self.board = Board()
        self.bag = deque()
        self._refill_bag()

        self._set_curr_piece(self._next_piece())

        self.swap_piece = None
        self.can_swap = True
        self.game_over = False
        
        self.remaining_pieces = PIECE_LIMIT

        if scorer == None:
            scorer = ModernScorer()
        self.scorer = scorer

        self.lines_completed_by_last_move = 0
        self.last_move_was_tspin = False

    def clone(self, clone_board=True):
        rand = random.Random()
        rand.setstate(self.random.getstate())
        clone = Game(skip=True)
        clone.scorer = self.scorer
        clone.random = rand
        if clone_board:
            clone.board = self.board.clone()
        else:
            clone.board = self.board
        clone.bag = self.bag.copy()
        clone.curr_piece = self.curr_piece.clone()
        clone.curr_piece_x = self.curr_piece_x
        clone.curr_piece_y = self.curr_piece_y
        clone.curr_piece_rotation = self.curr_piece_rotation
        clone.swap_piece = self.swap_piece
        clone.can_swap = self.can_swap
        clone.game_over = self.game_over
        clone.remaining_pieces = self.remaining_pieces
        clone.lines_completed_by_last_move = self.lines_completed_by_last_move
        return clone

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
        
    def set_curr_position(self, x: int, y: int, orientation: int):
        self.curr_piece_x = x
        self.curr_piece_y = y
        self.curr_piece_rotation = orientation
        self.curr_piece = self.curr_piece.get_rotations()[orientation]
        self.last_move_was_tspin = False
        self.lines_completed_by_last_move = 0
    
    def rotate(self, rotation: Rotation) -> bool:
        if self.game_over:
            return False

        self.last_move_was_tspin = False
        self.lines_completed_by_last_move = 0

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
            return False

        self.last_move_was_tspin = False
        self.lines_completed_by_last_move = 0

        if not self.board.check_collision(self.curr_piece, self.curr_piece_x + dx, self.curr_piece_y + dy):
            self.curr_piece_x += dx
            self.curr_piece_y += dy
            return True
        return False
    
    #must be done before freezing piece in place
    def is_tspin(self) -> bool:
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
        self.t_spin_last_drop = is_tspin

        self.board.freeze(self.curr_piece, self.curr_piece_x, self.curr_piece_y)
        lines_cleared = self.board.clear_lines()
        self._set_curr_piece(self._next_piece())
        self.can_swap = True

        self.lines_completed_by_last_move = lines_cleared

        is_pclear = self.board.is_empty()

        self.remaining_pieces -= 1
        if self.remaining_pieces == 0:
            self.game_over = True

        return self.scorer.score_drop(lines_cleared, is_tspin, is_pclear)
    
    def find_hard_drop_pos(self) -> Tuple[int, int]:
        start_x = self.curr_piece_x
        start_y = self.curr_piece_y

        while self.move(0, -1):
            pass

        res = (self.curr_piece_x, self.curr_piece_y)
        self.curr_piece_x = start_x
        self.curr_piece_y = start_y
        return res
    
    def swap(self) -> bool:
        if not self.can_swap:
            return False
        if self.swap_piece == None:
            self.swap_piece = self.curr_piece.original_orientation
            self._set_curr_piece(self._next_piece())
            self.can_swap = False
            return False

        self.last_move_was_tspin = False
        self.lines_completed_by_last_move = 0
        
        new_piece = self.swap_piece
        self.swap_piece = self.curr_piece.original_orientation
        self._set_curr_piece(new_piece)
        self.can_swap = False
        return True
    
    def find_possible_positions(self) -> List[Tuple[int, int, int]]:
        start_piece = self.curr_piece
        start_x = self.curr_piece_x
        start_y = self.curr_piece_y
        start_rotation = self.curr_piece_rotation

        visited = set()
        queue = deque([(start_x, start_y, start_rotation)])
        res = set()

        while queue:
            x, y, rotation = queue.popleft()
            if (x, y, rotation) in visited:
                continue
            visited.add((x, y, rotation))

            self.set_curr_position(x, y, rotation)

            for dx, dy in [(-1, 0), (1, 0)]:
                if self.move(dx, dy):
                    queue.append((self.curr_piece_x, self.curr_piece_y, self.curr_piece_rotation))
                    self.set_curr_position(x, y, rotation)
            
            for move in [Rotation.CCW, Rotation.CW]:
                if self.rotate(move):
                    queue.append((self.curr_piece_x, self.curr_piece_y, self.curr_piece_rotation))
                    self.set_curr_position(x, y, rotation)

            hard_drop_state = (*self.find_hard_drop_pos(), rotation)
            
            res.add(hard_drop_state)
            queue.append(hard_drop_state)
        
        # return game to original state
        self.set_curr_position(start_x, start_y, start_rotation)

        return sorted(list(res), key=lambda x: (x[2], x[0], x[1]))

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
    
    def add_cheese(self, nlines: int):
        self.board.add_cheese(nlines)
