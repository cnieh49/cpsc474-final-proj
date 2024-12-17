import random
import os
import argparse
import time
import math
import copy
from collections import defaultdict

def expectimax_policy(game, depth=3):
    best_move = None
    best_value = float('-inf')
    moves = game.possible_moves()

    for move in moves:
        new_game = copy.deepcopy(game)
        new_game.next_move(move)
        value = expectimax(new_game, depth - 1)
        if value > best_value:
            best_value = value
            best_move = move

    return best_move


def evaluate_state(state):
    position_weight = [
        [8192, 16384, 32768, 65536],
        [4096,  2048,  1024,  512,],
        [32,     64,   128,   256],
        [16,     8,      4,     2]
    ]
    
    weighted_sum = 0
    for r in range(state.size):
        for c in range(state.size):
            weighted_sum += state.board[r][c] * position_weight[r][c]
    
    return state.score + weighted_sum  # Combine score and positional heuristic

def expectimax(state, depth):


    #If game over or depth limit is reached
    if not state.can_move() or depth == 0:
        return evaluate_state(state)

    # Max Node: Player's turn
    def max_value(state, depth):
        moves = state.possible_moves()
        if not moves:
            return state.score
        
        # Evaluate all possible moves and take the maximum value
        max_val = float('-inf')
        for move in moves:
            new_state = copy.deepcopy(state)
            new_state.next_move(move)
            val = expectimax(new_state, depth - 1)
            max_val = max(max_val, val)
        return max_val

    # Chance Node: Random tile placement
    def chance_value(state, depth):
        empty_cells = [(r, c) for r in range(state.size) for c in range(state.size) if state.board[r][c] == 0]
        if not empty_cells:
            return state.score
        
        total_value = 0
        for r, c in empty_cells:
            new_state = copy.deepcopy(state)
            new_state.board[r][c] = 2  # Only tile '2' is added
            total_value += expectimax(new_state, depth - 1)
        
        return total_value / len(empty_cells)  # Average value over all possible placements

    # If it's the player's turn (max node), evaluate all moves
    if depth % 2 == 1:  # Odd depth: player's turn
        return max_value(state, depth)
    else:  # Even depth: chance node
        return chance_value(state, depth)



class Node:
    def __init__(self, state, parent=None, action=None, is_chance_node=False):
        self.state = state  # Game2048 instance
        self.parent = parent
        self.children = []
        self.n = 0  # Visit count
        self.r = 0  # Total reward
        self.action = action  # Action taken to get to this state
        self.is_chance_node = is_chance_node  # Whether the node is a chance node

def UCB1(node, total_visits):
    if node.n == 0:
        return float('inf')  # Prioritize unvisited nodes
    exploitation = node.r / node.n
    exploration = math.sqrt(2 * math.log(total_visits) / node.n)
    return exploitation + exploration

def traverse(node):
    while node.children:
        if node.is_chance_node:
            # Randomly choose a child since tile placement is stochastic
            node = random.choice(node.children)
        else:
            # Use UCB1 to select the best child
            total_visits = sum(child.n for child in node.children)
            node = max(node.children, key=lambda child: UCB1(child, total_visits))
    return node

def expand(node):
    if node.is_chance_node:
        # Expand chance nodes by adding tile '2' in random empty cells
        empty_cells = [(r, c) for r in range(node.state.size) for c in range(node.state.size) if node.state.board[r][c] == 0]
        for r, c in empty_cells:
            new_state = copy.deepcopy(node.state)
            new_state.board[r][c] = 2
            child = Node(new_state, parent=node, is_chance_node=False)
            node.children.append(child)
    else:
        # Expand decision nodes by adding valid moves
        for move in node.state.possible_moves():
            new_state = copy.deepcopy(node.state)
            new_state.next_move(move)
            child = Node(new_state, parent=node, action=move, is_chance_node=True)
            node.children.append(child)


def simulate(state):
    simulation_state = copy.deepcopy(state)
    for _ in range(25):
        if not simulation_state.can_move():
            break

        # Choose the move that maximizes the heuristic evaluation
        moves = simulation_state.possible_moves()
        best_move = max(
            moves,
            key=lambda move: evaluate_state(copy.deepcopy(simulation_state).next_move(move))
        )
        simulation_state.next_move(best_move)

        # random play doesn't perform well so we instead play a few rounds to get the best move
        # move = random.choice(simulation_state.possible_moves())
        # simulation_state.next_move(move)
    return evaluate_state(simulation_state)

def backpropagate(node, reward):
    while node:
        node.n += 1
        node.r += reward
        node = node.parent

