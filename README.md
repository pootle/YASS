# YASS
Yet another simple Sudoku solver

Solver.py contains 2 classes:

sudoboardbrute is a very simple brute force solver in 60 lines of Python, It merely walks the tree of possible values for blank values until it
finds a valid solution. This typically runs on my old laptop in < .5 seconds. It will find all valid solutions.

sudoboardsmart uses the same basic technique but optimizes the search order, and shortcuts the case where a blank value has only 1 valid value.
It typically runs about 20 - 100 times faster than the simple brute force version.

There is a simple command line wrapper - sudoku5.py. 
It uses the python package colorama and probably won't work on windows.

Run with 

python3 sudoku5.py -m 0 700800060 000009100 002005008 100003200 000002086 043760001 080500000 300040000 001086004 -s 0 -c 0

Use -c 1 for the fast version

Use python3 sudoku5.py -h for parameter info
