# database/database.py (HOÀN CHỈNH)
import sqlite3
import hashlib
import json
from datetime import datetime

class CaroDatabase:
    def __init__(self, db_path="caro.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = None
        self.setup_database()
    
    def setup_database(self):
        """Setup database with required tables"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.create_tables()
            self.add_default_data()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            display_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            total_games INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            score INTEGER DEFAULT 1000,  -- ELO-like score
            win_streak INTEGER DEFAULT 0,
            best_win_streak INTEGER DEFAULT 0
        )
        ''')
        
        # Games table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER NOT NULL,
            player2_id INTEGER NOT NULL,
            winner_id INTEGER,  -- NULL for draw
            board_size INTEGER DEFAULT 15,
            total_moves INTEGER DEFAULT 0,
            game_duration INTEGER,  -- in seconds
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            status TEXT DEFAULT 'completed',  -- completed, abandoned
            FOREIGN KEY (player1_id) REFERENCES users (id),
            FOREIGN KEY (player2_id) REFERENCES users (id),
            FOREIGN KEY (winner_id) REFERENCES users (id)
        )
        ''')
        
        # Moves table (stores all moves of all games)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            move_number INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            x_position INTEGER NOT NULL,
            y_position INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games (id),
            FOREIGN KEY (player_id) REFERENCES users (id),
            UNIQUE(game_id, move_number)
        )
        ''')
        
        # Friends table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id1 INTEGER NOT NULL,
            user_id2 INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',  -- pending, accepted, blocked
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id1, user_id2),
            FOREIGN KEY (user_id1) REFERENCES users (id),
            FOREIGN KEY (user_id2) REFERENCES users (id),
            CHECK (user_id1 != user_id2)
        )
        ''')
        
        # Chat messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT,
            sender_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_player1 ON games(player1_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_player2 ON games(player2_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_moves_game ON moves(game_id)')
        
        self.connection.commit()
        print("✅ Database tables created with indexes")
    
    def add_default_data(self):
        """Add default test users"""
        test_users = [
            ('player1', '123', 'player1@example.com'),
            ('player2', '123', 'player2@example.com'),
            ('alice', 'password', 'alice@example.com'),
            ('bob', 'password', 'bob@example.com'),
            ('charlie', 'password', 'charlie@example.com'),
            ('diana', 'password', 'diana@example.com')
        ]
        
        cursor = self.connection.cursor()
        
        for username, password, email in test_users:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                password_hash = self._hash_password(password)
                cursor.execute('''
                INSERT INTO users (username, password_hash, email, score)
                VALUES (?, ?, ?, ?)
                ''', (username, password_hash, email, 1000))
                print(f"  Added test user: {username}")
        
        self.connection.commit()
        print(f"✅ Added {len(test_users)} test users")
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, email=None):
        """Register a new user"""
        try:
            cursor = self.connection.cursor()
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, "Username already exists"
            
            # Hash password and insert user
            password_hash = self._hash_password(password)
            
            cursor.execute('''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            
            user_id = cursor.lastrowid
            self.connection.commit()
            
            print(f"✅ User registered: {username} (ID: {user_id})")
            return True, {"user_id": user_id, "username": username}
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        try:
            cursor = self.connection.cursor()
            password_hash = self._hash_password(password)
            
            cursor.execute('''
            SELECT id, username, email, total_games, wins, losses, draws, score
            FROM users 
            WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Update last login time
                cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user_data['id'],))
                self.connection.commit()
                
                # Convert Row to dict
                user_dict = dict(user_data)
                user_dict['win_rate'] = round((user_dict['wins'] / user_dict['total_games'] * 100), 2) if user_dict['total_games'] > 0 else 0
                
                print(f"✅ User authenticated: {username}")
                return True, user_dict
            else:
                return False, "Invalid username or password"
                
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
        
    # Thêm các phương thức này vào class CaroDatabase (sau phương thức authenticate_user)

    def get_user_info(self, user_id):
        """Get basic user info"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
            SELECT id, username, display_name, score, total_games, wins, losses, draws
            FROM users 
            WHERE id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            if user_data:
                return dict(user_data)
            return None
        except Exception as e:
            print(f"❌ Failed to get user info: {e}")
            return None

    def update_user_profile(self, user_id, display_name=None, new_password=None):
        """Update user profile"""
        try:
            cursor = self.connection.cursor()
            
            updates = []
            params = []
            
            if display_name:
                updates.append("display_name = ?")
                params.append(display_name)
            
            if new_password:
                password_hash = self._hash_password(new_password)
                updates.append("password_hash = ?")
                params.append(password_hash)
            
            if not updates:
                return False
                
            params.append(user_id)
            
            query = f'''
            UPDATE users 
            SET {', '.join(updates)}
            WHERE id = ?
            '''
            
            cursor.execute(query, params)
            self.connection.commit()
            
            print(f"✅ Updated profile for user ID: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update profile: {e}")
            return False

    def update_user_score(self, user_id, score_change):
        """Update user score"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
            UPDATE users 
            SET score = MAX(score + ?, 0)
            WHERE id = ?
            ''', (score_change, user_id))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ Failed to update score: {e}")
            return False

    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
            SELECT id, username, display_name, score, total_games, wins, losses, draws
            FROM users 
            WHERE username = ?
            ''', (username,))
            
            user_data = cursor.fetchone()
            if user_data:
                return dict(user_data)
            return None
        except Exception as e:
            print(f"❌ Failed to get user by username: {e}")
            return None
    
    def save_game(self, player1_id, player2_id, moves_data, winner_id=None, board_size=15):
        """Save a completed game to database"""
        try:
            cursor = self.connection.cursor()
            
            # Calculate game duration (simulate 10-30 minutes)
            import random
            game_duration = random.randint(600, 1800)  # 10-30 minutes in seconds
            
            # Insert game record
            cursor.execute('''
            INSERT INTO games (player1_id, player2_id, winner_id, board_size, total_moves, game_duration, end_time)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (player1_id, player2_id, winner_id, board_size, len(moves_data), game_duration))
            
            game_id = cursor.lastrowid
            
            # Save all moves
            for move_number, move in enumerate(moves_data, 1):
                cursor.execute('''
                INSERT INTO moves (game_id, move_number, player_id, x_position, y_position)
                VALUES (?, ?, ?, ?, ?)
                ''', (game_id, move_number, move['player_id'], move['x'], move['y']))
            
            # Update player statistics
            players = [player1_id, player2_id]
            for player_id in players:
                cursor.execute('''
                UPDATE users SET total_games = total_games + 1 
                WHERE id = ?
                ''', (player_id,))
            
            if winner_id:
                # Update winner stats
                cursor.execute('''
                UPDATE users 
                SET wins = wins + 1,
                    win_streak = win_streak + 1,
                    best_win_streak = MAX(best_win_streak, win_streak + 1),
                    score = score + 20  -- Win gives +20 points
                WHERE id = ?
                ''', (winner_id,))
                
                # Update loser stats
                loser_id = player2_id if winner_id == player1_id else player1_id
                cursor.execute('''
                UPDATE users 
                SET losses = losses + 1,
                    win_streak = 0,
                    score = MAX(score - 20, 0)  -- Lose gives -20 points, minimum 0
                WHERE id = ?
                ''', (loser_id,))
            else:
                # Draw - update both players
                for player_id in players:
                    cursor.execute('''
                    UPDATE users 
                    SET draws = draws + 1,
                        score = score + 5  -- Draw gives +5 points
                    WHERE id = ?
                    ''', (player_id,))
            
            self.connection.commit()
            print(f"✅ Game saved: ID {game_id}, {len(moves_data)} moves")
            return game_id
            
        except Exception as e:
            print(f"❌ Failed to save game: {e}")
            return None
    
    def get_user_stats(self, user_id):
        """Get detailed statistics for a user"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
            SELECT 
                u.username,
                u.total_games,
                u.wins,
                u.losses,
                u.draws,
                u.score,
                u.win_streak,
                u.best_win_streak,
                u.created_at,
                u.last_login,
                COALESCE(AVG(g.game_duration), 0) as avg_game_duration,
                COUNT(DISTINCT f.user_id2) as friends_count
            FROM users u
            LEFT JOIN games g ON (u.id = g.player1_id OR u.id = g.player2_id)
            LEFT JOIN friends f ON (u.id = f.user_id1 AND f.status = 'accepted')
            WHERE u.id = ?
            GROUP BY u.id
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                stats = dict(row)
                
                # Calculate additional stats
                total_games = stats['total_games']
                if total_games > 0:
                    stats['win_rate'] = round((stats['wins'] / total_games) * 100, 2)
                    stats['loss_rate'] = round((stats['losses'] / total_games) * 100, 2)
                    stats['draw_rate'] = round((stats['draws'] / total_games) * 100, 2)
                else:
                    stats['win_rate'] = stats['loss_rate'] = stats['draw_rate'] = 0
                
                # Get recent games
                cursor.execute('''
                SELECT 
                    g.id,
                    CASE 
                        WHEN g.player1_id = ? THEN u2.username
                        ELSE u1.username
                    END as opponent,
                    CASE 
                        WHEN g.winner_id = ? THEN 'Win'
                        WHEN g.winner_id IS NULL THEN 'Draw'
                        ELSE 'Loss'
                    END as result,
                    g.total_moves,
                    g.game_duration,
                    g.end_time
                FROM games g
                JOIN users u1 ON g.player1_id = u1.id
                JOIN users u2 ON g.player2_id = u2.id
                WHERE g.player1_id = ? OR g.player2_id = ?
                ORDER BY g.end_time DESC
                LIMIT 5
                ''', (user_id, user_id, user_id, user_id))
                
                stats['recent_games'] = [dict(game) for game in cursor.fetchall()]
                
                return stats
            return None
            
        except Exception as e:
            print(f"❌ Failed to get user stats: {e}")
            return None
    
    def get_leaderboard(self, limit=10, order_by='score'):
        """Get leaderboard sorted by specified column"""
        try:
            cursor = self.connection.cursor()

            valid_columns = ['score', 'wins', 'win_streak', 'total_games']
            if order_by not in valid_columns:
                order_by = 'score'

            # SỬA: Bỏ điều kiện total_games > 0 để hiển thị cả users mới
            query = f'''
            SELECT
                username,
                score,
                total_games,
                wins,
                losses,
                draws,
                win_streak,
                best_win_streak,
                CASE
                    WHEN total_games > 0 THEN ROUND(wins * 100.0 / total_games, 2)
                    ELSE 0
                END as win_rate
            FROM users
            ORDER BY {order_by} DESC
            LIMIT ?
            '''

            cursor.execute(query, (limit,))

            leaderboard = []
            for row in cursor.fetchall():
                leaderboard.append(dict(row))

            return leaderboard

        except Exception as e:
            print(f"❌ Failed to get leaderboard: {e}")
            return []
    
    def search_users(self, search_term, limit=20):
        """Search for users by username"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
            SELECT id, username, total_games, wins, score
            FROM users
            WHERE username LIKE ?
            ORDER BY username
            LIMIT ?
            ''', (f'%{search_term}%', limit))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"❌ Failed to search users: {e}")
            return []
    
    def add_friend_request(self, from_user_id, to_user_id):
        """Send friend request"""
        try:
            cursor = self.connection.cursor()
            
            # Check if friendship already exists
            cursor.execute('''
            SELECT status FROM friends 
            WHERE (user_id1 = ? AND user_id2 = ?) OR (user_id1 = ? AND user_id2 = ?)
            ''', (from_user_id, to_user_id, to_user_id, from_user_id))
            
            existing = cursor.fetchone()
            if existing:
                status = existing['status']
                if status == 'accepted':
                    return False, "Already friends"
                elif status == 'pending':
                    return False, "Friend request already pending"
                elif status == 'blocked':
                    return False, "Cannot send request (blocked)"
            
            # Add friend request
            cursor.execute('''
            INSERT INTO friends (user_id1, user_id2, status)
            VALUES (?, ?, 'pending')
            ''', (from_user_id, to_user_id))
            
            self.connection.commit()
            return True, "Friend request sent"
            
        except Exception as e:
            return False, f"Failed to send friend request: {str(e)}"
    
    def backup_database(self, backup_path):
        """Create backup of database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def restore_database(self, backup_path):
        """Restore database from backup"""
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            
            # Reconnect to restored database
            self.connection.close()
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            print(f"✅ Database restored from: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

# Test script
def test_database():
    """Test database functionality"""
    print("🧪 Testing Caro Database...")
    
    # Create test database
    db = CaroDatabase("test_caro.db")
    
    try:
        # Test authentication
        print("\n1. Testing authentication...")
        success, result = db.authenticate_user("player1", "123")
        if success:
            print(f"   ✅ Login successful: {result['username']}")
        else:
            print(f"   ❌ Login failed: {result}")
        
        # Test user stats
        print("\n2. Testing user stats...")
        if success:
            stats = db.get_user_stats(result['id'])
            if stats:
                print(f"   ✅ Got stats for {stats['username']}")
                print(f"      Score: {stats['score']}, Games: {stats['total_games']}")
        
        # Test leaderboard
        print("\n3. Testing leaderboard...")
        leaderboard = db.get_leaderboard(5)
        print(f"   ✅ Leaderboard has {len(leaderboard)} entries")
        for i, player in enumerate(leaderboard, 1):
            print(f"      {i}. {player['username']} - {player['score']} points")
        
        # Test search
        print("\n4. Testing user search...")
        users = db.search_users("play", 5)
        print(f"   ✅ Found {len(users)} users matching 'play'")
        
        # Test game saving (simulated)
        print("\n5. Testing game save...")
        if success:
            moves = [
                {'player_id': result['id'], 'x': 7, 'y': 7},
                {'player_id': 2, 'x': 7, 'y': 8},
                {'player_id': result['id'], 'x': 8, 'y': 7},
            ]
            game_id = db.save_game(result['id'], 2, moves, winner_id=result['id'])
            if game_id:
                print(f"   ✅ Game saved with ID: {game_id}")
        
        print("\n✅ All database tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_database()