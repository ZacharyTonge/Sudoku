# My Sudoku Solver

I first began this project for my apprenticeship under the python module as I enjoy solving the NYT sudokus so why not! 

## First algorithm iteration
I began by creating the linear solving algorithm displayed in oldsudoku.py which would attempt to brute force puzzles by working it's way from the first to last box trying every digit until the sudoku became invalid and then it backtracked. I soon realised it was too slow for complex puzzles.

## Making the algorithm more efficient!
I then did some research on more efficient algorithms and soon began working on the second iteration. 
The new solver works by finding the square with least possible numbers. This eradicates easy squares with only one solution vastly reducing the number of routes the algorithm will take.

## Adding an image parser
Now I was happy with the efficiency of the algorithm, I then had the idea of being able to upload photos of sudokus so I could take screenshots of the NYT sudokus and get it to solve them. This involved firstly processing an image to extract all the cells and their numbers. I then had to predict these numbers using a neural network which I have trained on the Mnist dataset alongside some of my own processed images as I found it strugggled with typed digits as the Mnist dataset are handwritten digits. My own digits, I've took from some of the sudokus I've trained it on (some of which I had to correct the number the network had predicted). I ended up going down a rabbit hole on how CNN's work and the most efficient way of training them (hence the comments I've added to the model.py file to try and jog my memory on what each layer is actually doing)

### Creating the GUI
Finally I created a quick GUI to make it easy to use!! :) 