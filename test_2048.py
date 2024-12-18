import subprocess

"""
Can also view README.md for the descriptions, findings, and results
---------------------------------------------------------------------
Group: Peidong Chen, Caleb Nieh

Here our goal is to determine how well an expectimax and mcts agent can play 2048. 

Our baseline agents were random, random heursitic (right/down), and greedy. The most important ones to compare against were:
the greedy base agent (strategy 3), which picks the move that will increase your score (calculated by the sum of all the tiles 
that you have already merged) by the largest amount every time (strategy prioritizes merges of the same tile choosing randomly 
between equal best moves), and our agent that very roughly mimicked the general 2048 strategy of trying to keep your best/highest 
tiles in one corner. Our agent would randomly choose between going down and going right as long as both were valid (if not, 
choose randomly between remaing valid moves).

When comparing to our baseline, we have a few ways we can compare, the main ones being the highest tile distribution
across games, as well as the average score. While they are both indications of the success of an agent or strategy,
these will differ slightly, depending on the strategy. For example, from our baseline agents, the greedy strategy will
return the highest average score. However, its highest tile distribution is not as strong as the right/down strategy,
as it will prioritize highest piece over score.

Some Things to Notes:

When implementing MCTS we opted to change the simulation a bit so that it fit our game better. Instead of using a random playout 
until the game ends,we opted to prune the search and choose the next best move.
Why?
We pruned the search to make the program run faster as 2048 (we chose to simulate 25 states before stopping), if played right, 
can go on for a long time. Going all the way to the end wouldn't benefit our tree by too much. We choose the next best move, which
was the next immediate best move, calculated based off of the score increase as well as tile placement, weighing the tiles based
off of their values, instead of a random move because in 2048 we don't want to do random moves. Doing a random move simulation 
messed up our tree data and gave us results that were similar to the random agent. This is because in 2048 our moves cannot be 
random if we want to make the best play. Even with pruning MCTS is the slowest to run as there are simply way to may states to 
visit all of them in a timely manner. We implemented the tree as move nodes and chance nodes where move nodes could have up to 
4 children (w, a, s, d) and chance nodes could have up to 15 children (1 for each empty tile on the grid- we always have 1 tile minimum).
Due to the large state space, mcts runs slow and if we set the time limit too low, it may cause mcts to end before it has explore 
all children nodes of the root state causing a divide by zero error.

When implementing expectimax we found that depth that were odd performed better and depths of 3 and 5 were best mix of performance and time
Why odd?
We separated the tree nodes into either a max node or a random chance node. If the depth is even we end up return the score on a random chance node
which makes our expectimax algorithm do some suboptimal moves


Why we didn't implement Q-Learn like we originally said in the video?
After implementing MCTS and seeing it's results we thought QLearning would yeild similar results to MCTS.
We decided to stop implementing Q-Learning with Function Approximation (QFL) for 2048 and pivoted to Expectimax due to the following reasons:
1. Expectimax aligns better with 2048’s deterministic nature when it comes to player moves and probabilistic nature with tile spawning. 
QFL, being a reinforcement learning method, would require more extensive training and tuning, which may not directly leverage the specific dynamics of 2048.
2. Implementing and training a QFL model demands significant computational resources and time for optimization and we figured this out after implementing mcts. 
Expectimax, on the other hand, provides a more straightforward heuristic-based approach, allowing us to focus on exploring optimal strategies efficiently.
3. We wanted a better model that could beat the game so we went with Expectimax which would be faster and perform better for a game like 2048


Results: https://docs.google.com/spreadsheets/d/1qoLnjjEVtiJnsqZ6Lp5vJxHFZ4a2lUxvHyiGLg_HPcg/edit?usp=sharing

Test script runs all the agents on 10 games with no time limit. To run the test script, you can call make, then run ./Test2048.

to change the number of games or add time limits run following format:
pypy3 game2048 [# of games] [time limit in seconds]

Like the test script, if a time limit is not given, the code will default to infinity (without a time limit)


"""


for i in range(1, 6):
    subprocess.run(["pypy3", "game2048.py", "10", str(i)])
    print("------------------------")
