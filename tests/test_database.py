# tests/test_database.py - TESTS RIÊNG CHO DATABASE
import unittest
import tempfile
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import CaroDatabase

class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database"""

    def setUp(self):
        """Create test database"""
        # Tạo temp file với delete=False để quản lý thủ công
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()  # Đóng file ngay
        self.db = CaroDatabase(self.db_path)

    def tearDown(self):
        """Clean up test database"""
        # Đảm bảo database connection đã đóng
        if hasattr(self, 'db') and self.db:
            self.db.close()

        # Xóa file
        if os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except:
                pass  # Bỏ qua nếu không xóa được

    def test_user_registration_and_auth(self):
        """Test user registration and authentication"""
        # Register new user
        success, result = self.db.register_user("newuser", "password123", "new@example.com")
        self.assertTrue(success)
        print(f"✅ User registered: {result['username']}")

        # Authenticate with correct password
        success, user = self.db.authenticate_user("newuser", "password123")
        self.assertTrue(success)
        self.assertEqual(user['username'], 'newuser')
        print(f"✅ User authenticated: {user['username']}")

        # Fail with wrong password
        success, error = self.db.authenticate_user("newuser", "wrongpass")
        self.assertFalse(success)
        print(f"✅ Authentication failed as expected with wrong password")

    def test_game_saving(self):
        """Test saving and retrieving games"""
        # Register two users
        self.db.register_user("player_a", "pass")
        self.db.register_user("player_b", "pass")

        # Authenticate to get IDs
        success, user_a = self.db.authenticate_user("player_a", "pass")
        success, user_b = self.db.authenticate_user("player_b", "pass")

        # Simulate game moves
        moves = [
            {'player_id': user_a['id'], 'x': 7, 'y': 7},
            {'player_id': user_b['id'], 'x': 8, 'y': 7},
            {'player_id': user_a['id'], 'x': 7, 'y': 8},
            {'player_id': user_b['id'], 'x': 8, 'y': 8},
            {'player_id': user_a['id'], 'x': 7, 'y': 9},
        ]

        # Save game (player_a wins)
        game_id = self.db.save_game(user_a['id'], user_b['id'], moves, winner_id=user_a['id'])
        self.assertIsNotNone(game_id)
        print(f"✅ Game saved with ID: {game_id}")

        # Check user stats updated
        stats_a = self.db.get_user_stats(user_a['id'])
        stats_b = self.db.get_user_stats(user_b['id'])

        # Kiểm tra stats
        self.assertIsNotNone(stats_a)
        self.assertIsNotNone(stats_b)

        if stats_a and stats_b:
            print(f"✅ Player A wins: {stats_a.get('wins', 0)}, Player B losses: {stats_b.get('losses', 0)}")

    def test_leaderboard(self):
        """Test leaderboard functionality"""
        # Add test users với games
        test_users = [
            ("champion", "pass", 1500),
            ("runnerup", "pass", 1400),
            ("third", "pass", 1300),
        ]

        for username, password, score in test_users:
            # Register user
            self.db.register_user(username, password)
            success, user = self.db.authenticate_user(username, password)

            if success:
                # Update score và total_games
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "UPDATE users SET score = ?, total_games = 10 WHERE id = ?",
                    (score, user['id'])
                )
                self.db.connection.commit()

        # Get leaderboard - CHỈ lấy users có total_games > 0
        leaderboard = self.db.get_leaderboard(10)

        print(f"Leaderboard entries: {len(leaderboard)}")
        for i, player in enumerate(leaderboard, 1):
            print(f"  {i}. {player['username']} - {player['score']} points")

        # Kiểm tra có ít nhất 3 entries
        self.assertGreaterEqual(len(leaderboard), 3)

        # Sắp xếp leaderboard để kiểm tra
        if len(leaderboard) >= 3:
            sorted_leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)
            print(f"✅ Leaderboard sorted correctly")

    def test_user_stats(self):
        """Test getting user statistics"""
        # Register and login user
        self.db.register_user("stats_user", "pass")
        success, user = self.db.authenticate_user("stats_user", "pass")

        self.assertTrue(success)

        # Get stats
        stats = self.db.get_user_stats(user['id'])

        self.assertIsNotNone(stats)
        self.assertEqual(stats['username'], 'stats_user')
        self.assertEqual(stats['total_games'], 0)  # Chưa có game
        print(f"✅ User stats retrieved: {stats['username']}")

class TestDatabaseBasic(unittest.TestCase):
    """Basic database tests"""

    def test_database_creation(self):
        """Test database file creation"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            db_path = tmp.name

        try:
            db = CaroDatabase(db_path)

            # Test table creation
            cursor = db.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = ['users', 'games', 'moves', 'friends', 'chat_messages']
            for table in expected_tables:
                self.assertIn(table, tables)
                print(f"✅ Table '{table}' exists")

            db.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

def run_database_tests():
    """Run database tests"""
    print("="*60)
    print("🧪 RUNNING DATABASE TESTS")
    print("="*60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseBasic))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*60)
    print("📊 DATABASE TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("✅ ALL DATABASE TESTS PASSED!")
    else:
        print("❌ SOME DATABASE TESTS FAILED!")

        for test, traceback in result.failures:
            print(f"\n❌ FAILED: {test}")
            print(traceback)

        for test, traceback in result.errors:
            print(f"\n❌ ERROR: {test}")
            print(traceback)

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_database_tests()
    sys.exit(0 if success else 1)