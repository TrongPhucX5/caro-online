import sqlite3
import hashlib

class CaroDatabase:
	def __init__(self, db_path="caro.db"):
		self.conn = sqlite3.connect(db_path)
		self.create_tables()
    
	def create_tables(self):
		cursor = self.conn.cursor()
        
		# Users table
		cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT UNIQUE NOT NULL,
			password_hash TEXT NOT NULL,
			email TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			total_games INTEGER DEFAULT 0,
			wins INTEGER DEFAULT 0,
			losses INTEGER DEFAULT 0,
			draws INTEGER DEFAULT 0,
			elo_rating INTEGER DEFAULT 1000
		)
		''')
        
		# Games table
		cursor.execute('''
		CREATE TABLE IF NOT EXISTS games (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			player1_id INTEGER,
			player2_id INTEGER,
			winner_id INTEGER,
			board_size INTEGER DEFAULT 15,
			moves TEXT,  # JSON string of moves
			start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			end_time TIMESTAMP,
			FOREIGN KEY (player1_id) REFERENCES users (id),
			FOREIGN KEY (player2_id) REFERENCES users (id),
			FOREIGN KEY (winner_id) REFERENCES users (id)
		)
		''')
        
		self.conn.commit()
		print("✅ Database tables created")
    
	def register_user(self, username, password):
		try:
			cursor = self.conn.cursor()
			password_hash = hashlib.sha256(password.encode()).hexdigest()
            
			cursor.execute('''
			INSERT INTO users (username, password_hash) 
			VALUES (?, ?)
			''', (username, password_hash))
            
			self.conn.commit()
			return True, "Registration successful"
		except sqlite3.IntegrityError:
			return False, "Username already exists"
		except Exception as e:
			return False, str(e)
    
	def authenticate_user(self, username, password):
		cursor = self.conn.cursor()
		password_hash = hashlib.sha256(password.encode()).hexdigest()
        
		cursor.execute('''
		SELECT id, username FROM users 
		WHERE username = ? AND password_hash = ?
		''', (username, password_hash))
        
		user = cursor.fetchone()
		if user:
			return True, {"id": user[0], "username": user[1]}
		return False, "Invalid credentials"
    
	def save_game(self, player1_id, player2_id, winner_id, moves):
		cursor = self.conn.cursor()
        
		# Save game
		cursor.execute('''
		INSERT INTO games (player1_id, player2_id, winner_id, moves, end_time)
		VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
		''', (player1_id, player2_id, winner_id, moves))
        
		game_id = cursor.lastrowid
        
		# Update user statistics
		users = [player1_id, player2_id]
		for user_id in users:
			cursor.execute('''
			UPDATE users SET total_games = total_games + 1 
			WHERE id = ?
			''', (user_id,))
        
		if winner_id:
			cursor.execute('''
			UPDATE users SET wins = wins + 1 WHERE id = ?
			''', (winner_id,))
            
			loser_id = player2_id if winner_id == player1_id else player1_id
			cursor.execute('''
			UPDATE users SET losses = losses + 1 WHERE id = ?
			''', (loser_id,))
        
		self.conn.commit()
		return game_id
    
	def get_leaderboard(self, limit=10):
		cursor = self.conn.cursor()
        
		cursor.execute('''
		SELECT username, wins, losses, draws, elo_rating,
			   ROUND(wins * 100.0 / total_games, 2) as win_rate
		FROM users 
		WHERE total_games > 0
		ORDER BY elo_rating DESC
		LIMIT ?
		''', (limit,))
        
		return cursor.fetchall()
    
	def close(self):
		self.conn.close()

# Test
if __name__ == "__main__":
	db = CaroDatabase()
	db.register_user("test", "123")
	success, user = db.authenticate_user("test", "123")
	print(f"Auth: {success}, User: {user}")
	db.close()
