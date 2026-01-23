import tkinter as tk
from tkinter import messagebox
import os
from avatar_config import get_avatar_path
from components.header import Header
from components.room_list import RoomList
from components.player_list import PlayerList

class LobbyView:
    def __init__(self, parent, controller):
        self.controller = controller
        self.parent = parent
        
        # Theme màu sắc
        self.colors = {
            'bg_main': '#f3f4f6',       
            'sidebar': '#ffffff',       
            'primary': '#2563eb',       
            'success': '#10b981',      
            'warning': '#f59e0b',       
            'text_dark': '#1f2937',     
            'text_gray': '#6b7280',     
            'border': '#e5e7eb'         
        }
        
        self.frame = tk.Frame(parent, bg=self.colors['bg_main'])
        
        # Biến UI
        self.lbl_display_name = None
        self.lbl_username = None
        self.lbl_avatar = None
        self.avatar_image = None
        
        self.create_widgets()

    def create_widgets(self):
        # 1. Header
        self.header = Header(self.frame, self.controller)
        self.header.pack(fill=tk.X, side=tk.TOP)
        
        # Đường kẻ header
        tk.Frame(self.frame, bg=self.colors['border'], height=1).pack(fill=tk.X)

        # 2. Main Body
        main_body = tk.Frame(self.frame, bg=self.colors['bg_main'])
        main_body.pack(fill=tk.BOTH, expand=True)

        # === CỘT TRÁI (SIDEBAR) ===
        sidebar = tk.Frame(main_body, bg=self.colors['sidebar'], width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        tk.Frame(main_body, bg=self.colors['border'], width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Profile
        profile_frame = tk.Frame(sidebar, bg=self.colors['sidebar'], pady=30, padx=20)
        profile_frame.pack(fill=tk.X)
        
        # Avatar Image
        self.lbl_avatar = tk.Label(profile_frame, text="👤", font=("Segoe UI", 45), 
                 bg=self.colors['sidebar'], fg=self.colors['text_gray'])
        self.lbl_avatar.pack()
                 
        self.lbl_display_name = tk.Label(profile_frame, text="Loading...", 
                                         font=("Segoe UI", 14, "bold"), wraplength=220,
                                         bg=self.colors['sidebar'], fg=self.colors['text_dark'])
        self.lbl_display_name.pack(pady=(10, 2))
        
        self.lbl_username = tk.Label(profile_frame, text="@username", 
                                     font=("Segoe UI", 10), 
                                     bg=self.colors['sidebar'], fg=self.colors['text_gray'])
        self.lbl_username.pack()
        
        # Nút Edit Profile
        tk.Button(profile_frame, text="✏️ Sửa hồ sơ", 
                 command=lambda: self.controller.show_view('profile'),
                 font=("Segoe UI", 8), bg="#f3f4f6", fg="black", bd=0, cursor="hand2").pack(pady=5)

        tk.Frame(sidebar, bg=self.colors['border'], height=1).pack(fill=tk.X, padx=20, pady=10)

        # Menu
        menu_frame = tk.Frame(sidebar, bg=self.colors['sidebar'], padx=15)
        menu_frame.pack(fill=tk.BOTH, expand=True)

        self.create_sidebar_btn(menu_frame, "⚔️  Tìm trận nhanh", self.colors['primary'], self.quick_match)
        self.create_sidebar_btn(menu_frame, "➕  Tạo phòng mới", self.colors['success'], self.create_room)
        self.create_sidebar_btn(menu_frame, "👁️  Vào xem trận", '#6366f1', self.view_selected_match)
        self.create_sidebar_btn(menu_frame, "🚪  Vào phòng", self.colors['text_dark'], self.join_selected_room)

        # Nút Đăng xuất (Đáy Sidebar)
        bottom_sidebar = tk.Frame(sidebar, bg=self.colors['sidebar'], padx=15, pady=20)
        bottom_sidebar.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Button(bottom_sidebar, text="⬅  Đăng xuất", 
                 command=self.logout_confirm,
                 bg='#fee2e2', fg='#ef4444', 
                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, bd=0, cursor="hand2", height=2).pack(fill=tk.X)
        
        # Nút Refresh (Trên nút đăng xuất)
        self.create_sidebar_btn(bottom_sidebar, "🔄  Làm mới", self.colors['warning'], self.refresh_all_data)


        # === CỘT PHẢI (NỘI DUNG) ===
        self.content_area = tk.Frame(main_body, bg=self.colors['bg_main'], padx=25, pady=25)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(self.content_area, text="Sảnh chờ game", 
                 font=("Segoe UI", 16, "bold"), 
                 bg=self.colors['bg_main'], fg=self.colors['text_dark']).pack(anchor='w', pady=(0, 15))

        self.lists_container = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        self.lists_container.pack(fill=tk.BOTH, expand=True)

        # --- FIX LAYOUT: PACK CỘT PHẢI (PLAYER) TRƯỚC ---
        player_wrapper = tk.Frame(self.lists_container, bg='white', width=220)
        player_wrapper.config(highlightbackground=self.colors['border'], highlightthickness=1)
        player_wrapper.pack(side=tk.RIGHT, fill=tk.Y)
        player_wrapper.pack_propagate(False) # Cố định size
        
        tk.Label(player_wrapper, text="  Người chơi online", font=("Segoe UI", 10, "bold"), 
                 bg="#f9fafb", fg=self.colors['text_dark'], anchor='w', height=2).pack(fill=tk.X)
        tk.Frame(player_wrapper, bg=self.colors['border'], height=1).pack(fill=tk.X)
        
        self.player_list = PlayerList(player_wrapper, self.controller)
        self.player_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- SAU ĐÓ MỚI PACK CỘT TRÁI (ROOM) ---
        room_wrapper = tk.Frame(self.lists_container, bg='white')
        room_wrapper.config(highlightbackground=self.colors['border'], highlightthickness=1)
        room_wrapper.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(room_wrapper, text="  Danh sách phòng", font=("Segoe UI", 10, "bold"), 
                 bg="#f9fafb", fg=self.colors['text_dark'], anchor='w', height=2).pack(fill=tk.X)
        tk.Frame(room_wrapper, bg=self.colors['border'], height=1).pack(fill=tk.X)
        
        self.room_list = RoomList(room_wrapper, self.controller)
        self.room_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Helper & Actions
    def create_sidebar_btn(self, parent, text, color, command):
        tk.Button(parent, text=text, command=command, bg=color, fg='white', 
                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, bd=0, cursor="hand2", height=2).pack(fill=tk.X, pady=5)

    def update_user_info(self):
        d_name = getattr(self.controller, 'display_name', None) or getattr(self.controller, 'username', 'Unknown')
        user = getattr(self.controller, 'username', 'guest')
        avatar_id = getattr(self.controller, 'avatar_id', 0)
        
        if self.lbl_display_name: self.lbl_display_name.config(text=d_name)
        if self.lbl_username: self.lbl_username.config(text=f"@{user}")
        
        # Load avatar
        if self.lbl_avatar:
            rel_path = get_avatar_path(avatar_id)
            possible_paths = [
                os.path.join("client", rel_path), 
                rel_path
            ]
            final_path = None
            for p in possible_paths:
                if os.path.exists(p):
                    final_path = p
                    break
                    
            if final_path:
                try:
                    img = tk.PhotoImage(file=final_path)
                    # Resize? Tkinter PhotoImage doesn't resize well. 
                    # Assuming avatars are pre-sized (96px based on filename).
                    # If needed subsample: img = img.subsample(2)
                    self.lbl_avatar.config(image=img, text="", width=96, height=96)
                    self.avatar_image = img
                except:
                     self.lbl_avatar.config(image="", text="??")
            else:
                 self.lbl_avatar.config(image="", text="👤")

    def handle_message(self, message):
        type = message.get('type')
        if type == 'ROOM_LIST': self.room_list.update(message.get('rooms', []))
        elif type == 'ONLINE_PLAYERS': self.player_list.update(message.get('players', []))
        elif type == 'VIEW_MATCH_INFO':
            info = f"Phòng: {message.get('room_id')}\nTrạng thái: {message.get('status')}\nNgười chơi: {', '.join(message.get('players', []))}"
            messagebox.showinfo("Chi tiết", info)

    # Button Commands
    def quick_match(self):
        # Ẩn danh sách phòng/người chơi
        self.lists_container.pack_forget()
        
        # Hiển thị UI tìm trận (nhúng trực tiếp)
        self.search_frame = tk.Frame(self.content_area, bg='white', 
                                     highlightbackground=self.colors['border'], highlightthickness=1)
        self.search_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center content
        center_frame = tk.Frame(self.search_frame, bg='white')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(center_frame, text="⌛", font=("Segoe UI", 40), bg='white', fg=self.colors['warning']).pack(pady=10)
        tk.Label(center_frame, text="Đang tìm trận...", font=("Segoe UI", 16, "bold"), bg='white').pack(pady=(0, 5))
        
        self.lbl_search_status = tk.Label(center_frame, text="Đang tìm đối thủ phù hợp...", 
                                        font=("Segoe UI", 10), bg='white', fg=self.colors['text_gray'])
        self.lbl_search_status.pack(pady=5)
        
        # Animation Bar (giả lập)
        canvas = tk.Canvas(center_frame, width=300, height=4, bg="#f3f4f6", bd=0, highlightthickness=0)
        canvas.pack(pady=20)
        bar = canvas.create_rectangle(0, 0, 0, 4, fill=self.colors['primary'], width=0)
        
        def animate_bar(w=0):
            try:
                # Kiểm tra frame và canvas còn tồn tại không trước khi vẽ
                if hasattr(self, 'search_frame') and self.search_frame.winfo_exists() and canvas.winfo_exists():
                    w += 5
                    if w > 300: w = 0
                    canvas.coords(bar, 0, 0, w, 4)
                    self.search_frame.after(20, lambda: animate_bar(w))
            except Exception:
                pass # Bỏ qua lỗi nếu widget biến mất đột ngột
        animate_bar()

        # Nút Hủy
        def cancel_search():
            self.controller.pending_action = None # Reset cờ hành động
            self.search_frame.destroy()
            self.lists_container.pack(fill=tk.BOTH, expand=True)
            
        tk.Button(center_frame, text="❌ Hủy tìm kiếm", command=cancel_search, 
                 bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"),
                 relief=tk.FLAT, padx=20, pady=8, cursor="hand2").pack(pady=20)

        # Gửi request sau 1.5s
        self.frame.after(1500, lambda: self._send_quick_match_request())
        
    def _send_quick_match_request(self):
        # Kiểm tra xem frame tìm kiếm còn tồn tại không (user chưa hủy)
        if hasattr(self, 'search_frame') and self.search_frame.winfo_exists():
            if hasattr(self.controller, 'find_match'):
                self.controller.find_match()


    def reset_search_ui(self):
        """Hủy giao diện tìm kiếm và quay về sảnh chính (không tự tìm lại)"""
        # Hủy timer (nếu có)
        try:
            if hasattr(self, 'search_frame'):
                 self.search_frame.destroy()
                 del self.search_frame
        except: pass
        
        # Hiện lại danh sách phòng
        try:
            self.lists_container.pack(fill=tk.BOTH, expand=True)
        except: pass

        # Reset action pending
        if hasattr(self.controller, 'pending_action'):
             self.controller.pending_action = None
        
        # Reset current room locally if set
        if self.controller.current_room:
             self.controller.current_room = None

    def _restore_searching_state(self):
        if not (hasattr(self, 'search_frame') and self.search_frame.winfo_exists()): return
        
        for widget in self.search_frame.winfo_children(): widget.destroy()
        
        center_frame = tk.Frame(self.search_frame, bg='white')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(center_frame, text="⌛", font=("Segoe UI", 40), bg='white', fg=self.colors['warning']).pack(pady=10)
        tk.Label(center_frame, text="Đang tìm trận...", font=("Segoe UI", 16, "bold"), bg='white').pack(pady=(0, 5))
        
        # Gọi lại tìm trận (nếu người dùng là người tìm kiếm B)
        # Nếu là người tạo phòng (A), họ vẫn ở trong phòng, chỉ cần đợi tiếp
        # A doesn't need to call find_match again, server keeps A in waiting room
        if self.controller.current_room is None:
             self.controller.find_match()

    def handle_match_found(self, message):
        """Hiển thị thông báo tìm thấy trận và đếm ngược"""
        # Đảm bảo hiển thị frame tìm kiếm/popup nếu chưa có
        if not hasattr(self, 'search_frame') or not self.search_frame.winfo_exists():
             self.lists_container.pack_forget()
             self.search_frame = tk.Frame(self.content_area, bg='white', 
                                         highlightbackground=self.colors['border'], highlightthickness=1)
             self.search_frame.pack(fill=tk.BOTH, expand=True)

        # Xóa hết nội dung cũ
        for widget in self.search_frame.winfo_children():
            widget.destroy()
            
        opp_name = message.get('opponent_name', 'Unknown')
        room_id = message.get('room_id')
        timeout = message.get('timeout', 15)
        
        # Center content lại
        center_frame = tk.Frame(self.search_frame, bg='white')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(center_frame, text="✅", font=("Segoe UI", 40), bg='white', fg=self.colors['success']).pack(pady=10)
        tk.Label(center_frame, text=f"Đã tìm thấy đối thủ:\n{opp_name}", 
                    font=("Segoe UI", 14, "bold"), bg='white', wraplength=400, justify='center').pack(pady=(0, 5))
        
        tk.Label(center_frame, text="Bạn có muốn vào trận đấu này?", font=("Segoe UI", 12), bg='white').pack()
        
        # Timer Countdown
        lbl_timer = tk.Label(center_frame, text=f"{timeout}s", font=("Segoe UI", 24, "bold"), bg='white', fg=self.colors['primary'])
        lbl_timer.pack(pady=10)
        
        btn_frame = tk.Frame(center_frame, bg='white')
        btn_frame.pack(pady=20)
        
        def on_decline():
            if hasattr(self.controller, 'decline_match'):
                self.controller.decline_match(room_id)
            
            # Xóa popup
            self.search_frame.destroy()
            self.lists_container.pack(fill=tk.BOTH, expand=True)

            # Xử lý tùy theo trạng thái (người tìm hay chủ phòng)
            if self.controller.pending_action == 'quick_match':
                 self.controller.pending_action = None 
                 # Nếu là Quick Matcher đang giữ room -> Rời phòng
                 if self.controller.current_room:
                      self.controller.network.send({'type': 'LEAVE_ROOM', 'room_id': self.controller.current_room})
                      self.controller.current_room = None
            else:
                 # Nếu là Chủ phòng (Manual Create) -> Quay lại Game View đợi tiếp
                 if self.controller.current_room:
                      self.controller.show_view('game') 

        def on_accept():
            # Dùng accept_match thay vì join_room
            if hasattr(self.controller, 'accept_match'):
                self.controller.accept_match(room_id)
            
            # UI chuyển sang trạng thái "Đang đợi đối thủ..."
            for widget in btn_frame.winfo_children(): 
                if isinstance(widget, tk.Button): widget.config(state=tk.DISABLED)
            
            tk.Label(center_frame, text="Đang đợi đối thủ xác nhận...", fg="#6b7280", bg='white', font=("Segoe UI", 10, "italic")).pack(pady=10)

        tk.Button(btn_frame, text="❌ Từ chối", command=on_decline,
                    bg="#f3f4f6", fg=self.colors['text_dark'], font=("Segoe UI", 10, "bold"),
                    relief=tk.FLAT, padx=15, pady=8, width=12, cursor="hand2").pack(side=tk.LEFT, padx=10)
                    
        tk.Button(btn_frame, text="✅ Vào Ngay", command=on_accept,
                    bg=self.colors['success'], fg="white", font=("Segoe UI", 10, "bold"),
                    relief=tk.FLAT, padx=15, pady=8, width=12, cursor="hand2").pack(side=tk.LEFT, padx=10)
                    
        # Logic đếm ngược
        self.match_timer = timeout
        def countdown():
            if not self.search_frame.winfo_exists(): return
            # Nếu đã chấp nhận (nút bị disable) thì không tự hủy nữa? Hay vẫn hủy?
            # Thường thì nên giữ timer để timeout server xử lý. 
            # Nhưng ở đây client đếm ngược để hiển thị thôi.
            
            self.match_timer -= 1
            lbl_timer.config(text=f"{self.match_timer}s")
            if self.match_timer > 0:
                self.search_frame.after(1000, countdown)
            else:
                pass # Hết giờ, để server timeout handle
        
        self.search_frame.after(1000, countdown)
            
    def logout_confirm(self):
        if messagebox.askyesno("Đăng xuất", "Bạn chắc chắn muốn thoát?"): self.controller.logout()
        
    def view_selected_match(self):
        rid = self.room_list.get_selected_room()
        if rid: self.controller.view_match(rid)
        else: messagebox.showwarning("!", "Chọn phòng trước")
        
    def join_selected_room(self):
        # Dùng hàm mới để lấy info đầy đủ
        info = self.room_list.get_selected_room_info()
        if not info:
            messagebox.showwarning("!", "Chọn phòng trước")
            return
            
        rid = info['id']
        has_pass = info['has_password']
        
        password = None
        if has_pass:
            from tkinter import simpledialog
            password = simpledialog.askstring("Mật khẩu", "Phòng này yêu cầu mật khẩu:")
            if password is None: # User bấm Cancel
                return
                
        self.controller.join_room(rid, password)
        
    def create_room(self):
        # Tạo dialog tùy chỉnh
        dialog = tk.Toplevel(self.frame)
        dialog.title("Tạo phòng mới")
        dialog.geometry("300x250")
        dialog.config(bg='white')
        
        # Center dialog
        x = self.parent.winfo_x() + 100
        y = self.parent.winfo_y() + 100
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text="Cấu hình phòng", font=("Segoe UI", 12, "bold"), bg='white').pack(pady=10)
        
        # Password
        tk.Label(dialog, text="Mật khẩu (Để trống nếu công khai):", bg='white').pack(anchor='w', padx=20)
        pass_entry = tk.Entry(dialog, show="*")
        pass_entry.pack(fill=tk.X, padx=20, pady=5)
        
        # Time Limit
        tk.Label(dialog, text="Thời gian suy nghĩ (giây):", bg='white').pack(anchor='w', padx=20)
        time_entry = tk.Entry(dialog)
        time_entry.insert(0, "30")
        time_entry.pack(fill=tk.X, padx=20, pady=5)
        
        def on_create():
            pwd = pass_entry.get().strip()
            try:
                limit = int(time_entry.get())
                if limit < 5: limit = 5
                if limit > 300: limit = 300
            except:
                limit = 30
                
            self.controller.create_room(password=pwd if pwd else None, time_limit=limit)
            dialog.destroy()
            
        tk.Button(dialog, text="Tạo phòng", command=on_create, 
                 bg=self.colors['success'], fg='white', relief=tk.FLAT).pack(pady=20)
    def refresh_all_data(self): self.controller.refresh_all_data()
    
    def show(self):
        # Reset UI về trạng thái mặc định (xóa UI tìm trận nếu có)
        if hasattr(self, 'search_frame') and self.search_frame.winfo_exists():
            self.search_frame.destroy()
            self.lists_container.pack(fill=tk.BOTH, expand=True)
            # Reset action nếu cần thiết
            if hasattr(self.controller, 'pending_action'):
                 self.controller.pending_action = None

        self.frame.pack(fill=tk.BOTH, expand=True)
        self.update_user_info()
    def hide(self): self.frame.pack_forget()