# tests/test_game.py
import unittest
import sys
import os

# Thêm đường dẫn để import folder cha (giúp import shared.board)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        success, result = self.board.make_move(7, 7, 1)
        self.assertTrue(success)
        self.assertEqual(result, 'continue')
        self.assertEqual(self.board.board[7][7], 1)

    def test_invalid_move(self):
        """Test move outside board"""
        # SỬA: Đã khớp chuỗi thông báo lỗi với board.py ('Invalid move')
        success, result = self.board.make_move(20, 20, 1)
        self.assertFalse(success)
        self.assertEqual(result, 'Invalid move')

    def test_win_horizontal(self):
        """Test horizontal win condition"""
        # Place 5 X's in a row
        for i in range(5):
            # SỬA: Ép lượt chơi về Player 1 để test logic thắng (bỏ qua luật đổi lượt)
            self.board.current_player = 1

            success, result = self.board.make_move(i, 0, 1)
            if i < 4:
                self.assertTrue(success, f"Move {i} failed")
                self.assertEqual(result, 'continue')
            else:  # 5th move should win
                self.assertTrue(success, "Winning move failed")
                self.assertEqual(result, 'win')
                self.assertEqual(self.board.winner, 1)

    def test_win_vertical(self):
        """Test vertical win condition"""
        for i in range(5):
            # SỬA: Ép lượt chơi về Player 1
            self.board.current_player = 1

            success, result = self.board.make_move(0, i, 1)
            if i < 4:
                self.assertTrue(success)
                self.assertEqual(result, 'continue')
            else:
                self.assertTrue(success)
                self.assertEqual(result, 'win')
                self.assertEqual(self.board.winner, 1)

    def test_win_diagonal(self):
        """Test diagonal win condition"""
        for i in range(5):
            # SỬA: Ép lượt chơi về Player 1
            self.board.current_player = 1

            success, result = self.board.make_move(i, i, 1)
            if i < 4:
                self.assertTrue(success)
                self.assertEqual(result, 'continue')
            else:
                self.assertTrue(success)
                self.assertEqual(result, 'win')
                self.assertEqual(self.board.winner, 1)

    def test_full_board(self):
        """Test draw condition"""
        small_board = CaroBoard(3) # Board 3x3 không thể thắng vì cần 5 nước
        # Fill board without winning
        moves = [(0,0,1), (0,1,2), (0,2,1),
                (1,0,2), (1,1,1), (1,2,2),
                (2,0,1), (2,1,2), (2,2,1)]

        results = []
        for x, y, player in moves:
            # Ép lượt chơi đúng với data test
            small_board.current_player = player
            success, result = small_board.make_move(x, y, player)
            results.append(result)

        # Kiểm tra move cuối cùng là draw
        self.assertEqual(results[-1], 'draw')
        self.assertTrue(small_board.is_full())

    def test_switch_player(self):
        """Test player switching"""
        self.assertEqual(self.board.current_player, 1)

        # Player 1 moves
        success, result = self.board.make_move(0, 0, 1)
        self.assertTrue(success)
        self.assertEqual(self.board.current_player, 2)

        # Player 2 moves
        success, result = self.board.make_move(1, 1, 2)
        self.assertTrue(success)
        self.assertEqual(self.board.current_player, 1)

def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCaroGame)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Running Caro Game Logic Tests...")
    print("="*50)
    success = run_tests()
    sys.exit(0 if success else 1)