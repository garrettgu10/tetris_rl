# Tetris RL

## Dependencies
```
pip install -r requirements.txt
```

## Running
### Viewing trained models
```
python test_models.py N
```
where N is a number in [0, 5]  

0 - genetic algorithm, beam search  
1 - cross entropy, beam search  
2 - noisy cross entropy, beam search  
3 - genetic algorithm, greedy search  
4 - cross entropy, greedy search  
5 - noisy cross entropy, greedy search  

### Training more models
```
python train_ga.py
python train_nce.py
python train_nce2.py
```

### Generating numbers in bulk & in parallel
```
make ga.regular.ten ga.beam.ten nce.regular.ten nce.beam.ten nce2.regular.ten nce2.beam.ten -j 24
```