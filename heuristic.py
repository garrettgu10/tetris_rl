from tetris import Board
from gym import Env, spaces
from typing import List

# trained weights from https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
# aggregate height: -0.510066
# complete lines: 0.760666
# holes: -0.35663
# bumpiness: -0.184483

class TetrisHeuristic():
    def __init__(self) -> None:
        self.scorers = [
            AggregateHeightScorer(),
            CompleteLinesScorer(),
            HolesScorer(),
            BumpinessScorer(),
        ]

    def num_heuristics(self):
        return len(self.scorers)

    def predict(self, weight: List[float], state: spaces.Dict):
        assert len(weight) == self.num_heuristics()
        return sum([weight[i] * scorer.score(state) for i, scorer in enumerate(self.scorers)])

def columnHeight(board: spaces.Box, x: int) -> int:
    col_height = 0
    for y in range(40):
        if board[y][x] != 0:
            col_height = y + 1
    return col_height

class BoardScorer(object):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        raise NotImplementedError

class AggregateHeightScorer(object):
    def __init__(self) -> None:
        pass
    
    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]
        aggregate_height = 0
        for x in range(10):
            aggregate_height += columnHeight(board, x)
        return aggregate_height

class CompleteLinesScorer(object):
    def __init__(self) -> None:
        pass
    
    def score(self, state: spaces.Dict) -> float:
        return state["lines_completed"]

class HolesScorer(object):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]
        holes = 0

        for x in range(10):
            holes_in_col = 0
            start_counting = False
            for y in range(39, -1, -1):
                if board[y][x] != 0:
                    start_counting = True
                elif start_counting:
                    holes_in_col += 1
            holes += holes_in_col
        return holes

class BumpinessScorer(object):
    def __init__(self) -> None:
        pass

    def score(self, state: spaces.Dict) -> float:
        board:spaces.Box = state["board"]
        heights = [columnHeight(board, x) for x in range(10)]

        bumpiness = 0
        for i in range(1, len(heights)):
            bumpiness += abs(heights[i] - heights[i - 1])
        
        return bumpiness