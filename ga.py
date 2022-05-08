import numpy as np
from numpy import random as rand
from heuristic import TetrisHeuristic, simulate_game
import pickle

class Individual():
    def __init__(self, num_weights) -> None:
        self.weights = 2 * rand.random(num_weights) - 1
        self.fitness = -1
        self.normalize()

    def normalize(self):
        self.weights = self.weights / np.linalg.norm(self.weights)

    def set_weights(self, weights):
        assert len(weights) == len(self.weights)
        self.weights = weights
        self.normalize()

    def mutate(self):
        pos = rand.choice(len(self.weights))
        self.weights[pos] += 0.4 * rand.random() - 0.2 # In the range [-.2, .2]
        self.normalize()


class GeneticAlgoModel():
    def __init__(self, pop_size: int, verbose: bool, heuristic: TetrisHeuristic) -> None:
        self.pop_size = pop_size
        self.verbose = verbose
        self.heuristic = heuristic
        self.population = [Individual(heuristic.num_heuristics()) for _ in range(pop_size)] 

    def mutate(self):
        for individual in self.children:
            if rand.random() < .05:
                individual.mutate()

    def cross_over(self, parent1, parent2):
        child = Individual(self.heuristic.num_heuristics())
        child.set_weights(parent1.fitness * parent1.weights + parent2.fitness * parent2.weights)
        return child

    def replace(self):
        self.population.sort(key=lambda i: i.fitness)
        self.population = self.population[:int(.3 * self.pop_size)]
        self.population.extend(self.children)
        assert self.pop_size == len(self.population)

    def tournament(self):
        self.children = []
        while len(self.children < int(.3 * self.pop_size)):
            selected = rand.choice(self.population, int(.1 * self.pop_size), replace=False)

            first, second = selected[0], selected[1]
            if second.fitness > first.fitness:
                first, second = second, first

            for cur in selected:
                if cur.fitness > first.fitness: 
                    second = first
                    first = cur
                elif cur.fitness > second.fitness:
                    second = cur

            child = self.cross_over(first, second)
            self.children.append(child)

    def calc_fitness(self, num_games, max_pieces):
        for individual in self.population:
            individual.fitness = 0
            for _ in range(num_games):
                individual.fitness += simulate_game(individual.weights, self.heuristic, max_pieces)

    def sim_generation(self, num_games, max_pieces):
        self.calc_fitness(num_games, max_pieces)
        self.tournament()
        self.mutate()
        self.replace()
        return max([individual.fitness for individual in self.population])

    def learn(self, num_generations, num_games, max_pieces):
        for g in num_generations:
            best_fitness = self.sim_generation(num_games, max_pieces)
            if self.verbose: print(f'Generation {g+1} terminated with best fitness {best_fitness}')

    def play_game(self):
        self.population.sort(key=lambda individual: individual.fitness)
        best_weights = self.population[-1].weights
        score = simulate_game(best_weights, self.heuristic, render=True)
        print('Game terminated with score', score)

    def save(self, save_file):
        pickle.dump(self, open(save_file, "wb" ))
    