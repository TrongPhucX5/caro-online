import tkinter as tk
from tkinter import ttk

class RoomList(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self.setup_style()
        self.create_widgets()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"), 
                        background="white", foreground="#4b5563", relief="flat")
        
        style.configure("Treeview", 
                        font=("Segoe UI", 10),
                        rowheight=35,
                        background="white", fieldbackground="white", relief="flat")
        
        style.map("Treeview", background=[('selected', '#eff6ff')], foreground=[('selected', '#1e40af')])

    def create_widgets(self):
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        # Chú ý: Cột thứ 4 là 'raw_id' dùng để lưu ID gốc nhưng không hiển thị
        columns = ('display_id', 'name', 'count', 'raw_id')
        
        self.tree = ttk.Treeview(self, columns=columns, show='headings', 
                                 yscrollcommand=scrollbar.set, selectmode='browse')
        
        # Cấu hình hiển thị cột (Cột raw_id để width=0 để ẩn đi)
        self.tree.column('display_id', width=100, anchor='w')
        self.tree.column('name', width=230, anchor='w')
        self.tree.column('count', width=80, anchor='center')
        self.tree.column('raw_id', width=0, stretch=tk.NO) # <--- ẨN CỘT NÀY
        
        self.tree.heading('display_id', text='Phòng', anchor='w')
        self.tree.heading('name', text='Cặp đấu', anchor='w')
        self.tree.heading('count', text='Số lượng', anchor='center')
        self.tree.heading('raw_id', text='') # Không cần tiêu đề cho cột ẩn
        
        scrollbar.config(command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree.bind('<Double-1>', self.on_double_click)

    def update(self, rooms):
        # 1. Xóa sạch dữ liệu cũ trên giao diện
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 2. Thêm dữ liệu mới từ Server
        for room in rooms:
            raw_id = room['id']
            # Logic làm đẹp tên phòng
            try:
                room_num = raw_id.split('_')[1]
                display_id = f"Phòng #{int(room_num):02d}"
            except:
                display_id = raw_id

            status_text = f"{room['count']}/2"
            if room['status'] == 'playing':
                status_text += " (Đang chơi)"
            
            # Chèn vào bảng (Lưu ý thứ tự values khớp với columns khai báo ở trên)
            self.tree.insert('', tk.END, values=(
                display_id,           # Cột 1: Tên đẹp
                room['match_text'],   # Cột 2: Cặp đấu
                status_text,          # Cột 3: Trạng thái
                raw_id                # Cột 4 (Ẩn): ID gốc để xử lý logic
            ))

    def get_selected_room(self):
        selected = self.tree.selection()
        if selected:
            # Lấy giá trị từ cột ẩn 'raw_id' (index 3)
            # Đây là cách chuẩn nhất, không cần split chuỗi gì cả
            return self.tree.item(selected[0])['values'][3]
        return None

    def on_double_click(self, event):
        room_id = self.get_selected_room()
        if room_id and hasattr(self.controller, 'join_room'):
            self.controller.join_room(room_id)