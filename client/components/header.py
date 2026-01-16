# client/components/header.py
import tkinter as tk


class Header:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = tk.Frame(parent, bg='#1e88e5', height=70)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create header widgets"""
        # Left side: Title and email
        left_header = tk.Frame(self.frame, bg='#1e88e5')
        left_header.pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            left_header, text="Caro Game",
            bg='#1e88e5', fg='white',
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")
        
        tk.Label(
            left_header, text="lphuc2324@gmail.com",
            bg='#1e88e5', fg='#e3f2fd',
            font=("Segoe UI", 10)
        ).pack(anchor="w")
        
        # Right side: Buttons
        right_header = tk.Frame(self.frame, bg='#1e88e5')
        right_header.pack(side=tk.RIGHT, padx=20)
        
        tk.Button(
            right_header, text="Đăng xuất", 
            command=self.controller.logout,
            bg='#e53935', fg='white', 
            font=("Segoe UI", 10, "bold"),
            width=10, height=1
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            right_header, text="Hồ sơ", 
            command=lambda: self.controller.show_view('profile'),
            bg='#43a047', fg='white', 
            font=("Segoe UI", 10, "bold"),
            width=10, height=1
        ).pack(side=tk.RIGHT, padx=5)
        
    def pack(self, **kwargs):
        """Pack the header frame"""
        self.frame.pack(**kwargs)
        
    def pack_forget(self):
        """Hide the header"""
        self.frame.pack_forget()