import random
import os

class Game2048:
    def __init__(self):
        self.size = 4
        self.score = 0
        self.board = [[0] * self.size for _ in range(self.size)]
        self.add_random_tile()
        self.add_random_tile()

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
        os.system('cls' if os.name == 'nt' else 'clear')
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
        print("Game Over! Thanks for playing.")

if __name__ == "__main__":
    game = Game2048()
    game.play()
