import tkinter as tk
from tkinter import messagebox
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
        
        tk.Label(profile_frame, text="👤", font=("Segoe UI", 45), 
                 bg=self.colors['sidebar'], fg=self.colors['text_gray']).pack()
                 
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
        content_area = tk.Frame(main_body, bg=self.colors['bg_main'], padx=25, pady=25)
        content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(content_area, text="Sảnh chờ game", 
                 font=("Segoe UI", 16, "bold"), 
                 bg=self.colors['bg_main'], fg=self.colors['text_dark']).pack(anchor='w', pady=(0, 15))

        lists_container = tk.Frame(content_area, bg=self.colors['bg_main'])
        lists_container.pack(fill=tk.BOTH, expand=True)

        # --- FIX LAYOUT: PACK CỘT PHẢI (PLAYER) TRƯỚC ---
        player_wrapper = tk.Frame(lists_container, bg='white', width=220)
        player_wrapper.config(highlightbackground=self.colors['border'], highlightthickness=1)
        player_wrapper.pack(side=tk.RIGHT, fill=tk.Y)
        player_wrapper.pack_propagate(False) # Cố định size
        
        tk.Label(player_wrapper, text="  Người chơi online", font=("Segoe UI", 10, "bold"), 
                 bg="#f9fafb", fg=self.colors['text_dark'], anchor='w', height=2).pack(fill=tk.X)
        tk.Frame(player_wrapper, bg=self.colors['border'], height=1).pack(fill=tk.X)
        
        self.player_list = PlayerList(player_wrapper, self.controller)
        self.player_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- SAU ĐÓ MỚI PACK CỘT TRÁI (ROOM) ---
        room_wrapper = tk.Frame(lists_container, bg='white')
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
        if self.lbl_display_name: self.lbl_display_name.config(text=d_name)
        if self.lbl_username: self.lbl_username.config(text=f"@{user}")

    def handle_message(self, message):
        type = message.get('type')
        if type == 'ROOM_LIST': self.room_list.update(message.get('rooms', []))
        elif type == 'ONLINE_PLAYERS': self.player_list.update(message.get('players', []))
        elif type == 'VIEW_MATCH_INFO':
            info = f"Phòng: {message.get('room_id')}\nTrạng thái: {message.get('status')}\nNgười chơi: {', '.join(message.get('players', []))}"
            messagebox.showinfo("Chi tiết", info)

    # Button Commands
    def quick_match(self):
        if hasattr(self.controller, 'find_match'): self.controller.find_match()
        else: messagebox.showinfo("Info", "Chức năng đang phát triển")
    
    def logout_confirm(self):
        if messagebox.askyesno("Đăng xuất", "Bạn chắc chắn muốn thoát?"): self.controller.logout()
        
    def view_selected_match(self):
        rid = self.room_list.get_selected_room()
        if rid: self.controller.view_match(rid)
        else: messagebox.showwarning("!", "Chọn phòng trước")
        
    def join_selected_room(self):
        rid = self.room_list.get_selected_room()
        if rid: self.controller.join_room(rid)
        else: messagebox.showwarning("!", "Chọn phòng trước")
        
    def create_room(self): self.controller.create_room()
    def refresh_all_data(self): self.controller.refresh_all_data()
    
    def show(self): 
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.update_user_info()
    def hide(self): self.frame.pack_forget()