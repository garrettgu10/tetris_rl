import imp
from multiprocessing import Queue, Process
from heuristic import simulate_game

def start_processes(num_processes, process_function, args):
    processes = []
    for _ in range(num_processes):
        processes.append(Process(target=process_function, args=args))
    for p in processes:
        p.start()
    return processes

def end_processes(processes, modified, num_processes):
    count, chromosomes = 0, []
    while count < num_processes:
        c = modified.get()
        if c == 'DONE':
            count+=1
            continue
        chromosomes.append(c)
    
    for p in processes:
        p.join()

    return chromosomes

def prep_sim(chromosomes, num_processes):
    for _ in range(num_processes):
        chromosomes.append("DONE")

    q, modified = Queue(), Queue()
    for c in chromosomes:
        q.put(c)
    chromosomes = q

    return chromosomes, modified

def process_function_ga(chromosomes, modified):
    while True:
        c = chromosomes.get()
        if c == 'DONE':
            break
        
        c.fitness = 0
        for game in range(c.num_games):
                score = simulate_game(c.weights, c.heuristic, c.max_pieces)
                c.fitness += score
        modified.put(c)

    modified.put('DONE')