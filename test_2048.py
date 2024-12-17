import subprocess

"""
include a build script/makefile and a test script so we don't have to figure out how to run your code; the test script 
should include a brief description of your game, what your code is doing, your research question, and the results 
(for example, "I'm determining how well a Q-agent can play NFL Strategy.  Here's my winning percentage over 250000 games 
vs. a rule-based player" or "I'm determining how MCTS compares to a heuristic-based agent. Here's my winning percentage 
over 100 games for a range of search times when playing against a minimax player with a simple heuristic searching to 
depth 4, with both sides making random moves 10% of the time:")  If your results will take more than a few minutes to generate, 
please have your script run what can be done in a few minutes, describe your complete results, and include instructions 
for reproducing those complete results.

Group: Peidong Chen, Caleb Nieh

Here our goal is to determine how well an expectimax and mcts agent can play 2048. 

We had several baseline agents, including some random ones (completely random and cycling the four moves in order)
but the most important ones to compare against were the greedy-based agent (strategy 5), which picks the move that
will increase you score by the largest amount every time (choosing randomly between equal best moves), and our agents
that very roughly mimicked the general 2048 strategy of trying to keep your best/highest tiles in one corner. 
We had two of those agents, both which tried to keep their best tiles in the bottom right corner, but with slightly
different approaches. One would randomly choose between going down and going right as long as both were valid,
and the other would alternate between going right until you wouldn't any longer, and going down until you couldn't any
longer, both choosing arbitrary values when neither right or down were viable options.


"""


for i in range(1, 8):
    subprocess.run(["python3", "game2048.py", "10", str(i)])
    print("------------------------")
