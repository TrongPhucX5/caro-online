import tkinter as tk
from tkinter import messagebox
from sound_manager import SoundManager

class GameView:
    def __init__(self, parent, controller):
        self.controller = controller
        
        # --- CẤU HÌNH MÀU SẮC (THEME HIỆN ĐẠI) ---
        self.colors = {
            'bg_main': '#f3f4f6',       # Nền tổng thể
            'board_bg': '#ffffff',      # Nền bàn cờ
            'panel_bg': '#ffffff',      # Nền bảng điều khiển phải
            'primary': '#2563eb',       # Xanh chủ đạo
            'text_dark': '#1f2937',     # Chữ đen
            'border': '#e5e7eb',        # Viền
            'x_color': '#ef4444',       # Màu quân X (Đỏ)
            'o_color': '#3b82f6',       # Màu quân O (Xanh)
            'highlight': '#fef3c7'      # Màu ô vừa đánh (Vàng nhạt)
        }
        
        self.frame = tk.Frame(parent, bg=self.colors['bg_main'])
        
        self.canvas = None
        self.chat_display = None
        self.chat_input = None
        self.game_status = None
        self.player_label = None
        self.turn_indicator = None
        self.overlay = None # Lưu overlay kết quả để xóa khi cần
        self.timer_id = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo giao diện Game hiện đại"""
        container = tk.Frame(self.frame, bg=self.colors['bg_main'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # --- CỘT TRÁI: BÀN CỜ ---
        left_panel = tk.Frame(container, bg=self.colors['bg_main'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Status Bar phía trên bàn cờ
        status_frame = tk.Frame(left_panel, bg=self.colors['bg_main'])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.game_status = tk.Label(status_frame, text="Đang chờ đối thủ...",
                                    fg=self.colors['text_dark'], bg=self.colors['bg_main'],
                                    font=("Segoe UI", 14, "bold"))
        self.game_status.pack(side=tk.LEFT)
        
        self.turn_indicator = tk.Label(status_frame, text="", 
                                       fg=self.colors['primary'], bg=self.colors['bg_main'],
                                       font=("Segoe UI", 11, "italic"))
        self.turn_indicator.pack(side=tk.RIGHT)
        
        # Timer Label
        self.timer_label = tk.Label(status_frame, text="30s", 
                                    fg=self.colors['text_dark'], bg=self.colors['bg_main'],
                                    font=("Segoe UI", 12, "bold"), width=6)
        self.timer_label.pack(side=tk.RIGHT, padx=10)

        # Canvas Bàn cờ
        board_frame = tk.Frame(left_panel, bg='white', bd=1, relief=tk.SOLID)
        board_frame.config(highlightbackground=self.colors['border'], highlightthickness=1, bd=0)
        board_frame.pack(anchor='center') 
        
        state = self.controller.get_game_state()
        board_size = state['board_size']
        cell_size = state['cell_size']
        px = board_size * cell_size
        
        self.canvas = tk.Canvas(board_frame, width=px, height=px, bg=self.colors['board_bg'], highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        # --- CỘT PHẢI: THÔNG TIN & CHAT ---
        right_panel = tk.Frame(container, bg=self.colors['bg_main'], width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        right_panel.pack_propagate(False) 
        
        # 1. Info Card
        info_card = tk.Frame(right_panel, bg='white', padx=15, pady=15)
        info_card.pack(fill=tk.X, pady=(0, 15))
        info_card.config(highlightbackground=self.colors['border'], highlightthickness=1)
        
        tk.Label(info_card, text="Thông tin trận đấu", font=("Segoe UI", 11, "bold"), bg='white').pack(anchor='w')
        tk.Frame(info_card, bg=self.colors['border'], height=1).pack(fill=tk.X, pady=5)
        
        self.player_label = tk.Label(info_card, text="Bạn là: ?", font=("Segoe UI", 10), bg='white', fg='#4b5563')
        self.player_label.pack(anchor='w')
        
        btn_frame = tk.Frame(info_card, bg='white', pady=10)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="🏳️ Đầu hàng", command=self.surrender,
                  bg='#fef3c7', fg='#d97706', relief=tk.FLAT, width=12).pack(side=tk.LEFT, padx=(0, 5))
                  
        tk.Button(btn_frame, text="🚪 Rời phòng", command=self.leave_game,
                  bg='#fee2e2', fg='#ef4444', relief=tk.FLAT, width=12).pack(side=tk.RIGHT)

        # 2. Chat Box
        chat_card = tk.Frame(right_panel, bg='white', padx=15, pady=15)
        chat_card.pack(fill=tk.BOTH, expand=True)
        chat_card.config(highlightbackground=self.colors['border'], highlightthickness=1)
        
        tk.Label(chat_card, text="Trò chuyện", font=("Segoe UI", 11, "bold"), bg='white').pack(anchor='w')
        tk.Frame(chat_card, bg=self.colors['border'], height=1).pack(fill=tk.X, pady=5)
        
        self.chat_display = tk.Text(chat_card, state=tk.DISABLED, bg='#f9fafb', fg='#374151',
                                    font=("Segoe UI", 9), relief=tk.FLAT, padx=5, pady=5)
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        input_frame = tk.Frame(chat_card, bg='white')
        input_frame.pack(fill=tk.X)
        
        self.chat_input = tk.Entry(input_frame, font=("Segoe UI", 10), relief=tk.SOLID, bd=1)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.chat_input.bind("<Return>", self.send_chat)
        
        tk.Button(input_frame, text="Gửi", command=self.send_chat,
                  bg=self.colors['primary'], fg='white', relief=tk.FLAT).pack(side=tk.RIGHT, padx=(5, 0))

    # --- HÀM VẼ ---
    def draw_board(self):
        # Nếu có overlay cũ thì xóa đi
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            
        state = self.controller.get_game_state()
        board_size = state['board_size']
        cell_size = state['cell_size']
        
        self.canvas.delete("all")
        for i in range(board_size + 1):
            p = i * cell_size
            self.canvas.create_line(p, 0, p, board_size * cell_size, fill='#e5e7eb')
            self.canvas.create_line(0, p, board_size * cell_size, p, fill='#e5e7eb')

    def draw_piece(self, x, y, player):
        state = self.controller.get_game_state()
        cell_size = state['cell_size']
        
        self.canvas.delete("highlight")
        x1, y1 = x * cell_size + 1, y * cell_size + 1
        x2, y2 = (x + 1) * cell_size - 1, (y + 1) * cell_size - 1
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors['highlight'], outline='', tags="highlight")
        self.canvas.tag_lower("highlight")
        
        p = 6 
        x1, y1 = x * cell_size + p, y * cell_size + p
        x2, y2 = (x + 1) * cell_size - p, (y + 1) * cell_size - p
        
        if player == 'X':
            self.canvas.create_line(x1, y1, x2, y2, fill=self.colors['x_color'], width=3, capstyle=tk.ROUND)
            self.canvas.create_line(x1, y2, x2, y1, fill=self.colors['x_color'], width=3, capstyle=tk.ROUND)
            SoundManager.play_move_x()
        else:
            self.canvas.create_oval(x1, y1, x2, y2, outline=self.colors['o_color'], width=3)
            SoundManager.play_move_o()

    def on_board_click(self, event):
        # KHÓA CLICK: Nếu game chưa active -> Chặn
        if not self.controller.game_active:
            # Chỉ hiện thông báo nếu đang đợi người chơi, còn nếu hết game thì thôi
            if "waiting" in self.game_status.cget("text").lower():
                messagebox.showinfo("Chờ đối thủ", "Vui lòng đợi người chơi khác vào phòng!")
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
            self.update_turn_indicator()
            self.start_timer()

    # --- CÁC HÀM CHỨC NĂNG ---
    def leave_game(self):
        """Xử lý rời phòng thông minh hơn"""
        # CHỈ CẢNH BÁO NẾU GAME ĐANG DIỄN RA (Active = True)
        if self.controller.game_active:
            if not messagebox.askyesno("Rời phòng", "Trận đấu đang diễn ra. Nếu thoát bạn sẽ bị xử thua. Tiếp tục?"):
                return # Nếu chọn No thì hủy lệnh thoát

        # Nếu game đã kết thúc (Active = False), code sẽ chạy thẳng xuống đây -> Thoát luôn
        try:
            self.controller.network.send({
                'type': 'LEAVE_ROOM',
                'room_id': self.controller.current_room
            })
        except:
            pass
            
        self.controller.game_active = False
        self.controller.current_room = None
        self.controller.show_view('lobby')

    def surrender(self):
        if self.controller.game_active and messagebox.askyesno("Đầu hàng", "Chấp nhận thua cuộc?"):
            self.controller.surrender()

    def request_rematch(self):
        """Gửi yêu cầu chơi lại"""
        self.controller.network.send({
            'type': 'PLAY_AGAIN',
            'room_id': self.controller.current_room
        })
        self.game_status.config(text="Đã gửi yêu cầu chơi lại...", fg=self.colors['primary'])
        
        # Xóa overlay nếu có
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def send_chat(self, event=None):
        msg = self.chat_input.get().strip()
        if msg:
            self.add_chat_message("Bạn", msg)
            self.chat_input.delete(0, tk.END)
            self.controller.send_chat(msg)
            
    def add_chat_message(self, sender, msg):
        self.chat_display.config(state=tk.NORMAL)
        tag = "me" if sender == "Bạn" else "other"
        self.chat_display.insert(tk.END, f"{sender}: ", ("bold", tag))
        self.chat_display.insert(tk.END, f"{msg}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def update_turn_indicator(self):
        state = self.controller.get_game_state()
        
        # Nếu là khán giả
        if state['player_symbol'] is None:
             self.turn_indicator.config(text=f"Lượt của {state['current_turn']}", fg='gray')
             return

        if state['current_turn'] == state['player_symbol']:
            self.turn_indicator.config(text="✨ Đến lượt bạn!", fg=self.colors['primary'])
        else:
            self.turn_indicator.config(text="⏳ Đợi đối thủ...", fg=self.colors['text_dark'])

    # --- HÀM HIỂN THỊ KẾT QUẢ (OVERLAY) ---
    def show_result_overlay(self, result_type, winner=None):
        """Hiển thị bảng kết quả ngay trên bàn cờ"""
        # Tạo Frame phủ lên bàn cờ (Overlay)
        # Lưu ý: width/height phải khớp với kích thước canvas (15*30 = 450)
        state = self.controller.get_game_state()
        px = state['board_size'] * state['cell_size']
        
        self.overlay = tk.Frame(self.canvas, bg='') # bg rỗng để trong suốt (nhưng tk cơ bản ko hỗ trợ tốt)
        # Mẹo: Dùng place đè lên frame bàn cờ
        
        # Tạo một Container nổi ở giữa màn hình (giả lập popup)
        result_box = tk.Frame(self.frame, bg='white', padx=4, pady=4)
        result_box.place(relx=0.5, rely=0.5, anchor='center', width=300, height=200)
        result_box.config(highlightbackground="#2563eb", highlightthickness=2)
        
        # Lưu tham chiếu để xóa sau này
        self.overlay = result_box
        
        inner = tk.Frame(result_box, bg='white')
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if result_type == 'WIN':
            text, color, msg = "🏆 CHIẾN THẮNG!", "#10b981", "Bạn chơi quá hay!"
            SoundManager.play_win()
        elif result_type == 'LOSE':
            text, color, msg = "💀 THẤT BẠI!", "#ef4444", "Đừng buồn, thử lại nào!"
            SoundManager.play_lose()
        elif result_type == 'SPECTATOR':
            if winner == 'Draw':
                text, color, msg = "🤝 TRẬN ĐẤU KẾT THÚC!", "#f59e0b", "Hai bên hòa nhau!"
            else:
                text, color, msg = "🏁 TRẬN ĐẤU KẾT THÚC!", "#2563eb", f"Người thắng: {winner}"
            SoundManager.play_notify()
        else:
            text, color, msg = "🤝 HÒA CỜ!", "#f59e0b", "Trận đấu cân não!"
            SoundManager.play_notify()
            
        tk.Label(inner, text=text, font=("Segoe UI", 18, "bold"), fg=color, bg='white').pack(pady=(0, 10))
        tk.Label(inner, text=msg, font=("Segoe UI", 10), fg="#4b5563", bg='white').pack(pady=(0, 20))
        
        btn_frame = tk.Frame(inner, bg='white')
        btn_frame.pack(fill=tk.X)
        
        # Chỉ hiện nút Chơi lại nếu không phải khán giả
        if result_type != 'SPECTATOR':
            tk.Button(btn_frame, text="🔄 Chơi lại", 
                    command=self.request_rematch,
                    bg=self.colors['primary'], fg='white', font=("Segoe UI", 9, "bold"),
                    relief=tk.FLAT, width=10, height=2).pack(side=tk.LEFT, padx=5)
        else:
            # Nếu là khán giả, nút Thoát căn giữa hoặc full
            pass 
                  
        tk.Button(btn_frame, text="🚪 Thoát", 
                  command=lambda: [result_box.destroy(), self.leave_game()],
                  bg="#e5e7eb", fg="black", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, width=10, height=2).pack(side=tk.RIGHT if result_type != 'SPECTATOR' else tk.TOP, padx=5, fill=tk.X if result_type == 'SPECTATOR' else tk.NONE)

    # --- TIMER LOGIC ---
    def start_timer(self):
        try:
            val = int(self.controller.time_limit)
            self.remaining_time = val
        except:
            self.remaining_time = 30 # Fallback default
            
        self.update_timer_display()
        
        if self.timer_id:
            try:
                self.frame.after_cancel(self.timer_id)
            except: pass
            self.timer_id = None
            
        self.run_timer()
        
    def run_timer(self):
        try:
            if not self.controller.game_active:
                return
                
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.update_timer_display()
                self.timer_id = self.frame.after(1000, self.run_timer)
            else:
                # Hết giờ client tự hiểu là server sẽ xử lý
                self.timer_label.config(text="0s", fg='red')
        except Exception as e:
            print(f"Timer error: {e}")
            self.timer_id = None
            
    def update_timer_display(self):
        self.timer_label.config(text=f"{self.remaining_time}s")
        if self.remaining_time <= 5:
            self.timer_label.config(fg='#ef4444') # Đỏ khi sắp hết
        else:
            self.timer_label.config(fg=self.colors['text_dark'])

    # --- XỬ LÝ MESSAGE ---
    def handle_message(self, message):
        msg_type = message.get('type')
        
        if msg_type == 'ROOM_CREATED':
            room_id = message.get('room_id')
            # Set False vì chưa có người thứ 2
            self.controller.set_game_state(room_id, 'X', False)
            self.player_label.config(text="Bạn cầm quân: X (Đỏ)", fg=self.colors['x_color'])
            self.draw_board()
            self.game_status.config(text=f"Phòng chờ...", fg=self.colors['text_dark'])
            self.turn_indicator.config(text="⏳ Đang đợi người vào...", fg='gray')
            self.timer_label.config(text="--") # Reset timer label
            self.controller.show_view('game')
            
        elif msg_type == 'ROOM_JOINED':
            room_id = message.get('room_id')
            players = message.get('players', [])
            player_symbol = message.get('player_symbol')
            
            # Cập nhật Time Limit
            self.controller.time_limit = message.get('time_limit', 30)

            if player_symbol:
                # Có đủ 2 người -> Set True để chơi
                self.controller.set_game_state(room_id, player_symbol, True)
                color = self.colors['x_color'] if player_symbol == 'X' else self.colors['o_color']
                self.player_label.config(text=f"Bạn cầm quân: {player_symbol}", fg=color)
            
            # Xóa overlay kết quả cũ nếu có (trường hợp chơi lại)
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None
                
            self.game_status.config(text="Trận đấu bắt đầu!", fg=self.colors['primary'])
            self.draw_board()
            self.update_turn_indicator()
            self.start_timer() # Start Timer
            
            self.add_chat_message("Hệ thống", f"Phòng: {', '.join(players)}")
            self.controller.show_view('game')
            
        elif msg_type == 'BOARD_STATE':
            moves = message.get('moves', [])
            self.draw_board() # Reset board first
            for move in moves:
                x, y, val = move['x'], move['y'], move['val']
                self.draw_piece(x, y, val)
                
        elif msg_type == 'VIEW_MATCH_INFO':
            # Xử lý khi xem
            room_id = message.get('room_id')
            players = message.get('players', [])
            
            # QUAN TRỌNG: Reset state thành spectator (player_symbol = None)
            self.controller.set_game_state(room_id, None, True)
            
            # Setup UI cho Viewer
            self.game_status.config(text=f"Đang xem: {', '.join(players)}", fg=self.colors['text_dark'])
            self.player_label.config(text="Khán giả", fg='gray')
            self.turn_indicator.config(text="Đang theo dõi trận đấu", fg='gray')
            
            # Ẩn nút chức năng
            pass

        elif msg_type == 'SYNC_TIMER':
            self.remaining_time = message.get('remaining_time', 0)
            self.update_timer_display()
            # Nếu đang playing thì chạy tiếp
            if self.controller.game_active: # Spectator sets active=False?
                # Spectator might treat game as active=True to see updates?
                # For safety, just run timer locally
                if self.timer_id: self.frame.after_cancel(self.timer_id)
                self.run_timer()

        elif msg_type == 'OPPONENT_MOVE':
            x, y = message.get('x'), message.get('y')
            # Ưu tiên lấy symbol server gửi, nếu không có thì fallback logic cũ (cho player)
            server_symbol = message.get('symbol')
            if server_symbol:
                opp_symbol = server_symbol
            else:
                opp_symbol = 'O' if self.controller.player_symbol == 'X' else 'X'
            
            self.draw_piece(x, y, opp_symbol)
            self.controller.switch_turn()
            self.update_turn_indicator()
            self.start_timer() # Reset Timer
            
        elif msg_type == 'GAME_OVER':
            self.controller.game_active = False # Dừng game
            if self.timer_id: self.frame.after_cancel(self.timer_id) # Stop Timer
            winner = message.get('winner')
            self.turn_indicator.config(text="Kết thúc", fg='red')
            
            # HIỆN BẢNG KẾT QUẢ XỊN
            is_spectator = self.controller.player_symbol is None
            
            if is_spectator:
                self.show_result_overlay('SPECTATOR', winner)
            elif winner == self.controller.username:
                self.show_result_overlay('WIN')
            elif winner == 'Draw':
                self.show_result_overlay('DRAW')
            else:
                self.show_result_overlay('LOSE')
            
        elif msg_type == 'OPPONENT_LEFT':
            # Chỉ báo thắng nều game ĐANG DIỄN RA
            if self.controller.game_active:
                self.controller.game_active = False
                
                # Check xem mình là người chơi hay spectator
                if self.controller.player_symbol: # Là người chơi
                    messagebox.showinfo("Thông báo", "Đối thủ đã thoát trận. Bạn thắng!")
                    self.leave_game()
                else: # Là khán giả
                    messagebox.showinfo("Thông báo", "Một người chơi đã thoát trận. Kết thúc!")
                    self.leave_game()
            else:
                # Nếu game đã xong rồi mà đối thủ thoát -> Chỉ thông báo nhẹ hoặc bỏ qua
                # (Vì lúc này bạn đang xem bảng kết quả, không cần popup làm phiền)
                self.add_chat_message("Hệ thống", "Người chơi đã rời phòng.")
            
        elif msg_type == 'CHAT':
            self.add_chat_message(message.get('sender'), message.get('message'))
            
    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
    def hide(self):
        self.frame.pack_forget()