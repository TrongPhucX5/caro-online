# client/gui.py (HOÀN CHỈNH)
import tkinter as tk
from tkinter import messagebox, ttk
import json

class CaroClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Caro Online")
        self.window.geometry("700x750")
        
        # Game state
        self.username = None
        self.player_symbol = 'X'  # X or O
        self.current_turn = 'X'
        self.game_active = False
        self.board_size = 15
        self.cell_size = 30
        
        # Setup frames
        self.setup_login_frame()
        self.setup_main_menu_frame()
        self.setup_game_frame()
        
        # Show login frame first
        self.show_frame('login')
        
    def setup_login_frame(self):
        """Setup login/register frame"""
        self.login_frame = tk.Frame(self.window, bg='lightgray')
        
        # Title
        title = tk.Label(self.login_frame, text="Caro Online", 
                        font=("Arial", 28, "bold"), bg='lightgray')
        title.pack(pady=30)
        
        # Username
        tk.Label(self.login_frame, text="Username:", 
                font=("Arial", 12), bg='lightgray').pack()
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "player1")  # Default for testing
        
        # Password
        tk.Label(self.login_frame, text="Password:", 
                font=("Arial", 12), bg='lightgray').pack()
        self.password_entry = tk.Entry(self.login_frame, font=("Arial", 12), 
                                      width=25, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "123")  # Default for testing
        
        # Buttons
        btn_frame = tk.Frame(self.login_frame, bg='lightgray')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Login", command=self.login, 
                 width=15, bg='green', fg='white').pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Register", command=self.register, 
                 width=15).pack(side=tk.LEFT, padx=10)
        
        # Quick test buttons
        test_frame = tk.Frame(self.login_frame, bg='lightgray')
        test_frame.pack(pady=10)
        
        tk.Label(test_frame, text="Quick Test:", bg='lightgray').pack()
        test_btn_frame = tk.Frame(test_frame, bg='lightgray')
        test_btn_frame.pack()
        
        tk.Button(test_btn_frame, text="Player 1", command=lambda: self.quick_login("player1"),
                 width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(test_btn_frame, text="Player 2", command=lambda: self.quick_login("player2"),
                 width=10).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.login_status = tk.Label(self.login_frame, text="", 
                                    font=("Arial", 10), bg='lightgray', fg='red')
        self.login_status.pack(pady=10)
    
    def setup_main_menu_frame(self):
        """Setup main menu after login"""
        self.menu_frame = tk.Frame(self.window, bg='lightblue')
        
        # Welcome label
        self.welcome_label = tk.Label(self.menu_frame, text="", 
                                     font=("Arial", 20, "bold"), bg='lightblue')
        self.welcome_label.pack(pady=40)
        
        # Menu buttons
        button_style = {'font': ("Arial", 14), 'width': 25, 'height': 2}
        
        tk.Button(self.menu_frame, text="🎮 Play Online", 
                 command=self.play_online, **button_style).pack(pady=10)
        
        tk.Button(self.menu_frame, text="🤖 Play vs AI", 
                 command=self.play_vs_ai, **button_style).pack(pady=10)
        
        tk.Button(self.menu_frame, text="📊 Leaderboard", 
                 command=self.show_leaderboard, **button_style).pack(pady=10)
        
        tk.Button(self.menu_frame, text="⚙️ Settings", 
                 command=self.show_settings, **button_style).pack(pady=10)
        
        tk.Button(self.menu_frame, text="❌ Logout", 
                 command=self.logout, **button_style).pack(pady=20)
    
    def setup_game_frame(self):
        """Setup game playing frame"""
        self.game_frame = tk.Frame(self.window)
        
        # Top bar with game info
        top_bar = tk.Frame(self.game_frame, bg='gray', height=50)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        
        self.game_status = tk.Label(top_bar, text="Waiting for opponent...", 
                                   font=("Arial", 12, "bold"), bg='gray', fg='white')
        self.game_status.pack(pady=15)
        
        # Game board (Canvas)
        board_size_px = self.board_size * self.cell_size
        self.canvas = tk.Canvas(self.game_frame, width=board_size_px, 
                               height=board_size_px, bg='beige')
        self.canvas.pack(pady=20)
        
        # Draw the board
        self.draw_board()
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        # Bottom frame for chat and controls
        bottom_frame = tk.Frame(self.game_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Chat area
        chat_frame = tk.LabelFrame(bottom_frame, text="Chat", padx=10, pady=10)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.chat_display = tk.Text(chat_frame, height=8, width=30, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        chat_input_frame = tk.Frame(chat_frame)
        chat_input_frame.pack(fill=tk.X, pady=5)
        
        self.chat_input = tk.Entry(chat_input_frame, width=25)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_input.bind("<Return>", self.send_chat)
        
        tk.Button(chat_input_frame, text="Send", command=self.send_chat).pack(side=tk.RIGHT)
        
        # Game controls
        control_frame = tk.LabelFrame(bottom_frame, text="Controls", padx=10, pady=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Button(control_frame, text="Surrender", command=self.surrender,
                 width=15).pack(pady=5)
        tk.Button(control_frame, text="New Game", command=self.new_game,
                 width=15).pack(pady=5)
        tk.Button(control_frame, text="Back to Menu", command=self.back_to_menu,
                 width=15).pack(pady=20)
        
        # Player info
        info_frame = tk.Frame(control_frame)
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text="You:", font=("Arial", 10)).pack()
        self.player_label = tk.Label(info_frame, text="X", font=("Arial", 24, "bold"))
        self.player_label.pack()
        
        tk.Label(info_frame, text="Turn:", font=("Arial", 10)).pack(pady=(10,0))
        self.turn_label = tk.Label(info_frame, text="X", font=("Arial", 24, "bold"))
        self.turn_label.pack()
    
    def draw_board(self):
        """Draw the caro board grid"""
        self.canvas.delete("all")  # Clear canvas
        
        # Draw grid lines
        for i in range(self.board_size + 1):
            # Vertical lines
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.board_size * self.cell_size, 
                                   fill="black", width=1)
            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.board_size * self.cell_size, y, 
                                   fill="black", width=1)
        
        # Draw coordinate labels (optional)
        for i in range(self.board_size):
            x = i * self.cell_size + self.cell_size // 2
            y = self.board_size * self.cell_size + 15
            self.canvas.create_text(x, y, text=str(i), font=("Arial", 8))
            
            y_pos = i * self.cell_size + self.cell_size // 2
            self.canvas.create_text(-15, y_pos, text=str(i), font=("Arial", 8))
    
    def draw_piece(self, x, y, player):
        """Draw X or O at board position (x, y)"""
        # Calculate pixel coordinates
        x1 = x * self.cell_size + 5
        y1 = y * self.cell_size + 5
        x2 = (x + 1) * self.cell_size - 5
        y2 = (y + 1) * self.cell_size - 5
        
        if player == 'X' or player == 1:
            # Draw X (red)
            self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)
            self.canvas.create_line(x1, y2, x2, y1, fill="red", width=3)
        elif player == 'O' or player == 2:
            # Draw O (blue)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            radius = min(x2 - x1, y2 - y1) / 2 - 2
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                   center_x + radius, center_y + radius,
                                   outline="blue", width=3)
    
    def on_board_click(self, event):
        """Handle board click"""
        if not self.game_active:
            messagebox.showinfo("Info", "Game not started yet!")
            return
        
        # Calculate board coordinates
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        # Validate coordinates
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            print(f"Clicked at ({x}, {y})")
            
            # Check if it's player's turn
            if self.current_turn == self.player_symbol:
                # Draw piece
                self.draw_piece(x, y, self.player_symbol)
                
                # Send move to server (TODO)
                # For now, just switch turn
                self.switch_turn()
            else:
                messagebox.showinfo("Not your turn", "Wait for opponent's move!")
    
    def switch_turn(self):
        """Switch turn between X and O"""
        if self.current_turn == 'X':
            self.current_turn = 'O'
        else:
            self.current_turn = 'X'
        
        self.turn_label.config(text=self.current_turn)
        self.game_status.config(text=f"{self.current_turn}'s turn")
    
    def show_frame(self, frame_name):
        """Show specific frame"""
        frames = {
            'login': self.login_frame,
            'menu': self.menu_frame,
            'game': self.game_frame
        }
        
        # Hide all frames
        for frame in frames.values():
            frame.pack_forget()
        
        # Show requested frame
        frames[frame_name].pack(fill=tk.BOTH, expand=True)
    
    def quick_login(self, username):
        """Quick login for testing"""
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, "123")
        self.login()
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.login_status.config(text="Please enter username and password")
            return
        
        # TODO: Connect to server for authentication
        # For now, simulate successful login
        self.username = username
        self.login_status.config(text="Login successful!", fg='green')
        
        # Update welcome message
        self.welcome_label.config(text=f"Welcome, {username}!")
        
        # Switch to main menu after short delay
        self.window.after(1000, lambda: self.show_frame('menu'))
    
    def register(self):
        """Handle registration"""
        messagebox.showinfo("Registration", 
                          "Registration feature will be implemented soon!\n" +
                          "For now, use: player1/123 or player2/123")
    
    def play_online(self):
        """Start online game"""
        self.game_status.config(text="Looking for opponent...")
        self.show_frame('game')
        
        # For testing, start game immediately
        self.window.after(2000, self.start_test_game)
    
    def play_vs_ai(self):
        """Play against AI"""
        messagebox.showinfo("AI Mode", "AI mode coming soon!\nPlaying online for now.")
        self.play_online()
    
    def show_leaderboard(self):
        """Show leaderboard"""
        messagebox.showinfo("Leaderboard", 
                          "Leaderboard feature coming soon!\n" +
                          "Currently in development.")
    
    def show_settings(self):
        """Show settings"""
        messagebox.showinfo("Settings", 
                          "Settings feature coming soon!\n" +
                          "Default: 15x15 board, X goes first.")
    
    def logout(self):
        """Logout and return to login screen"""
        self.username = None
        self.show_frame('login')
    
    def start_test_game(self):
        """Start a test game (for development)"""
        self.game_active = True
        self.player_symbol = 'X'  # First player is X
        self.current_turn = 'X'   # X goes first
        
        self.player_label.config(text=self.player_symbol)
        self.turn_label.config(text=self.current_turn)
        self.game_status.config(text=f"Your turn! You are {self.player_symbol}")
        
        # Add welcome message to chat
        self.add_chat_message("System", "Game started! X goes first.")
        self.add_chat_message("System", "Click on the board to place your piece.")
    
    def send_chat(self, event=None):
        """Send chat message"""
        message = self.chat_input.get().strip()
        if message:
            self.add_chat_message("You", message)
            self.chat_input.delete(0, tk.END)
            
            # TODO: Send to server
            # For now, just echo
            self.window.after(1000, lambda: self.add_chat_message("Opponent", "I see your message!"))
    
    def add_chat_message(self, sender, message):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def surrender(self):
        """Surrender current game"""
        if messagebox.askyesno("Surrender", "Are you sure you want to surrender?"):
            self.add_chat_message("System", "You surrendered!")
            self.game_active = False
            self.game_status.config(text="Game over - You surrendered")
    
    def new_game(self):
        """Start new game"""
        if messagebox.askyesno("New Game", "Start a new game?"):
            # Clear board
            self.canvas.delete("all")
            self.draw_board()
            
            # Reset game state
            self.game_active = True
            self.player_symbol = 'O' if self.player_symbol == 'X' else 'X'  # Switch sides
            self.current_turn = 'X'  # X always starts
            
            self.player_label.config(text=self.player_symbol)
            self.turn_label.config(text=self.current_turn)
            
            # Clear chat
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            self.add_chat_message("System", f"New game started! You are {self.player_symbol}")
            self.game_status.config(text=f"{self.current_turn}'s turn - You are {self.player_symbol}")
    
    def back_to_menu(self):
        """Return to main menu"""
        if self.game_active:
            if not messagebox.askyesno("Leave Game", "Game in progress. Leave anyway?"):
                return
        
        self.show_frame('menu')
    
    def run(self):
        """Run the application"""
        # Center window on screen
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.window.mainloop()

if __name__ == "__main__":
    app = CaroClient()
    app.run()