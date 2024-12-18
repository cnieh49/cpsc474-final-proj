import random
import argparse
import time
import math
import copy
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

def evaluate_state(state):
    position_weight = [ #snake weight value
        [8192, 16384, 32768, 65536],
        [4096,  2048,  1024,  512,],
        [32,     64,   128,   256],
        [16,     8,      4,     2]
    ]
    
    weighted_sum = 0
    for r in range(state.size):
        for c in range(state.size):
            weighted_sum += state.board[r][c] * position_weight[r][c]
    
    return state.score + weighted_sum  #combine curr_score(short term) with snake weight score (long_term)

def expectimax_policy(state, depth=3):
    best_move = None
    best_value = float('-inf')
    moves = state.possible_moves()

    for move in moves:
        new_state = copy.deepcopy(state)
        new_state.next_state(move)
        value = expectimax(new_state, depth - 1)
        if value > best_value:
            best_value = value
            best_move = move

    return best_move


def expectimax(state, depth):
    if not state.can_move() or depth == 0:
        return evaluate_state(state)

    #max_node: player's move
    def max_value(state, depth):
        moves = state.possible_moves()
        
        #recurse
        max_val = float('-inf')
        for move in moves:
            new_state = copy.deepcopy(state)
            new_state.next_move(move)
            val = expectimax(new_state, depth - 1)
            max_val = max(max_val, val)
        return max_val

    #chance node: random tile placement
    def chance_value(state, depth):
        empty_cells = [(r, c) for r in range(state.size) for c in range(state.size) if state.board[r][c] == 0]
        if not empty_cells:
            return evaluate_state(state)
        
        total_value = 0
        for r, c in empty_cells:
            new_state = copy.deepcopy(state)
            new_state.board[r][c] = 2
            total_value += expectimax(new_state, depth - 1)
        
        return total_value / len(empty_cells)  #average value over all possible placements


    if depth % 2 == 1:  #player move
        return max_value(state, depth)
    else:  #random tile placement
        return chance_value(state, depth)




##################################################################################################################################################################################
##################################################################################################################################################################################
##################################################################################################################################################################################

class Node:
    def __init__(self, state, parent=None, action=None, is_chance_node=False):
        self.state = state  #2048 game instance
        self.parent = parent
        self.children = []
        self.n = 0 
        self.r = 0 
        self.action = action  
        self.is_chance_node = is_chance_node #if node is a random tile or a move

def UCB(r, n, T):
    exploration = math.sqrt(2 * math.log(T) / n)
    return (r / n) + exploration

def traverse(node):
    while node.children:
        if node.is_chance_node: #randomly choose chance node so we don't run into the issue of traversing a chance node to much. We want uniform visits for chance nodes. As n->inf random->uniform visits for each node
            node = random.choice(node.children)
        else: #pick move with best ucb value
            unvisited_children = []
            for child in node.children:
                if child.n == 0:
                    unvisited_children.append(child)
            if unvisited_children:
                return random.choice(unvisited_children)
            
            T = node.n
            node = max(node.children, key=lambda child: UCB(child.r, child.n, T))
    return node

def expand(node):
    if node.is_chance_node: #expand chance nodes by adding tile '2' in random empty cells
        empty_cells = [(r, c) for r in range(node.state.size) for c in range(node.state.size) if node.state.board[r][c] == 0]
        for r, c in empty_cells:
            new_state = copy.deepcopy(node.state)
            new_state.board[r][c] = 2
            child = Node(new_state, parent=node, is_chance_node=False)
            node.children.append(child)
    else: #expand decision nodes by adding valid moves
        for move in node.state.possible_moves():
            new_state = copy.deepcopy(node.state)
            new_state.next_move(move)
            child = Node(new_state, parent=node, action=move, is_chance_node=True)
            node.children.append(child)
    return random.choice(node.children)

