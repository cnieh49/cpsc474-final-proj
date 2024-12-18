# 2048 Strategy Comparison Report

### Group: Peidong Chen, Caleb Nieh

## Objective
Our goal is to determine how well an Expectimax and MCTS agent can play 2048.

## Baseline Agents
We implemented the following baseline agents:
1. **Random Agent**: Performs moves randomly.
2. **Random Heuristic Agent**: Prioritizes moving right/down (keeps high tile in one corner).
3. **Greedy Agent**: Picks the move that increases the score by the largest amount at each step. This strategy prioritizes merges of the same tile, choosing randomly between equally optimal moves.

## Metrics for Comparison
The main comparison methods for our agents:
1. **Highest Tile Distribution**: The distribution of the highest tile achieved across multiple games.
2. **Average Score**: The average score achieved across games.

### Why we chose these two?:
- We observed that certain agents have better performances depending on category. For example lets compare the following 2 baseline agents
 - The **Greedy Agent** had the higher average score among the baseline agents.
 - The **Right/Down Agent** showed stronger performance in terms of achieving higher tiles, as it prioritizes building large tiles over maximizing immediate score gains.

---

## MCTS Implementation
### Modifications
- **Pruned Search**: Limited the simulation to 25 states before stopping.  
  - **Reason**: Simulating until the game ends is computationally expensive, and 2048 can last a long time if played well.
- **Heuristic-Based Simulations**: Used the next best move instead of random moves during simulations.  
  - **Reason**: Random moves disrupted the tree's data, producing results similar to the random agent. 2048 requires deliberate moves for optimal play.

### Challenges:
- Even with pruning, MCTS remained the slowest to run due to the sheer number of possible states.
- Tree Structure:
  - **Move Nodes**: Could have up to 4 children (`w`, `a`, `s`, `d`).
  - **Chance Nodes**: Could have up to 15 children (1 for each empty tile on the grid, with a minimum of 1 non-empty tile)
- If input limit is set too low, it will cause MCTS to not have enough time to explore its children causing a divide by zero error
---

## Expectimax Implementation
### Observations
- Odd depths (e.g., 3, 5) performed better than even depths.
  - **Reason**: Expectimax alternates between `max` nodes (player moves) and `random chance` nodes (tile spawns). An even depth ends on a random chance node, leading to suboptimal decisions.
- Depths of 3 and 5 offered the best trade-off between performance and computation time.

---

## Why We Didn't Implement Q-Learning
Initially, we planned to implement Q-Learning with Function Approximation (QFL). However, after implementing MCTS, we decided to pivot to Expectimax due to the following reasons:
1. **Alignment with Game Mechanics**: Expectimax better aligns with 2048's deterministic player moves and probabilistic tile spawning. QFL would require extensive training and may not fully leverage the specific dynamics of 2048.
2. **Resource Efficiency**: Implementing and training QFL demands significant computational resources and optimization time. After observing MCTS's results, we realized QFL would yield similar outcomes.
3. **Focus on Better Performance**: Expectimax provided a more efficient and effective heuristic-based approach, which was faster and better suited for 2048.
4. **Strategic Shift**: Our goal was to implement a model capable of beating the game. Expectimax offered a faster, more reliable approach to achieve this.

---

## Results

