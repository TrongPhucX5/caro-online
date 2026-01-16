# client/views/lobby_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from components.header import Header
from components.room_list import RoomList
from components.player_list import PlayerList


class LobbyView:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = tk.Frame(parent, bg='#f0f0f0')
        
        # Components
        self.header = None
        self.room_list = None
        self.player_list = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create lobby interface"""
        # Header
        self.header = Header(self.frame, self.controller)
        self.header.pack(fill=tk.X, pady=(0, 10))
        
        # Function frame
        func_frame = tk.LabelFrame(self.frame, text="Chức năng", 
                                   font=("Segoe UI", 11, "bold"),
                                   bg='#f0f0f0', fg='#1e88e5',
                                   labelanchor='n')
        func_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Function buttons
        tk.Button(func_frame, text="Tìm trận", 
                  font=("Segoe UI", 10), width=12, height=2,
                  bg='#1e88e5', fg='white').pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(func_frame, text="Vào xem",
                  command=self.view_selected_match, 
                  font=("Segoe UI", 10), width=12, height=2,
                  bg='#1e88e5', fg='white').pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(func_frame, text="Vào phòng", 
                  command=self.join_selected_room,
                  font=("Segoe UI", 10), width=12, height=2,
                  bg='#1e88e5', fg='white').pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(func_frame, text="Tạo phòng", 
                  command=self.create_room,
                  font=("Segoe UI", 10), width=12, height=2,
                  bg='#43a047', fg='white').pack(side=tk.LEFT, padx=5, pady=5)
        
        # Tabs Container
        tabs_container = tk.Frame(self.frame, bg='#f0f0f0')
        tabs_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Tabs Header
        tabs_header = tk.Frame(tabs_container, bg='#f0f0f0')
        tabs_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(tabs_header, text="Danh sách phòng", 
                 font=("Segoe UI", 12, "bold"),
                 bg='#f0f0f0').pack(side=tk.LEFT)
        
        tk.Label(tabs_header, text="Người chơi", 
                 font=("Segoe UI", 12, "bold"),
                 bg='#f0f0f0').pack(side=tk.LEFT, padx=30)
        
        # Main Content Frame
        content_frame = tk.Frame(tabs_container, bg='white', relief=tk.GROOVE, bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Room List (Left)
        room_container = tk.Frame(content_frame, bg='white')
        room_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        
        self.room_list = RoomList(room_container, self.controller)
        self.room_list.pack(fill=tk.BOTH, expand=True)
        
        # Player List (Right)
        player_container = tk.Frame(content_frame, bg='white', relief=tk.GROOVE, bd=1)
        player_container.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 10), pady=10, ipadx=10)
        
        self.player_list = PlayerList(player_container, self.controller)
        self.player_list.pack(fill=tk.BOTH, expand=True)
        
        # Bottom Controls
        bottom_frame = tk.Frame(self.frame, bg='#f0f0f0')
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(bottom_frame, text="Vào phòng", 
                  command=self.join_selected_room,
                  bg='#1e88e5', fg='white',
                  font=("Segoe UI", 10, "bold"),
                  width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(bottom_frame, text="Làm mới", 
                  command=self.refresh_all_data,
                  bg='#ff9800', fg='white',
                  font=("Segoe UI", 10, "bold"),
                  width=15, height=2).pack(side=tk.RIGHT, padx=5)
        
        # Refresh button in function frame
        tk.Button(func_frame, text="🔄 Làm mới", 
                  command=self.refresh_all_data,
                  bg='#ff9800', fg='white',
                  font=("Segoe UI", 10, "bold"),
                  width=12, height=2).pack(side=tk.RIGHT, padx=5, pady=5)
        
    def view_selected_match(self):
        """View selected match"""
        room_id = self.room_list.get_selected_room()
        if room_id:
            self.controller.view_match(room_id)
        else:
            messagebox.showwarning("Warning", "Chọn một phòng trước!")
            
    def join_selected_room(self):
        """Join selected room"""
        room_id = self.room_list.get_selected_room()
        if room_id:
            self.controller.join_room(room_id)
        else:
            messagebox.showwarning("Warning", "Chọn một phòng trước!")
            
    def create_room(self):
        """Create new room"""
        self.controller.create_room()
        
    def refresh_all_data(self):
        """Refresh all data"""
        self.controller.refresh_all_data()
        
    def handle_message(self, message):
        """Handle server messages"""
        msg_type = message.get('type')
        
        if msg_type == 'ROOM_LIST':
            rooms = message.get('rooms', [])
            self.room_list.update(rooms)
            
        elif msg_type == 'ONLINE_PLAYERS':
            players = message.get('players', [])
            self.player_list.update(players)
            
        elif msg_type == 'VIEW_MATCH_INFO':
            room_info = f"Phòng: {message.get('room_id')}\n"
            room_info += f"Trạng thái: {message.get('status')}\n"
            room_info += f"Người chơi: {', '.join(message.get('players', []))}"
            messagebox.showinfo("Thông tin phòng", room_info)
            
    def show(self):
        """Show this view"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
    def hide(self):
        """Hide this view"""
        self.frame.pack_forget()