def simulate(node):
    state = node.state
    if node.is_chance_node: #modify board a bit to ensure random playout doens't start on chance nodes
        node.state.add_random_tile()

    for _ in range(25): #prune since 2048 can take too long to end
        if not state.can_move():
            break
        #choose the move that maximizes the heuristic evaluation
        moves = state.possible_moves()
        best_move = max( #can't be entirely random playout as we still want good moves
            moves,
            key=lambda move: evaluate_state(copy.deepcopy(state).next_state(move))
        )
        state.next_state(best_move) 

    return evaluate_state(state) / (2 ** 20) #makes reward smaller helps with exploration

def update(node, reward):
    while node:
        node.n += 1
        node.r += reward
        node = node.parent

def mcts_policy(root_state, time_limit):
    root = Node(root_state, is_chance_node=False)
    start_time = time.time()

    while time.time() - start_time < time_limit:
        #traverse
        leaf = traverse(root)        
        #expand
        if not leaf.children and leaf.state.can_move():
            leaf = expand(leaf)
        
        #simulate
        sim_leaf = copy.deepcopy(leaf)
        reward = simulate(sim_leaf)
        
        #update
        update(leaf, reward)
    # for c in root.children:
    #     print(c.n)
    # print('------------')
    best_child = max(root.children, key=lambda c: c.r / c.n)
    return best_child.action


##################################################################################################################################################################################
##################################################################################################################################################################################
##################################################################################################################################################################################

class Game2048:
    def __init__(self):
        self.size = 4
        self.score = 0
        self.board = [[0] * self.size for _ in range(self.size)]
        self.highest = 2
        self.add_random_tile()
        self.add_random_tile()
    
    def next_state(self, move): #performs move and adds new tile
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
    
    def next_move(self, move): #performs move
        if move == 'w':
            self.slide_up()
        elif move == 'a':
            self.slide_left()
        elif move == 's':
            self.slide_down()
        else:
            self.slide_right()
        return self
    

    def possible_moves(self):
        moves = []
        for direction, slide_func in [('w', self.slide_up), ('a', self.slide_left), ('s', self.slide_down), ('d', self.slide_right)]:
            #store the original board state
            original_board = [row[:] for row in self.board]

            slide_func()

            if self.board != original_board:
                moves.append(direction)

            #restore the original board
            self.board = original_board

        return moves
    
    def greedy_moves(self): #goes for highest high score (short term)
        highest_score = -1
        moves = []
        for direction, slide_func in [(0, self.slide_up), (1, self.slide_left), (2, self.slide_down), (3, self.slide_right)]:
            #store the original board state
            original_board = [row[:] for row in self.board]

            slide_func()

            #if the board changes, the move is valid
            if self.board != original_board:
                moves.append((direction, self.score))
                if self.score > highest_score:
                    highest_score = self.score

            #restore the original board
            self.board = original_board
        if highest_score < 0:
            return random.randint(0, 3)
        highest_moves = []
        for direction, score in moves:
            if score >= highest_score:
                highest_moves.append(direction)
        return highest_moves[random.randint(0, len(highest_moves) - 1)]
    
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
        for row in self.board:
            print("+----" * self.size + "+")
            print("".join(f"|{num:^4}" if num != 0 else "|    " for num in row) + "|")
        print("+----" * self.size + "+")

    def play(self): #allows player to play in terminal
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
        # if strat == 1:
        #     return (move_index + 1) % 4
        if strat == 1:
            return random.randint(0, 3)
        if strat == 2:
            r_move = self.can_move_right()
            d_move = self.can_move_down()
            if r_move and d_move:
                return random.randint(2, 3)
            elif r_move:
                return 3
            elif d_move:
                return 2
            else:
                return random.choice([0, 1])  #random between up and left
        # if strat == 4:
        #     r_move = self.can_move_right()
        #     d_move = self.can_move_down()
        #     if move_index == -1:
        #         return 3
        #     elif move_index != 2:
        #         if r_move:
        #             return 3
        #         elif d_move:
        #             return 2
        #     else:
        #         if d_move:
        #             return 2
        #         elif r_move:
        #             return 3
        #     return random.choice([0, 1])
        
        if strat == 3: #greedy
            return self.greedy_moves()
        
        if strat == 4: #mcts
            # self.print_board()
            moves = ['w', 'a', 's', 'd']
            move = mcts_policy(self, .5)
            return moves.index(move)
        
        if strat == 5: #expectimax
            # self.print_board()
            moves = ['w', 'a', 's', 'd']
            move = expectimax_policy(self, 3)  #adjust depth for performance 3 or 5 is best
            return moves.index(move)

    def can_move_right(self):
        old_board = [row[:] for row in self.board]
        self.slide_right()
        can_move = (self.board != old_board)
        self.board = old_board  #restore board
        return can_move

    def can_move_down(self):
        old_board = [row[:] for row in self.board]
        self.slide_down()
        can_move = (self.board != old_board)
        self.board = old_board  #restore board
        return can_move

    def simulate_game(self, strat, limit):
        moves = ['w', 'a', 's', 'd']  #repeated move sequence
        move_index = -1

        start_time = time.time()
        while self.can_move() and ((time.time() - start_time) < limit):
            # self.print_board()
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

        return self.score, self.highest

