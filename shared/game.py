import time
from shared.board import CaroBoard

class CaroGame:
	"""Manage a complete caro game"""
	def __init__(self, player1_id, player2_id):
		self.player1_id = player1_id
		self.player2_id = player2_id
		self.board = CaroBoard()
		self.start_time = None
		self.end_time = None
	def start(self):
		"""Start the game"""
		self.start_time = time.time()
	def make_move(self, player_id, x, y):
		"""Player makes a move"""
		# Determine which player is making move
		if player_id == self.player1_id:
			player = 1
		elif player_id == self.player2_id:
			player = 2
		else:
			return False, "Not a player in this game"
		success, result = self.board.make_move(x, y, player)
		if success and result in ['win', 'draw']:
			self.end_time = time.time()
		return success, result
	def get_game_state(self):
		"""Get current game state"""
		return {
			'board': self.board.get_board(),
			'current_player': self.board.current_player,
			'moves': len(self.board.moves_history),
			'winner': self.board.winner,
			'game_over': self.board.game_over,
			'player_turn': self.get_player_turn()
		}
	def get_player_turn(self):
		"""Get which player's turn it is"""
		if self.board.current_player == 1:
			return self.player1_id
		else:
			return self.player2_id
