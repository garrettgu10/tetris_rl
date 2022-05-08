from ga import GeneticAlgoModel

ga_model = GeneticAlgoModel()

ga_model.learn(num_generations=20, num_games=100, max_pieces=500)
ga_model.play_game()
ga_model.save('ga.pkl')