import random
import os
import argparse

class Game2048:
    def __init__(self):
        self.size = 4
        self.score = 0
        self.board = [[0] * self.size for _ in range(self.size)]
        self.highest = 2
        self.add_random_tile_new()
        self.add_random_tile_new()

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

        # if strat == 3:
        #     # count = 0
        #     while self.can_move():
        #         r_move = True
        #         d_move = True
        #         # move_index = self.determine_move(strat, move_index)
        #         if r_move and d_move:
        #             move_index = random.randint(2, 3)
        #         elif r_move:
        #             move_index = 3
        #         elif d_move:
        #             move_index = 2
        #         else:
        #             move_index = random.choice([0, 1])  # Random between Up and Left
        #         move = moves[move_index]

        #         old_board = [row[:] for row in self.board]
        #         if move == 'w':
        #             self.slide_up()
        #         elif move == 'a':
        #             self.slide_left()
        #         elif move == 's':
        #             self.slide_down()
        #         elif move == 'd':
        #             self.slide_right()

        #         if self.board != old_board:
        #             self.add_random_tile()
        #             # count += 1
        #             if move_index != 2:
        #                 r_move = True
        #             if move_index != 3:
        #                 d_move = True
        #         else:
        #             if move_index == 3:
        #                 r_move = False
        #             elif move_index == 2:
        #                 d_move = False

        # else:
        while self.can_move():
            # self.print_board()
            # move3 = input("Enter move (w/a/s/d): ").strip().lower()
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

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run multiple 2048 game simulations.")
    parser.add_argument("games", type=int, help="Number of games to simulate")
    parser.add_argument("strategy", type=int, choices=[1, 2, 3, 4], help="Strategy to use (1, 2, or 3)")
    # 1 - looping moves between w, a, s, d repeatedly until failure
    # 2 - completely random
    # 3 - go right until you cant, then down until you cant (repeat with random if both don't work)
    args = parser.parse_args()

    total_score = 0
    max_score = 0
    high_tile = 0

    # Run the specified number of games
    for game_number in range(1, args.games + 1):
        # print(f"Starting Game {game_number} with Strategy {args.strategy}...")
        game = Game2048()
        game.simulate_game(strat=args.strategy)
        # print(f"Game {game_number} Final Score: {game.score}\n")
        total_score += game.score
        high_tile = max(high_tile, game.highest)
        max_score = max(max_score, game.score)

    print("Simulation Complete!")
    print(f"Total Games Played: {args.games}")
    print(f"Highest Score Achieved: {max_score}")
    print(f"Highest Tile Achieved: {high_tile}")
    print(f"Average Score: {total_score / args.games:.2f}")

if __name__ == "__main__":
    main()


# if __name__ == "__main__":
#     game = Game2048()
#     score = game.simulate_game()
#     print(f"{score}")
#     #game.play()
