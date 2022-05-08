from ga import GeneticAlgoModel
from heuristic import TetrisHeuristic

ga_model = GeneticAlgoModel(pop_size=100, verbose=True, heuristic=TetrisHeuristic())
ga_model.train(num_generations=20, num_games=100, max_pieces=500, num_processes=16)
ga_model.play_game()
ga_model.save('ga.pkl')