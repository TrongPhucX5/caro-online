import tkinter as tk
from tkinter import messagebox

class CaroGUI:
	def __init__(self):
		self.window = tk.Tk()
		self.window.title("Caro Online")
		self.window.geometry("600x700")
        
		# Login Frame
		self.login_frame = tk.Frame(self.window)
		self.setup_login()
        
		# Game Frame
		self.game_frame = tk.Frame(self.window)
        
		self.current_frame = self.login_frame
		self.current_frame.pack()
        
	def setup_login(self):
		tk.Label(self.login_frame, text="Caro Online", font=("Arial", 24)).pack(pady=20)
        
		tk.Label(self.login_frame, text="Username:").pack()
		self.username_entry = tk.Entry(self.login_frame, width=30)
		self.username_entry.pack(pady=5)
        
		tk.Label(self.login_frame, text="Password:").pack()
		self.password_entry = tk.Entry(self.login_frame, width=30, show="*")
		self.password_entry.pack(pady=5)
        
		tk.Button(self.login_frame, text="Login", command=self.login, width=20).pack(pady=10)
		tk.Button(self.login_frame, text="Register", command=self.register, width=20).pack()
        
	def setup_game_board(self):
		self.canvas = tk.Canvas(self.game_frame, width=500, height=500, bg="beige")
		self.canvas.pack(pady=20)
		self.draw_board()
        
		# Bind click event
		self.canvas.bind("<Button-1>", self.board_click)
        
		# Status label
		self.status_label = tk.Label(self.game_frame, text="Waiting for opponent...", font=("Arial", 12))
		self.status_label.pack()
        
		# Chat area
		self.chat_text = tk.Text(self.game_frame, height=8, width=50)
		self.chat_text.pack(pady=5)
        
		self.chat_entry = tk.Entry(self.game_frame, width=40)
		self.chat_entry.pack(pady=5)
		tk.Button(self.game_frame, text="Send", command=self.send_chat).pack()
    
	def draw_board(self, size=15):
		cell_size = 500 // size
        
		# Draw grid
		for i in range(size + 1):
			# Vertical lines
			self.canvas.create_line(i * cell_size, 0, i * cell_size, 500, fill="black")
			# Horizontal lines
			self.canvas.create_line(0, i * cell_size, 500, i * cell_size, fill="black")
    
	def board_click(self, event):
		cell_size = 500 // 15
		x = event.x // cell_size
		y = event.y // cell_size
        
		# Draw X or O
		if self.current_player == 1:  # X
			self.draw_x(x, y, cell_size)
		else:  # O
			self.draw_o(x, y, cell_size)
        
		# Send move to server
		self.send_move(x, y)
    
	def draw_x(self, x, y, cell_size):
		padding = cell_size // 4
		x1 = x * cell_size + padding
		y1 = y * cell_size + padding
		x2 = (x + 1) * cell_size - padding
		y2 = (y + 1) * cell_size - padding
        
		self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)
		self.canvas.create_line(x1, y2, x2, y1, fill="red", width=3)
    
	def draw_o(self, x, y, cell_size):
		padding = cell_size // 4
		center_x = x * cell_size + cell_size // 2
		center_y = y * cell_size + cell_size // 2
		radius = cell_size // 2 - padding
        
		self.canvas.create_oval(center_x - radius, center_y - radius,
							   center_x + radius, center_y + radius,
							   outline="blue", width=3)
    
	def login(self):
		username = self.username_entry.get()
		password = self.password_entry.get()
        
		# TODO: Connect to server
		print(f"Login attempt: {username}")
        
		# Switch to game frame
		self.current_frame.pack_forget()
		self.setup_game_board()
		self.game_frame.pack()
		self.current_frame = self.game_frame
    
	def register(self):
		messagebox.showinfo("Register", "Registration feature coming soon!")
    
	def send_move(self, x, y):
		print(f"Move at ({x}, {y})")
    
	def send_chat(self):
		message = self.chat_entry.get()
		if message:
			self.chat_text.insert(tk.END, f"You: {message}\n")
			self.chat_entry.delete(0, tk.END)
    
	def run(self):
		self.window.mainloop()

if __name__ == "__main__":
	app = CaroGUI()
	app.run()
