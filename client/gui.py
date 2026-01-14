import tkinter as tk
from tkinter import messagebox
from network import NetworkClient  # Yêu cầu file network.py cùng thư mục

class CaroClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Caro Online")
        self.window.geometry("700x750")
        
        # --- KẾT NỐI MẠNG (Core) ---
        self.network = NetworkClient()
        self.network.set_handler(self.handle_server_message)
        # ---------------------------

        # Trạng thái game
        self.username = None
        self.player_symbol = 'X'  # Mặc định, sẽ cập nhật khi vào phòng
        self.current_turn = 'X'
        self.game_active = False
        self.board_size = 15
        self.cell_size = 30
        self.current_room = None
        
        # Setup giao diện
        self.setup_login_frame()
        self.setup_main_menu_frame()
        self.setup_game_frame()
        
        # Mặc định hiện màn hình đăng nhập
        self.show_frame('login')
        
        # Xử lý khi đóng cửa sổ
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def handle_server_message(self, message):
        """Bộ não xử lý tin nhắn từ Server"""
        msg_type = message.get('type')
        print(f"📩 Server: {message}") # Debug log

        if msg_type == 'LOGIN_SUCCESS':
            self.login_status.config(text=message.get('message'), fg='green')
            self.window.after(1000, lambda: self.show_frame('menu'))

        elif msg_type == 'ROOM_CREATED':
            self.current_room = message.get('room_id')
            self.game_status.config(text=f"Room: {self.current_room} - Waiting...")
            self.player_symbol = 'X' # Chủ phòng là X
            self.player_label.config(text="X")
            self.show_frame('game')

        elif msg_type == 'ROOM_JOINED':
            self.current_room = message.get('room_id')
            players = message.get('players', [])
            self.game_status.config(text="Game Started!")
            self.add_chat_message("System", f"Room ready! Players: {', '.join(players)}")
            
            # Người thứ 2 vào phòng là O
            if len(players) == 2 and self.username == players[1]:
                self.player_symbol = 'O'
                self.player_label.config(text="O")
            
            self.game_active = True
            self.current_turn = 'X'
            self.turn_label.config(text='X')

        elif msg_type == 'OPPONENT_MOVE':
            # Vẽ nước đi của đối thủ
            x, y = message.get('x'), message.get('y')
            opponent_symbol = 'O' if self.player_symbol == 'X' else 'X'
            self.draw_piece(x, y, opponent_symbol)
            self.switch_turn()
            self.game_status.config(text="Your Turn!")

        elif msg_type == 'GAME_OVER':
            # Xử lý kết quả trận đấu
            winner = message.get('winner')
            msg_text = message.get('message')
            self.game_active = False
            
            if winner == self.username:
                messagebox.showinfo("VICTORY", f"🏆 {msg_text}")
            elif winner == 'Draw':
                messagebox.showinfo("DRAW", f"🤝 {msg_text}")
            else:
                messagebox.showinfo("DEFEAT", f"💀 {msg_text}")
            
            self.show_frame('menu')

        elif msg_type == 'OPPONENT_LEFT':
            self.game_active = False
            messagebox.showinfo("Disconnected", "Opponent left the game!")
            self.show_frame('menu')

        elif msg_type == 'ERROR':
            messagebox.showerror("Error", message.get('message'))
            self.login_status.config(text=message.get('message'), fg='red')

    # --- PHẦN GIAO DIỆN (UI) ---
    def setup_login_frame(self):
        self.login_frame = tk.Frame(self.window, bg='lightgray')
        
        tk.Label(self.login_frame, text="Caro Online", font=("Arial", 28, "bold"), bg='lightgray').pack(pady=30)
        
        tk.Label(self.login_frame, text="Username:", font=("Arial", 12), bg='lightgray').pack()
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "player1")
        
        tk.Label(self.login_frame, text="Password:", font=("Arial", 12), bg='lightgray').pack()
        self.password_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "123")
        
        btn_frame = tk.Frame(self.login_frame, bg='lightgray')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Login", command=self.login, width=15, bg='green', fg='white').pack(side=tk.LEFT, padx=10)
        
        # Quick Test Buttons (Vẫn giữ để bạn tiện test nhanh)
        test_frame = tk.Frame(self.login_frame, bg='lightgray')
        test_frame.pack(pady=10)
        tk.Label(test_frame, text="Quick Login:", bg='lightgray').pack()
        tk.Button(test_frame, text="Player 1", command=lambda: self.quick_login("player1")).pack(side=tk.LEFT, padx=5)
        tk.Button(test_frame, text="Player 2", command=lambda: self.quick_login("player2")).pack(side=tk.LEFT, padx=5)
        
        self.login_status = tk.Label(self.login_frame, text="", font=("Arial", 10), bg='lightgray', fg='red')
        self.login_status.pack(pady=10)

    def setup_main_menu_frame(self):
        self.menu_frame = tk.Frame(self.window, bg='lightblue')
        self.welcome_label = tk.Label(self.menu_frame, text="", font=("Arial", 20, "bold"), bg='lightblue')
        self.welcome_label.pack(pady=40)
        
        btn_style = {'font': ("Arial", 14), 'width': 25, 'height': 2}
        
        tk.Button(self.menu_frame, text="🎮 Create Room", command=self.create_room, **btn_style).pack(pady=10)
        # Nút Join Room tạm thời fix cứng ID để test, ngày mai mình sẽ làm danh sách phòng
        tk.Button(self.menu_frame, text="🚀 Join Room (ID: room_1)", command=self.join_room_test, **btn_style).pack(pady=10)
        tk.Button(self.menu_frame, text="❌ Logout", command=self.logout, **btn_style).pack(pady=20)

    def setup_game_frame(self):
        self.game_frame = tk.Frame(self.window)
        
        # Top bar
        top_bar = tk.Frame(self.game_frame, bg='gray', height=50)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        self.game_status = tk.Label(top_bar, text="Waiting...", font=("Arial", 12, "bold"), bg='gray', fg='white')
        self.game_status.pack(pady=15)
        
        # Board
        board_size_px = self.board_size * self.cell_size
        self.canvas = tk.Canvas(self.game_frame, width=board_size_px, height=board_size_px, bg='beige')
        self.canvas.pack(pady=20)
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        # Chat & Controls
        bottom_frame = tk.Frame(self.game_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        
        control_frame = tk.LabelFrame(bottom_frame, text="Info", padx=10, pady=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Button(control_frame, text="Quit Game", command=self.back_to_menu, width=15).pack(pady=5)
        
        info_frame = tk.Frame(control_frame)
        info_frame.pack(pady=10)
        tk.Label(info_frame, text="You:", font=("Arial", 10)).pack()
        self.player_label = tk.Label(info_frame, text="X", font=("Arial", 24, "bold"))
        self.player_label.pack()
        tk.Label(info_frame, text="Turn:", font=("Arial", 10)).pack(pady=(10,0))
        self.turn_label = tk.Label(info_frame, text="X", font=("Arial", 24, "bold"))
        self.turn_label.pack()

    # --- CÁC HÀM LOGIC ---
    def draw_board(self):
        self.canvas.delete("all")
        for i in range(self.board_size + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.board_size * self.cell_size, fill="black")
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.board_size * self.cell_size, y, fill="black")

    def draw_piece(self, x, y, player):
        x1, y1 = x * self.cell_size + 5, y * self.cell_size + 5
        x2, y2 = (x + 1) * self.cell_size - 5, (y + 1) * self.cell_size - 5
        if player == 'X':
            self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)
            self.canvas.create_line(x1, y2, x2, y1, fill="red", width=3)
        else:
            self.canvas.create_oval(x1, y1, x2, y2, outline="blue", width=3)

    def on_board_click(self, event):
        if not self.game_active: return
        
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            # Chỉ được đánh khi đến lượt mình
            if self.current_turn == self.player_symbol:
                self.draw_piece(x, y, self.player_symbol)
                # Gửi nước đi lên Server
                self.network.send({
                    'type': 'MOVE',
                    'x': x, 'y': y,
                    'room_id': self.current_room
                })
                self.switch_turn()
                self.game_status.config(text="Opponent's Turn")
            else:
                self.game_status.config(text="Wait for your turn!", fg='red')

    def switch_turn(self):
        self.current_turn = 'O' if self.current_turn == 'X' else 'X'
        self.turn_label.config(text=self.current_turn)

    def login(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        if not u: return
        
        if self.network.connect():
            self.username = u
            self.network.send({'type': 'LOGIN', 'username': u, 'password': p})
            self.login_status.config(text="Connecting...", fg='blue')
        else:
            self.login_status.config(text="Server not found!", fg='red')

    def quick_login(self, name):
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, name)
        self.login()

    def create_room(self):
        self.draw_board()
        self.network.send({'type': 'CREATE_ROOM'})

    def join_room_test(self):
        self.draw_board()
        self.network.send({'type': 'JOIN_ROOM', 'room_id': 'room_1'})

    def send_chat(self, event=None):
        msg = self.chat_input.get().strip()
        if msg:
            self.add_chat_message("You", msg)
            self.chat_input.delete(0, tk.END)
            # Todo: Gửi chat lên server

    def add_chat_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def back_to_menu(self):
        # Tạm thời ngắt kết nối để thoát nhanh
        self.network.disconnect()
        self.show_frame('login')

    def logout(self):
        self.network.disconnect()
        self.show_frame('login')

    def show_frame(self, name):
        for f in [self.login_frame, self.menu_frame, self.game_frame]: f.pack_forget()
        if name == 'login': self.login_frame.pack(fill=tk.BOTH, expand=True)
        elif name == 'menu': self.menu_frame.pack(fill=tk.BOTH, expand=True)
        elif name == 'game': self.game_frame.pack(fill=tk.BOTH, expand=True)

    def on_close(self):
        self.network.disconnect()
        self.window.destroy()

    def run(self):
        self.window.update_idletasks()
        # Center window
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f'{w}x{h}+{x}+{y}')
        self.window.mainloop()

if __name__ == "__main__":
    app = CaroClient()
    app.run()