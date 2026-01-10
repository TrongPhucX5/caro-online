class CaroBoard:
	def __init__(self, size=15):
		self.size = size
		self.board = [[0 for _ in range(size)] for _ in range(size)]
		self.current_player = 1  # 1 for X, 2 for O
		self.moves = []
		self.winner = None
        
	def make_move(self, x, y, player):
		if self.is_valid_move(x, y):
			self.board[y][x] = player
			self.moves.append((x, y, player))
            
			if self.check_win(x, y, player):
				self.winner = player
				return 'win'
			elif self.is_full():
				return 'draw'
			else:
				self.current_player = 3 - player  # Switch player (1->2, 2->1)
				return 'continue'
		return 'invalid'
    
	def is_valid_move(self, x, y):
		return 0 <= x < self.size and 0 <= y < self.size and self.board[y][x] == 0
    
	def check_win(self, x, y, player):
		# Check 5 in a row in all directions
		directions = [(1,0), (0,1), (1,1), (1,-1)]
        
		for dx, dy in directions:
			count = 1  # Current stone
            
			# Positive direction
			for i in range(1, 5):
				nx, ny = x + dx*i, y + dy*i
				if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny][nx] == player:
					count += 1
				else:
					break
            
			# Negative direction
			for i in range(1, 5):
				nx, ny = x - dx*i, y - dy*i
				if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny][nx] == player:
					count += 1
				else:
					break
            
			if count >= 5:
				return True
		return False
    
	def is_full(self):
		return all(cell != 0 for row in self.board for cell in row)
    
	def get_board_state(self):
		return self.board
