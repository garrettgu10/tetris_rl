import numpy as np
from numpy import random as rand
from heuristic import TetrisHeuristic, simulate_game
import pickle
from process_util import prep_sim, start_processes, end_processes, process_function, SimArgs
import time
from datetime import timedelta


'''
    We wrote this code ourselves. But it's based on a blog post called
    "Tetris AI - The (Near) Perfect Bot"
    by Yiyuan Lee. See our paper for a full citation.
'''



class Individual():
    def __init__(self, num_weights) -> None:
        self.weights = 2 * rand.random(num_weights) - 1
        self.fitness = -10e9
        self.normalize()

    def normalize(self):
        if abs(np.linalg.norm(self.weights)) < .000001:
            return
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
        self.population = self.population[int(.3 * self.pop_size):]
        self.population.extend(self.children)
        assert self.pop_size == len(self.population)

    def tournament(self):
        self.children = []
        while len(self.children) < int(.3 * self.pop_size):
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

    def calc_fitness(self, num_games, max_pieces, num_processes):
        fresh_blood = sum([individual.fitness < 0 for individual in self.population])
        assert fresh_blood == self.pop_size or fresh_blood == int(.3 * self.pop_size)

        if num_processes == 1:
            for individual in self.population:
                individual.fitness = 0
                for _ in range(num_games):
                    score = simulate_game(individual.weights, self.heuristic, max_pieces)
                    individual.fitness += score
        else:
            args = SimArgs(num_games, max_pieces, self.heuristic)
            chromosomes, modified = prep_sim(self.population, num_processes)
            processes = start_processes(num_processes, process_function, (chromosomes, modified, args))
            chromosomes = end_processes(processes, modified, num_processes)
            self.population = chromosomes
            
    def sim_generation(self, num_games, max_pieces, num_processes):
        self.calc_fitness(num_games, max_pieces, num_processes)
        self.tournament()
        self.mutate()
        self.replace()
        return max([individual.fitness for individual in self.population])

    def train(self, num_generations, num_games, max_pieces, num_processes=1):
        for g in range(num_generations):
            start = time.time()
            best_fitness = self.sim_generation(num_games, max_pieces, num_processes)
            end = time.time()
            if self.verbose: 
                print(f'Generation {g+1} terminated with best fitness {best_fitness}')
                print(f'Time taken: {timedelta(seconds=end-start)}')


    def play_game(self, num_pieces=100):
        self.population.sort(key=lambda individual: individual.fitness)
        best_weights = self.population[-1].weights
        score = simulate_game(best_weights, self.heuristic, render=True, max_pieces=num_pieces)
        print('Game terminated with score', score)
        return score

    def save(self, save_file):
        pickle.dump(self, open(save_file, "wb" ))
    