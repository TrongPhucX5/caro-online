# shared/board.py - ĐÚNG
class CaroBoard:
    def __init__(self, size=15):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.current_player = 1  # 1 = X, 2 = O
        self.moves_history = []  # [(x, y, player), ...]
        self.winner = None
        self.game_over = False

    def make_move(self, x, y, player=None):
        """Make a move at position (x, y)"""
        if player is None:
            player = self.current_player

        # Validate move
        if not self.is_valid_move(x, y, player):
            return False, "Invalid move"

        # Make the move
        self.board[y][x] = player
        self.moves_history.append((x, y, player))

        # Check for win
        if self.check_win(x, y, player):
            self.winner = player
            self.game_over = True
            return True, "win"

        # Check for draw
        if self.is_full():
            self.game_over = True
            return True, "draw"

        # Switch player
        self.current_player = 3 - player  # 1->2 or 2->1
        return True, "continue"

    def is_valid_move(self, x, y, player):
        """Check if move is valid"""
        # Check game state
        if self.game_over:
            return False

        # Check board boundaries
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False

        # Check cell is empty
        if self.board[y][x] != 0:
            return False

        # Check correct player turn
        if player != self.current_player:
            return False

        return True

    def check_win(self, x, y, player):
        """Check if player wins after placing at (x, y)"""
        # Directions: horizontal, vertical, diagonal down-right, diagonal up-right
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            count = 1  # Count the current stone

            # Check positive direction
            for i in range(1, 5):
                nx, ny = x + dx * i, y + dy * i
                if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny][nx] == player:
                    count += 1
                else:
                    break

            # Check negative direction
            for i in range(1, 5):
                nx, ny = x - dx * i, y - dy * i
                if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny][nx] == player:
                    count += 1
                else:
                    break

            # If we have 5 or more in a row
            if count >= 5:
                return True

        return False

    def is_full(self):
        """Check if board is full"""
        for row in self.board:
            for cell in row:
                if cell == 0:
                    return False
        return True

    def get_board(self):
        """Get copy of board state"""
        return [row[:] for row in self.board]

    def get_legal_moves(self):
        """Get all legal moves for current player"""
        moves = []
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] == 0:
                    moves.append((x, y))
        return moves

    def reset(self):
        """Reset the board for new game"""
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 1
        self.moves_history = []
        self.winner = None
        self.game_over = False

    def print_board(self):
        """Print board to console (for debugging)"""
        symbols = {0: '.', 1: 'X', 2: 'O'}

        print("   " + " ".join(f"{i:2}" for i in range(self.size)))
        for y in range(self.size):
            print(f"{y:2} ", end="")
            for x in range(self.size):
                print(f"{symbols[self.board[y][x]]:2}", end="")
            print()
        print(f"Current player: {symbols[self.current_player]}")