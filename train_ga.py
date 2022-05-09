from ga import GeneticAlgoModel
from heuristic import TetrisHeuristic

ga_model = GeneticAlgoModel(pop_size=100, verbose=True, heuristic=TetrisHeuristic())
ga_model.train(num_generations=20, num_games=10, max_pieces=20, num_processes=24)
ga_model.save('ga.pkl')
ga_model.play_game()