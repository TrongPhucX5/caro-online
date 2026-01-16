# client/views/game_view.py
import tkinter as tk
from tkinter import messagebox


class GameView:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = tk.Frame(parent, bg='#444')
        
        self.canvas = None
        self.chat_display = None
        self.chat_input = None
        self.game_status = None
        self.player_label = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create game interface"""
        # Top status bar
        top = tk.Frame(self.frame, bg='#333')
        top.pack(fill=tk.X)
        
        self.game_status = tk.Label(top, text="Waiting...",
                                    fg='white', bg='#333',
                                    font=("Segoe UI", 14))
        self.game_status.pack(pady=10)
        
        # Main content
        main = tk.Frame(self.frame, bg='#444')
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Game board
        state = self.controller.get_game_state()
        board_size = state['board_size']
        cell_size = state['cell_size']
        px = board_size * cell_size
        
        self.canvas = tk.Canvas(main, width=px, height=px, bg='#fff8e1')
        self.canvas.pack(side=tk.LEFT, padx=(0, 20))
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        # Right panel
        right = tk.Frame(main, bg='#444')
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Player info
        info = tk.LabelFrame(right, text="Info", bg='#444', fg='white')
        info.pack(fill=tk.X)
        self.player_label = tk.Label(info, text="You: ?", bg='#444', fg='white')
        self.player_label.pack()
        
        # Chat box
        chat = tk.LabelFrame(right, text="Chat", bg='#444', fg='white')
        chat.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.chat_display = tk.Text(chat, state=tk.DISABLED, bg='#555', fg='white')
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Chat input
        input_box = tk.Frame(chat, bg='#444')
        input_box.pack(fill=tk.X)
        
        self.chat_input = tk.Entry(input_box)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_input.bind("<Return>", self.send_chat)
        
        tk.Button(input_box, text="Send", command=self.send_chat).pack(side=tk.RIGHT)
        
        # Bottom controls
        bottom = tk.Frame(self.frame, bg='#444')
        bottom.pack(fill=tk.X)
        
        tk.Button(bottom, text="Surrender", command=self.surrender,
                  bg='#fbc02d').pack(side=tk.RIGHT, padx=5)
        tk.Button(bottom, text="Quit", command=self.leave_game,
                  bg='#e53935', fg='white').pack(side=tk.RIGHT)
                  
    def draw_board(self):
        """Draw the game board"""
        state = self.controller.get_game_state()
        board_size = state['board_size']
        cell_size = state['cell_size']
        
        self.canvas.delete("all")
        for i in range(board_size + 1):
            p = i * cell_size
            self.canvas.create_line(p, 0, p, board_size * cell_size)
            self.canvas.create_line(0, p, board_size * cell_size, p)
            
    def draw_piece(self, x, y, player):
        """Draw game piece"""
        state = self.controller.get_game_state()
        cell_size = state['cell_size']
        
        x1, y1 = x * cell_size + 4, y * cell_size + 4
        x2, y2 = (x + 1) * cell_size - 4, (y + 1) * cell_size - 4
        
        if player == 'X':
            self.canvas.create_line(x1, y1, x2, y2, fill='red', width=3)
            self.canvas.create_line(x1, y2, x2, y1, fill='red', width=3)
        else:
            self.canvas.create_oval(x1, y1, x2, y2, outline='blue', width=3)
            
    def on_board_click(self, event):
        """Handle board click"""
        if not self.controller.game_active:
            return
            
        state = self.controller.get_game_state()
        cell_size = state['cell_size']
        current_turn = state['current_turn']
        player_symbol = state['player_symbol']
        
        if current_turn == player_symbol:
            x, y = event.x // cell_size, event.y // cell_size
            self.draw_piece(x, y, player_symbol)
            self.controller.send_move(x, y)
            self.controller.switch_turn()
            
    def send_chat(self, event=None):
        """Send chat message"""
        msg = self.chat_input.get().strip()
        if msg:
            self.add_chat_message("You", msg)
            self.chat_input.delete(0, tk.END)
            self.controller.send_chat(msg)
            
    def add_chat_message(self, sender, msg):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {msg}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def surrender(self):
        """Surrender game"""
        self.controller.surrender()
        
    def leave_game(self):
        """Leave current game"""
        self.controller.show_view('lobby')
        
    def handle_message(self, message):
        """Handle server messages"""
        msg_type = message.get('type')
        
        if msg_type == 'ROOM_CREATED':
            room_id = message.get('room_id')
            player_symbol = message.get('player_symbol', 'X') # Default to 'X'
            self.controller.set_game_state(room_id, player_symbol, True)
            self.player_label.config(text=f"You: {player_symbol}")
            self.draw_board()
            self.game_status.config(text=f"Room {room_id} - Waiting for opponent...")
            self.controller.show_view('game')
            
        elif msg_type == 'ROOM_JOINED':
            room_id = message.get('room_id')
            players = message.get('players', [])
            player_symbol = message.get('player_symbol') # Get symbol from server

            if player_symbol:
                self.controller.set_game_state(room_id, player_symbol, True)
                self.player_label.config(text=f"You: {player_symbol}")
            
            self.game_status.config(text="Game Started! Your turn.")
            self.draw_board()
            self.add_chat_message("System", f"Players: {', '.join(players)}")
            self.controller.show_view('game')
            
        elif msg_type == 'OPPONENT_MOVE':
            x, y = message.get('x'), message.get('y')
            opp_symbol = 'O' if self.controller.player_symbol == 'X' else 'X'
            self.draw_piece(x, y, opp_symbol)
            self.controller.switch_turn()
            self.game_status.config(text="Your turn")
            
        elif msg_type == 'GAME_OVER':
            self.controller.game_active = False
            winner = message.get('winner')
            
            if winner == self.controller.username:
                messagebox.showinfo("Victory", "🏆 You Won!")
            elif winner == 'Draw':
                messagebox.showinfo("Draw", "🤝 Draw!")
            else:
                messagebox.showinfo("Defeat", "💀 You Lost!")
                
            self.controller.show_view('lobby')
            
        elif msg_type == 'OPPONENT_LEFT':
            self.controller.game_active = False
            messagebox.showinfo("Info", "Opponent disconnected")
            self.controller.show_view('lobby')
            
        elif msg_type == 'CHAT':
            self.add_chat_message(message.get('sender'), message.get('message'))
            
    def show(self):
        """Show this view"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
    def hide(self):
        """Hide this view"""
        self.frame.pack_forget()