| Time (s)  | Strategy                  | Total Games Played | Highest Score Achieved | Highest Tile Achieved | Average Score | Highest Tile Distribution                                    | Win Percentage |
|-----------|---------------------------|--------------------|------------------------|-----------------------|---------------|------------------------------------------------------------|----------------|
| 15        | Expectimax      | 500                | 244064                | 4096                  | 78150.20      | {4096: 29, 2048: 211, 1024: 211, 512: 38, 256: 11}         | 0.48%          |
|           | Expectimax                | 100                | 253972                | 4096                  | 91382.24      | {4096: 7, 2048: 53, 1024: 30, 512: 9, 256: 1}              | 0.60%          |
|           | MCTS                      | 100                | 3616                  | 128                   | 2674.88       | {128: 4, 64: 95, 32: 1}                                    | 0.00%          |
|           | Greedy                    | 100                | 23568                 | 512                   | 7355.04       | {512: 1, 256: 19, 128: 61, 64: 19}                         | 0.00%          |
|           | Random Heuristic          | 100                | 19184                 | 512                   | 6612.60       | {512: 8, 256: 42, 128: 37, 64: 13}                         | 0.00%          |
|           | Random                    | 100                | 2864                  | 256                   | 1150.84       | {256: 11, 128: 44, 64: 33, 32: 12}                         | 0.00%          |
| 30        | Expectimax      | 500                | 270260                | 4096                  | 95515.43      | {4096: 51, 2048: 247, 1024: 157, 512: 36, 256: 8, 128: 1}  | 0.60%          |
|           | Expectimax                | 100                | 234808                | 4096                  | 95848.84      | {4096: 9, 2048: 56, 1024: 28, 512: 5, 256: 2}              | 0.65%          |
|           | MCTS                      | 100                | 9160                  | 256                   | 6755.28       | {256: 6, 128: 94}                                           | 0.00%          |
|           | Greedy                    | 100                | 16904                 | 256                   | 7632.00       | {256: 32, 128: 46, 64: 20, 32: 2}                          | 0.00%          |
|           | Random Heuristic          | 100                | 17144                 | 512                   | 6281.80       | {512: 4, 256: 43, 128: 44, 64: 9}                          | 0.00%          |
|           | Random                    | 100                | 3024                  | 256                   | 1187.64       | {256: 7, 128: 55, 64: 31, 32: 7}                           | 0.00%          |
| 60        | Expectimax      | 500                | 265700                | 4096                  | 95775.54      | {4096: 54, 2048: 245, 1024: 151, 512: 37, 256: 12, 128: 1} | 0.60%          |
|           | Expectimax                | 100                | 253252                | 4096                  | 100876.64     | {4096: 13, 2048: 51, 1024: 30, 512: 5, 256: 1}             | 0.64%          |
|           | MCTS                      | 100                | 24740                 | 512                   | 15966.64      | {512: 29, 256: 69, 128: 2}                                 | 0.00%          |
|           | Greedy                    | 100                | 16520                 | 256                   | 7895.44       | {256: 29, 128: 51, 64: 19, 32: 1}                          | 0.00%          |
|           | Random Heuristic          | 100                | 20268                 | 512                   | 6617.28       | {512: 9, 256: 35, 128: 45, 64: 10, 32: 1}                  | 0.00%          |
|           | Random                    | 100                | 2928                  | 256                   | 1222.20       | {256: 13, 128: 48, 64: 34, 32: 5}                          | 0.00%          |
| No Limit  | Expectimax      | 500                | 270408                | 4096                  | 94764.41      | {4096: 53, 2048: 253, 1024: 127, 512: 49, 256: 16, 128: 2} | 0.61%          |
|           | Expectimax                | 100                | 293264                | 4096                  | 96795.44      | {4096: 7, 2048: 58, 1024: 28, 512: 4, 256: 3}              | 0.65%          |
|           | MCTS                      | 100                | 36964                 | 512                   | 21487.44      | {512: 66, 256: 32, 128: 2}                                 | 0.00%          |
|           | Greedy                    | 100                | 19456                 | 512                   | 8264.64       | {512: 1, 256: 31, 128: 52, 64: 15, 32: 1}                  | 0.00%          |
|           | Random Heuristic          | 100                | 15248                 | 512                   | 6089.68       | {512: 4, 256: 36, 128: 47, 64: 13}                         | 0.00%          |
|           | Random                    | 100                | 3140                  | 256                   | 1174.72       | {256: 6, 128: 49, 64: 43, 32: 2}                           | 0.00%          |

---