def simulate_single_game(game_number, strategy, time_limit):
    game = Game2048()
    game.simulate_game(strat=strategy, limit=time_limit)
    
    #return the relevant data for aggregation
    return (game.score, game.highest)

def main():
    begin_time = time.time()
    # 1 - completely random
    # 2 - random pick between going right and going down (make a random choice if you can't do either)
    # 3 - greedy, always make the move that results in the highest added score, else move randomly
    # 4 - mcts
    # 5 - expectimax
    parser = argparse.ArgumentParser(description="Run multiple 2048 game simulations.")
    parser.add_argument("games", type=int, help="Number of games to simulate")
    parser.add_argument("strategy", type=int, choices=[1, 2, 3, 4, 5], help="Strategy to use (1 - 5)")
    parser.add_argument("limit", type=float, nargs='?', help="total amount of time that a set of games can run")

    args = parser.parse_args()

    if args.games == 0:
        game = Game2048()
        game.play()
        return

    if args.limit is None:
        time_limit = float('inf')
    else:
        time_limit = args.limit
    
    total_score = 0
    total_tiles = defaultdict(int)
    max_score = 0
    high_tile = 0
    total_wins = 0

    with ProcessPoolExecutor() as executor:
        futures = []

        #submit each game as a task
        for game_number in range(1, args.games + 1):
            futures.append(executor.submit(simulate_single_game, game_number, args.strategy, time_limit))
        
        #process results as the games complete
        for future in as_completed(futures):
            score, highest = future.result()

            #update aggregates
            total_score += score
            total_tiles[highest] += 1
            high_tile = max(high_tile, highest)
            max_score = max(max_score, score)
            if highest >= 2048:
                total_wins += 1

    # strat_name = ["wasd on repeat", "random", "random right/down", "right then down", "greedy (take highest score)", "mcts", "expectimax"]
    strat_name = ["random", "random right/down", "greedy (take highest score)", "mcts", "expectimax"]
    sorted_by_keys = dict(sorted(total_tiles.items(), reverse=True))

    print(f"Simulation Complete! Strategy: {strat_name[args.strategy - 1]}")
    print(f"Total Games Played: {args.games}")
    print(f"Highest Score Achieved: {max_score}")
    print(f"Highest Tile Achieved: {high_tile}")
    print(f"Average Score: {total_score / args.games:.2f}")
    print(f"Highest Tile Distribution: {sorted_by_keys}")
    print(f"Win Percentage: {total_wins / args.games:.2f}")
    end_time = time.time()
    print(f"Start time: {begin_time}, end time: {end_time}, time elapsed: {end_time - begin_time:.3f}")

if __name__ == "__main__":
    main()
