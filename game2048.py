import random
import os
import argparse
import time
import math

def expectimax_policy(state, depth):
    """
    Determine the best move using the Expectimax algorithm.
    :param state: Current Game2048 state.
    :param depth: Depth limit for the Expectimax search.
    :return: The best move ('w', 'a', 's', 'd').
    """
    best_move = None
    best_value = float('-inf')
    moves = state.possible_moves()

    for move in moves:
        # Simulate the state for the move
        board_copy = [row[:] for row in state.board]
        score_copy = state.score
        state.next_move(move)
        
        # Recursively evaluate using Expectimax
        value = expectimax(state, depth - 1)

        # Restore the state after simulation
        state.board = board_copy
        state.score = score_copy

        # Update the best move if necessary
        if value > best_value:
            best_value = value
            best_move = move
    return best_move



def expectimax(state, depth):
    """
    Recursive Expectimax algorithm to evaluate the best move.
    :param state: Current Game2048 state.
    :param depth: Depth limit for recursion.
    :return: The expected score of the state.
    """
    if depth == 0 or not state.can_move():
        return state.score

    max_value = float('-inf')
    for move in state.possible_moves():
        # Simulate the state for the move
        board_copy = [row[:] for row in state.board]
        score_copy = state.score
        state.next_move(move)

        # Recursively evaluate the state
        value = expectimax(state, depth - 1)

        # Restore the state after simulation
        state.board = board_copy
        state.score = score_copy

        max_value = max(max_value, value)

    return max_value

    # else:
    #     # Chance node (random tile placement)
    #     total_value = 0
    #     empty_tiles = [(r, c) for r in range(state.size) for c in range(state.size) if state.board[r][c] == 0]
    #     if not empty_tiles:
    #         return state.score

    #     for r, c in empty_tiles:
    #         # Simulate placing a '2' (90% probability)
    #         state.board[r][c] = 2
    #         value_2 = expectimax(state, depth - 1, True)
    #         total_value += 0.9 * value_2

    #         # Simulate placing a '4' (10% probability)
    #         state.board[r][c] = 4
    #         value_4 = expectimax(state, depth - 1, True)
    #         total_value += 0.1 * value_4

    #         # Undo the tile placement
    #         state.board[r][c] = 0

    #     return total_value / len(empty_tiles)




class Node:
    def __init__(self, state, action=None):
        self.state = state
        self.parent = None
        self.children = []
        self.n = 0
        self.r = 0
        self.action = action
        self.expanded = False

def UCB(r, n, T):
    exploration = math.sqrt(2 * math.log(T) / n)
    return (r / n) + exploration

def traverse(node):
    while node.expanded:
        unvisited_children = []
        for child in node.children:
            if child.n == 0:
                unvisited_children.append(child)
        if unvisited_children:
            return random.choice(unvisited_children)
        
        T = node.n
        ucb_child = max(node.children, key=lambda child: UCB(child.r, child.n, T))
        node = ucb_child
    return node


def expand(node):
    """
    Expand the current node by generating all possible moves.
    """

    if node.state.can_move() and not node.expanded:
        actions = node.state.possible_moves()

        for action in actions:
            new_state = node.state.next_move(action)
            new_node = Node(new_state, action)
            new_node.parent = node
            node.children.append(new_node)
        node.expanded = True
        return random.choice(node.children)
    return node


def simulate(state):
    """
    Simulate a random playthrough from the given state and return the score.
    """
    while state.can_move():
        actions = state.possible_moves()
        action = random.choice(actions)
        state = state.next_move(action)
    return state.score


def update(node, reward):
    """
    Backpropagate the simulation results through the tree.
    """
    while node:
        node.n += 1
        node.r += reward
        node = node.parent

def mcts_policy(root_state, time_limit=3.0):
    """
    Run MCTS to determine the best move from the root state.
    """
    root = Node(root_state)
    start_time = time.time()

    while time.time() - start_time < time_limit:
        # Selection
        leaf = traverse(root)

        # Expansion
        expanded_node = expand(leaf)

        # Simulation
        reward = simulate(expanded_node.state)

        # Backpropagation
        update(expanded_node, reward)
        

    # Choose the best move based on visits
    best_child = max(root.children, key=lambda c: c.r / c.n)
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
        old_board = [row[:] for row in self.board]

        self.slide_up()
        if self.board != old_board:
            moves.append("w")
        else:
            self.board = [row[:] for row in old_board]

        self.slide_left()
        if self.board != old_board:
            moves.append("a")
        else:
            self.board = [row[:] for row in old_board]

        self.slide_down()
        if self.board != old_board:
            moves.append("s")
        else:
            self.board = [row[:] for row in old_board]

        self.slide_right()
        if self.board != old_board:
            moves.append("d")
        else:
            self.board = [row[:] for row in old_board]
        return moves


    def add_random_tile_new(self):
        empty_tiles = [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == 0]
        if not empty_tiles:
            return
        r, c = random.choice(empty_tiles)
        self.board[r][c] = 2 if random.random() < 0.9 else 4
        self.highest = self.board[r][c] if self.board[r][c] > self.highest else self.highest
    
    def add_random_tile(self):
        empty_tiles = [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == 0]
        if not empty_tiles:
            return
        r, c = random.choice(empty_tiles)
        self.board[r][c] = 2 if random.random() < 0.9 else 4

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
        if strat == 5:
            moves = ['w', 'a', 's', 'd']
            move = mcts_policy(self, time_limit=1.0)
            return moves.index(move)
        

        if strat == 7:
            self.print_board()
            moves = ['w', 'a', 's', 'd']
            move = expectimax_policy(self, 3)  # Adjust depth for performance
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
    total_tiles = {}
    max_score = 0
    high_tile = 0

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
        if game.highest in total_tiles:
            total_tiles[game.highest] += 1
        else: 
            total_tiles[game.highest] = 1
        high_tile = max(high_tile, game.highest)
        max_score = max(max_score, game.score)

    sorted_by_keys = dict(sorted(total_tiles.items()))

    print("Simulation Complete!")
    print(f"Total Games Played: {args.games}")
    print(f"Highest Score Achieved: {max_score}")
    print(f"Highest Tile Achieved: {high_tile}")
    print(f"Average Score: {total_score / args.games:.2f}")
    print(f"Highest Tile Distribution: {sorted_by_keys}")

if __name__ == "__main__":
    main()


# if __name__ == "__main__":
#     game = Game2048()
#     score = game.simulate_game()
#     print(f"{score}")
#     #game.play()
