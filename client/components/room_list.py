import tkinter as tk
from tkinter import ttk

class RoomList:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg='white', relief=tk.GROOVE, bd=1)
        
        # Tiêu đề
        tk.Label(self.frame, text="Danh sách phòng", 
                 font=("Segoe UI", 12, "bold"),
                 bg='white').pack(pady=10)
        
        # Bảng phòng
        table_frame = tk.Frame(self.frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Header
        header_frame = tk.Frame(table_frame, bg='#1e88e5', height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Mã", font=("Segoe UI", 11, "bold"), 
                 bg='#1e88e5', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="Cặp đấu", font=("Segoe UI", 11, "bold"), 
                 bg='#1e88e5', fg='white', width=25).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="Số người", font=("Segoe UI", 11, "bold"), 
                 bg='#1e88e5', fg='white', width=10).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        tree_frame = tk.Frame(table_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=("id", "match", "count"),
            show="tree",
            yscrollcommand=scrollbar.set,
            height=10
        )
        
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=0, stretch=False)
        self.tree.heading("id", text="Mã")
        self.tree.heading("match", text="Cặp đấu")
        self.tree.heading("count", text="Số người")
        
        self.tree.column("id", width=150, anchor=tk.CENTER)
        self.tree.column("match", width=250, anchor=tk.W)
        self.tree.column("count", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
    
    def update(self, rooms):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for room in rooms:
            r_id = room['id']
            count = f"{room['count']}/2"
            match_text = room.get('match_text', 'Chờ đối thủ...')
            self.tree.insert("", tk.END, values=(r_id, match_text, count))
    
    def get_selected_room(self):
        selected = self.tree.selection()
        if selected:
            return self.tree.item(selected[0])['values'][0]
        return None
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)