def mcts_policy(root_state, time_limit):
    root = Node(root_state, is_chance_node=False)
    start_time = time.time()
    
    while time.time() - start_time < time_limit:
        # Selection
        leaf = traverse(root)
        
        # Expansion
        if not leaf.children and leaf.state.can_move():
            expand(leaf)
        
        # Simulation
        if leaf.children:
            leaf = random.choice(leaf.children)
        reward = simulate(leaf.state)
        
        # Backpropagation
        backpropagate(leaf, reward)
    
    # Choose the best move (child with the most visits)
    best_child = max(root.children, key=lambda c: c.n)
    return best_child.action

class Game2048:
    def __init__(self):
        self.size = 4
        self.score = 0
        self.board = [[0] * self.size for _ in range(self.size)]
        self.highest = 2
        self.add_random_tile_new()
        self.add_random_tile_new()
        self.initial = self.board

    def get_state(self):
        return tuple(tile for row in self.board for tile in row)

    def initial_state(self):
        return self.initial

    def get_reward(self):
        return self.score

    def action_space(self):
        return 4
    
    def game_over(self, state):
        # Check if there are no valid moves left
        self.board = [row[:] for row in state]
        return not self.can_move()
    
    def next_move(self, move):
        if move == 'w':
            self.slide_up()
        elif move == 'a':
            self.slide_left()
        elif move == 's':
            self.slide_down()
        else:
            self.slide_right()

        self.add_random_tile()
        return self
    

    def possible_moves(self):
        moves = []
        for direction, slide_func in [('w', self.slide_up), ('a', self.slide_left), 
                                    ('s', self.slide_down), ('d', self.slide_right)]:
            # Store the original board state
            original_board = [row[:] for row in self.board]

            # Apply the move
            slide_func()

            # If the board changes, the move is valid
            if self.board != original_board:
                moves.append(direction)

            # Restore the original board
            self.board = original_board

        return moves


    def add_random_tile_new(self):
        empty_tiles = [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == 0]
        if not empty_tiles:
            return
        r, c = random.choice(empty_tiles)
        self.board[r][c] = 2 #only add 2
        self.highest = self.board[r][c] if self.board[r][c] > self.highest else self.highest
    
    def add_random_tile(self):
        empty_tiles = [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == 0]
        if not empty_tiles:
            return
        r, c = random.choice(empty_tiles)
        self.board[r][c] = 2 #only add 2

    def can_move(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    return True
                if c + 1 < self.size and self.board[r][c] == self.board[r][c + 1]:
                    return True
                if r + 1 < self.size and self.board[r][c] == self.board[r + 1][c]:
                    return True
        return False

    def slide_row_left(self, row):
        new_row = [num for num in row if num != 0]
        merged = [False] * len(new_row)
        
        for i in range(len(new_row) - 1):
            if new_row[i] == new_row[i + 1] and not merged[i] and not merged[i + 1]:
                new_row[i] *= 2
                self.score += new_row[i]
                self.highest = new_row[i] if new_row[i] > self.highest else self.highest
                new_row[i + 1] = 0
                merged[i] = True
        
        new_row = [num for num in new_row if num != 0]
        return new_row + [0] * (self.size - len(new_row))

    def slide_left(self):
        self.board = [self.slide_row_left(row) for row in self.board]

    def slide_right(self):
        self.board = [self.slide_row_left(row[::-1])[::-1] for row in self.board]

    def slide_up(self):
        self.board = list(map(list, zip(*self.board)))
        self.slide_left()
        self.board = list(map(list, zip(*self.board)))

    def slide_down(self):
        self.board = list(map(list, zip(*self.board)))
        self.slide_right()
        self.board = list(map(list, zip(*self.board)))

    def print_board(self):
        # os.system('cls' if os.name == 'nt' else 'clear')
        for row in self.board:
            print("+----" * self.size + "+")
            print("".join(f"|{num:^4}" if num != 0 else "|    " for num in row) + "|")
        print("+----" * self.size + "+")

    def play(self):
        while self.can_move():
            self.print_board()
            print(f"Score: {self.score}")
            move = input("Enter move (w/a/s/d): ").strip().lower()
            if move not in "wasd" or len(move) != 1:
                print("Invalid move. Use 'w', 'a', 's', or 'd'.")
                continue

            old_board = [row[:] for row in self.board]
            if move == 'w':
                self.slide_up()
            elif move == 'a':
                self.slide_left()
            elif move == 's':
                self.slide_down()
            elif move == 'd':
                self.slide_right()

            if self.board != old_board:
                self.add_random_tile()
            else:
                print("Move didn't change the board. Try a different move.")

        self.print_board()
        print(f"Score: {self.score}")
        print("Game Over! Thanks for playing.")

    def determine_move(self, strat, move_index):
        if strat == 1:
            return (move_index + 1) % 4
        if strat == 2:
            return random.randint(0, 3)
        if strat == 3:
            r_move = self.can_move_right()
            d_move = self.can_move_down()
            # print(f"right: {r_move}")
            # print(f"down: {d_move}")
            if r_move and d_move:
                return random.randint(2, 3)
            elif r_move:
                return 3
            elif d_move:
                return 2
            else:
                return random.choice([0, 1])  # Random between Up and Left
        if strat == 4:
            r_move = self.can_move_right()
            d_move = self.can_move_down()
            if move_index == -1:
                return 3
            elif move_index != 2:
                if r_move:
                    return 3
                elif d_move:
                    return 2
            else:
                if d_move:
                    return 2
                elif r_move:
                    return 3
            return random.choice([0, 1])
        if strat == 5: #mcts
            self.print_board()
            root = copy.deepcopy(self)
            moves = ['w', 'a', 's', 'd']
            move = mcts_policy(root, 1)
            return moves.index(move)
        

        if strat == 7:
            self.print_board()
            moves = ['w', 'a', 's', 'd']
            move = expectimax_policy(self, 5)  # Adjust depth for performance
            return moves.index(move)





        # if strat > 4:
        #     state = self.get_state()
        #     return state, self.agent.get_action(state)

    def can_move_right(self):
        old_board = [row[:] for row in self.board]
        self.slide_right()
        can_move = (self.board != old_board)
        self.board = old_board  # Restore board
        return can_move

    def can_move_down(self):
        old_board = [row[:] for row in self.board]
        self.slide_down()
        can_move = (self.board != old_board)
        self.board = old_board  # Restore board
        return can_move

    def simulate_game(self, strat):
        moves = ['w', 'a', 's', 'd']  # Repeated move sequence
        move_index = -1

        # if strat > 4:
        #     self.agent = QLearning(Game2048(), 9)  # Create a Q-learning agent

        while self.can_move():
            # self.print_board()
            # move3 = input("Enter move (w/a/s/d): ").strip().lower()
            # if strat > 4:
            #     state, move_index = self.determine_move(strat, move_index)
            # else:
            move_index = self.determine_move(strat, move_index)
            # print(f"move_index: {move_index}")
            move = moves[move_index]

            old_board = [row[:] for row in self.board]
            if move == 'w':
                self.slide_up()
            elif move == 'a':
                self.slide_left()
            elif move == 's':
                self.slide_down()
            elif move == 'd':
                self.slide_right()

            if self.board != old_board:
                self.add_random_tile()
            #     if strat > 4:
            #         reward = self.get_reward()
            #         next_state = self.get_state()
            #         self.agent.update(state, move_index, reward, next_state)
            # elif strat > 4:
            #     reward = -1  # Penalize invalid moves
            #     next_state = state
            #     self.agent.update(state, move_index, reward, next_state)

        return self.score, self.highest

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run multiple 2048 game simulations.")
    parser.add_argument("games", type=int, help="Number of games to simulate")
    parser.add_argument("strategy", type=int, choices=[1, 2, 3, 4, 5, 6, 7], help="Strategy to use (1, 2, or 3)")
    # 1 - looping moves between w, a, s, d repeatedly until failure
    # 2 - completely random
    # 3 - random pick between going right and going down (make a random choice if you can't do either)
    # 4 - go right until you cant, then down until you cant (repeat with random if both don't work)
    # 5 - mcts
    # 6 - q-learning
    # 7 - expectimax (if time permits)
    args = parser.parse_args()

    total_score = 0
    total_tiles = defaultdict(int)
    max_score = 0
    high_tile = 0
    total_wins = 0

    # Run the specified number of games
    if args.games == 0:
        game = Game2048()
        game.play()


    for game_number in range(1, args.games + 1):
        # print(f"Starting Game {game_number} with Strategy {args.strategy}...")
        game = Game2048()
        game.simulate_game(strat=args.strategy)

        # print(f"Game {game_number} Final Score: {game.score}\n")
        total_score += game.score
        total_tiles[game.highest] += 1
        high_tile = max(high_tile, game.highest)
        max_score = max(max_score, game.score)
        if high_tile >= 2048:
            total_wins += 1

    sorted_by_keys = dict(sorted(total_tiles.items(), reverse=True))

    print("Simulation Complete!")
    print(f"Total Games Played: {args.games}")
    print(f"Highest Score Achieved: {max_score}")
    print(f"Highest Tile Achieved: {high_tile}")
    print(f"Average Score: {total_score / args.games:.2f}")
    print(f"Highest Tile Distribution: {sorted_by_keys}")
    print(f"Win Percentage: {total_wins / args.games:.2f}")

if __name__ == "__main__":
    main()


# if __name__ == "__main__":
#     game = Game2048()
#     score = game.simulate_game()
#     print(f"{score}")
#     #game.play()
