class TetrisHeuristic():
    def __init__(self) -> None:
        pass

    def num_heuristics(self):
        raise NotImplementedError

    def predict(self, weights, board):
        raise NotImplementedError