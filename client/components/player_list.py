import tkinter as tk
from tkinter import ttk

class PlayerList(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self.create_widgets()
        
    def create_widgets(self):
        # Dùng Treeview thay Listbox để đẹp hơn
        self.tree = ttk.Treeview(self, columns=('name',), show='tree', selectmode='none')
        
        # Cấu hình cột (ẩn header đi cho gọn)
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('name', anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def update(self, players):
        """Cập nhật danh sách người chơi"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for player in players:
            # Lấy tên hiển thị
            display_name = player.get('display_name', player.get('username', 'Unknown'))
            # Thêm icon xanh (dùng emoji) biểu thị online
            text = f" 🟢  {display_name}"
            self.tree.insert('', tk.END, values=(text,))
            
    def pack(self, **kwargs):
        super().pack(**kwargs)