class Scorer(object):
    def score_drop(
        self, 
        cleared_lines: int, 
        tspin: bool,
        pclear: bool) -> float:
        score = 0
        if tspin:
            score += cleared_lines
        else:
            score += 4 if cleared_lines == 4 else cleared_lines - 1
        
        if pclear:
            score += 10
        return score

class ModernScorer(Scorer):
    def score_drop(self, cleared_lines: int, tspin: bool, pclear: bool) -> float:
        score = cleared_lines ** 2
        if tspin:
            score *= 2
        if pclear:
            score += 10
        return score