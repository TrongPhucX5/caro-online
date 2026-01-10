import unittest
from shared.board import CaroBoard

class TestCaroGame(unittest.TestCase):
    def setUp(self):
        self.board = CaroBoard(15)
    
    def test_initial_board(self):
        """Test board initialization"""
        self.assertEqual(len(self.board.board), 15)
        self.assertEqual(len(self.board.board[0]), 15)
        self.assertEqual(self.board.current_player, 1)
    
    def test_valid_move(self):
        """Test valid move placement"""
        result = self.board.make_move(7, 7, 1)
        self.assertEqual(result, 'continue')
        self.assertEqual(self.board.board[7][7], 1)
    
    def test_invalid_move(self):
        """Test move outside board"""
        result = self.board.make_move(20, 20, 1)
        self.assertEqual(result, 'invalid')
    
    def test_win_horizontal(self):
        """Test horizontal win condition"""
        # Place 5 X's in a row
        for i in range(5):
            self.board.make_move(i, 0, 1)
        
        self.assertEqual(self.board.winner, 1)
    
    def test_win_vertical(self):
        """Test vertical win condition"""
        for i in range(5):
            self.board.make_move(0, i, 1)
        
        self.assertEqual(self.board.winner, 1)
    
    def test_win_diagonal(self):
        """Test diagonal win condition"""
        for i in range(5):
            self.board.make_move(i, i, 1)
        
        self.assertEqual(self.board.winner, 1)
    
    def test_full_board(self):
        """Test draw condition"""
        small_board = CaroBoard(3)
        # Fill board without winning
        moves = [(0,0,1), (0,1,2), (0,2,1),
                (1,0,2), (1,1,1), (1,2,2),
                (2,0,1), (2,1,2), (2,2,1)]
        
        results = []
        for x, y, player in moves:
            results.append(small_board.make_move(x, y, player))
        
        self.assertIn('draw', results)

def run_tests():
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests()
