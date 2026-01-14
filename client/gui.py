# client/gui.py (NGÀY 3: LOBBY SYSTEM)
import tkinter as tk
from tkinter import messagebox, ttk # Import thêm ttk để làm bảng đẹp
from network import NetworkClient

class CaroClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Caro Online")
        self.window.geometry("800x600") # Mở rộng cửa sổ một chút
        
        # Network
        self.network = NetworkClient()
        self.network.set_handler(self.handle_server_message)

        # State
        self.username = None
        self.player_symbol = 'X'
        self.current_turn = 'X'
        self.game_active = False
        self.board_size = 15
        self.cell_size = 30
        self.current_room = None
        
        # Setup UI
        self.setup_login_frame()
        self.setup_lobby_frame() # Thay Menu bằng Lobby
        self.setup_game_frame()
        
        self.show_frame('login')
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def handle_server_message(self, message):
        msg_type = message.get('type')
        print(f"📩 Server: {message}")

        if msg_type == 'LOGIN_SUCCESS':
            self.login_status.config(text="Success!", fg='green')
            self.username = self.username_entry.get() # Lưu username
            self.window.after(500, lambda: self.show_frame('lobby'))
            # Tự động tải danh sách phòng khi vào lobby
            self.window.after(600, self.refresh_rooms)

        elif msg_type == 'ROOM_LIST':
            # Cập nhật bảng danh sách phòng
            rooms = message.get('rooms', [])
            self.update_room_list(rooms)

        elif msg_type == 'ROOM_CREATED':
            self.current_room = message.get('room_id')
            self.player_symbol = 'X'
            self.player_label.config(text="X (You)")
            self.show_frame('game')
            self.game_status.config(text=f"Room: {self.current_room} - Waiting...")

        elif msg_type == 'ROOM_JOINED':
            self.current_room = message.get('room_id')
            players = message.get('players', [])
            self.game_active = True
            
            # Setup biểu tượng
            if self.username == players[0]:
                self.player_symbol = 'X'
            else:
                self.player_symbol = 'O'
            
            self.player_label.config(text=f"{self.player_symbol} (You)")
            self.game_status.config(text="Game Started!")
            self.show_frame('game')
            # self.add_chat_message("System", f"Joined {self.current_room}. Players: {', '.join(players)}")

        elif msg_type == 'OPPONENT_MOVE':
            x, y = message.get('x'), message.get('y')
            opp_symbol = 'O' if self.player_symbol == 'X' else 'X'
            self.draw_piece(x, y, opp_symbol)
            self.switch_turn()
            self.game_status.config(text="Your Turn!")

        elif msg_type == 'GAME_OVER':
            self.game_active = False
            winner = message.get('winner')
            msg = message.get('message')
            
            if winner == self.username:
                messagebox.showinfo("Victory", "🏆 You Won!")
            elif winner == 'Draw':
                messagebox.showinfo("Draw", "🤝 It's a Draw!")
            else:
                messagebox.showinfo("Defeat", "💀 You Lost!")
            
            self.show_frame('lobby')
            self.refresh_rooms() # Cập nhật lại trạng thái phòng

        elif msg_type == 'OPPONENT_LEFT':
            self.game_active = False
            messagebox.showinfo("Info", "Opponent disconnected!")
            self.show_frame('lobby')
            self.refresh_rooms()

        elif msg_type == 'ERROR':
            messagebox.showerror("Error", message.get('message'))

    # --- UI SETUP ---
    def setup_login_frame(self):
        self.login_frame = tk.Frame(self.window, bg='#f0f0f0')
        
        tk.Label(self.login_frame, text="CARO ONLINE", font=("Helvetica", 32, "bold"), bg='#f0f0f0', fg='#333').pack(pady=50)
        
        frame = tk.Frame(self.login_frame, bg='#f0f0f0')
        frame.pack()
        
        tk.Label(frame, text="Username:", font=("Arial", 12), bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(frame, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.username_entry.insert(0, "player1")
        
        tk.Label(frame, text="Password:", font=("Arial", 12), bg='#f0f0f0').grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(frame, font=("Arial", 12), show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.password_entry.insert(0, "123")
        
        tk.Button(self.login_frame, text="LOGIN", command=self.login, bg='#4CAF50', fg='white', font=("Arial", 12, "bold"), width=20).pack(pady=20)
        
        self.login_status = tk.Label(self.login_frame, text="", bg='#f0f0f0', fg='red')
        self.login_status.pack()

    def setup_lobby_frame(self):
        """Giao diện sảnh chờ (Thay thế Menu cũ)"""
        self.lobby_frame = tk.Frame(self.window, bg='#e0e0e0')
        
        # Header
        header = tk.Frame(self.lobby_frame, bg='#2196F3', height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="GAME LOBBY", font=("Arial", 18, "bold"), bg='#2196F3', fg='white').pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(header, text="Logout", command=self.logout, bg='#f44336', fg='white').pack(side=tk.RIGHT, padx=20)

        # Toolbar
        toolbar = tk.Frame(self.lobby_frame, bg='#e0e0e0')
        toolbar.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(toolbar, text="🔄 Refresh", command=self.refresh_rooms, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="➕ Create Room", command=self.create_room, bg='#4CAF50', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="▶ Join Selected", command=self.join_selected_room, bg='#2196F3', fg='white', width=15).pack(side=tk.LEFT, padx=5)

        # Room List (Table)
        list_frame = tk.Frame(self.lobby_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview (Bảng)
        columns = ('id', 'status', 'players')
        self.room_tree = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        
        self.room_tree.heading('id', text='Room ID')
        self.room_tree.heading('status', text='Status')
        self.room_tree.heading('players', text='Players')
        
        self.room_tree.column('id', width=150)
        self.room_tree.column('status', width=100)
        self.room_tree.column('players', width=100)
        
        self.room_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.room_tree.yview)

    def setup_game_frame(self):
        self.game_frame = tk.Frame(self.window, bg='gray')
        
        # Top Bar
        top = tk.Frame(self.game_frame, bg='#333')
        top.pack(fill=tk.X)
        
        self.game_status = tk.Label(top, text="Waiting...", fg='white', bg='#333', font=("Arial", 14))
        self.game_status.pack(pady=10)
        
        # Board Area
        center = tk.Frame(self.game_frame)
        center.pack()
        
        px = self.board_size * self.cell_size
        self.canvas = tk.Canvas(center, width=px, height=px, bg='#fff8e1') # Màu bàn cờ dịu mắt hơn
        self.canvas.pack(padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        # Bottom Controls
        bottom = tk.Frame(self.game_frame, bg='gray')
        bottom.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(bottom, text="Quit Game", command=self.leave_game, bg='#f44336', fg='white').pack(side=tk.RIGHT)
        
        info = tk.Frame(bottom, bg='gray')
        info.pack(side=tk.LEFT)
        self.player_label = tk.Label(info, text="You: ?", bg='gray', fg='white', font=("Arial", 12, "bold"))
        self.player_label.pack(anchor='w')

    # --- LOGIC ---
    def login(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        if u and self.network.connect():
            self.network.send({'type': 'LOGIN', 'username': u, 'password': p})

    def refresh_rooms(self):
        """Gửi yêu cầu lấy danh sách phòng"""
        self.network.send({'type': 'GET_ROOMS'})

    def update_room_list(self, rooms):
        """Hiển thị danh sách phòng lên bảng"""
        # Xóa hết dữ liệu cũ
        for item in self.room_tree.get_children():
            self.room_tree.delete(item)
            
        # Thêm dữ liệu mới
        for room in rooms:
            r_id = room['id']
            status = room['status']
            count = f"{room['count']}/2"
            self.room_tree.insert('', tk.END, values=(r_id, status, count))

    def create_room(self):
        self.network.send({'type': 'CREATE_ROOM'})
        self.draw_board()

    def join_selected_room(self):
        selected = self.room_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a room to join!")
            return
        
        item = self.room_tree.item(selected[0])
        room_id = item['values'][0] # Lấy cột đầu tiên (ID)
        status = item['values'][1]
        
        if status == 'playing':
            messagebox.showerror("Error", "Room is already full!")
            return
            
        self.network.send({'type': 'JOIN_ROOM', 'room_id': room_id})
        self.draw_board()

    def leave_game(self):
        if messagebox.askyesno("Quit", "Leave this game?"):
            self.network.disconnect() # Ngắt kết nối để thoát nhanh (Logic đơn giản)
            self.show_frame('login') # Quay về login (Reset)

    def logout(self):
        self.network.disconnect()
        self.show_frame('login')

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(self.board_size + 1):
            p = i * self.cell_size
            self.canvas.create_line(p, 0, p, self.board_size * self.cell_size, fill="#ccc")
            self.canvas.create_line(0, p, self.board_size * self.cell_size, p, fill="#ccc")

    def draw_piece(self, x, y, player):
        x1, y1 = x * self.cell_size + 4, y * self.cell_size + 4
        x2, y2 = (x + 1) * self.cell_size - 4, (y + 1) * self.cell_size - 4
        if player == 'X':
            self.canvas.create_line(x1, y1, x2, y2, fill='red', width=3)
            self.canvas.create_line(x1, y2, x2, y1, fill='red', width=3)
        else:
            self.canvas.create_oval(x1, y1, x2, y2, outline='blue', width=3)

    def on_board_click(self, event):
        if not self.game_active: return
        x, y = event.x // self.cell_size, event.y // self.cell_size
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            if self.current_turn == self.player_symbol:
                self.draw_piece(x, y, self.player_symbol)
                self.network.send({'type': 'MOVE', 'x': x, 'y': y, 'room_id': self.current_room})
                self.switch_turn()
            else:
                self.game_status.config(text="Wait for your turn!", fg='red')

    def switch_turn(self):
        self.current_turn = 'O' if self.current_turn == 'X' else 'X'

    def show_frame(self, name):
        for f in [self.login_frame, self.lobby_frame, self.game_frame]: f.pack_forget()
        if name == 'login': self.login_frame.pack(fill=tk.BOTH, expand=True)
        elif name == 'lobby': self.lobby_frame.pack(fill=tk.BOTH, expand=True)
        elif name == 'game': self.game_frame.pack(fill=tk.BOTH, expand=True)

    def on_close(self):
        self.network.disconnect()
        self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    CaroClient().run()