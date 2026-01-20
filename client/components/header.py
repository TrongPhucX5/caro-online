import tkinter as tk

class Header:
    def __init__(self, parent, controller):
        self.controller = controller
        # Header nền trắng, có viền dưới nhẹ
        self.frame = tk.Frame(parent, bg='white', height=60)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo Header tối giản"""
        # Container nội dung
        inner_frame = tk.Frame(self.frame, bg='white')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)
        
        # Logo / Tên Game (Bên trái)
        tk.Label(
            inner_frame, text="CARO ONLINE",
            bg='white', fg='#2563eb', # Màu xanh chủ đạo
            font=("Segoe UI", 16, "bold")
        ).pack(side=tk.LEFT)
        
        # Slogan hoặc Version (Bên phải)
        tk.Label(
            inner_frame, text="v1.0.0 - Stable",
            bg='white', fg='#9ca3af', # Màu xám nhạt
            font=("Segoe UI", 9)
        ).pack(side=tk.RIGHT, anchor='center')
        
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        
    def pack_forget(self):
        self.frame.pack_forget()