import tkinter as tk
from tkinter import messagebox

class LoginView:
    def __init__(self, parent, controller):
        self.controller = controller
        self.parent = parent
        
        # --- CẤU HÌNH MÀU SẮC ---
        self.colors = {
            'bg': '#ffffff',
            'primary': '#2563eb',
            'text_header': '#1e293b',
            'text_label': '#64748b',
            'border': '#cbd5e1',
            'error': '#ef4444'
        }
        
        self.frame = tk.Frame(parent, bg=self.colors['bg'])
        self.current_mode = 'login' 
        
        self.create_widgets()
        
    def create_widgets(self):
        # Container căn giữa
        self.container = tk.Frame(self.frame, bg=self.colors['bg'])
        self.container.place(relx=0.5, rely=0.5, anchor='center')

        # 1. Logo
        tk.Label(self.container, text="CARO ONLINE",
                 font=("Segoe UI", 28, "bold"),
                 bg=self.colors['bg'], fg=self.colors['primary']).pack(pady=(0, 30))

        # 2. Tiêu đề
        self.title_label = tk.Label(self.container, text="Đăng nhập",
                                    font=("Segoe UI", 18, "bold"),
                                    bg=self.colors['bg'], fg=self.colors['text_header'])
        self.title_label.pack(anchor='w', pady=(0, 15))

        # --- A. USERNAME (Luôn hiện) ---
        self.create_label("Tên đăng nhập")
        self.user_entry_frame, self.user_entry = self.create_input_field(self.container)
        self.user_entry.insert(0, "player1")

        # --- B. VÙNG ĐỆM (Chứa Tên hiển thị) ---
        # Tạo khung nhưng KHÔNG pack (không hiển thị) ngay từ đầu
        self.dynamic_area = tk.Frame(self.container, bg=self.colors['bg'])
        
        # Nhét sẵn các widget vào vùng đệm này (luôn pack sẵn bên trong khung con)
        tk.Label(self.dynamic_area, text="Tên hiển thị trong game", 
                 font=("Segoe UI", 10, "bold"), bg=self.colors['bg'], fg=self.colors['text_label']).pack(anchor='w', pady=(0, 6))
        
        self.display_entry_frame, self.display_entry = self.create_input_field(self.dynamic_area)
        # (Lưu ý: create_input_field tự động pack frame con, nên ta không cần pack lại)

        # --- C. PASSWORD (Luôn hiện) ---
        # Lưu lại label của mật khẩu để làm mốc
        self.lbl_password = self.create_label("Mật khẩu")
        
        self.pass_frame = tk.Frame(self.container, bg=self.colors['bg'], 
                                   highlightbackground=self.colors['border'], highlightthickness=1)
        self.pass_frame.pack(fill=tk.X, ipady=4, pady=(0, 20))
        
        self.pass_entry = tk.Entry(self.pass_frame, width=25, font=("Segoe UI", 11), show="*",
                                   relief=tk.FLAT, bg=self.colors['bg'])
        self.pass_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5))
        self.pass_entry.insert(0, "123")
        
        self.eye_btn = tk.Button(self.pass_frame, text="👁", width=3,
                                 command=self.toggle_password,
                                 relief=tk.FLAT, bg=self.colors['bg'], cursor="hand2", bd=0, 
                                 activebackground=self.colors['bg'])
        self.eye_btn.pack(side=tk.RIGHT, padx=5)

        # --- D. NÚT BẤM ---
        self.status_label = tk.Label(self.container, text="", font=("Segoe UI", 9),
                                     bg=self.colors['bg'], fg=self.colors['error'])
        self.status_label.pack(pady=(0, 10))

        self.action_btn = tk.Button(self.container, text="ĐĂNG NHẬP",
                                    command=self.handle_action,
                                    bg=self.colors['primary'], fg='white',
                                    font=("Segoe UI", 11, "bold"),
                                    relief=tk.FLAT, cursor="hand2", bd=0)
        self.action_btn.pack(fill=tk.X, ipady=10)

        # --- SWITCH MODE ---
        self.switch_frame = tk.Frame(self.container, bg=self.colors['bg'])
        self.switch_frame.pack(pady=(20, 0))

        self.switch_lbl = tk.Label(self.switch_frame, text="Chưa có tài khoản? ",
                                   bg=self.colors['bg'], fg=self.colors['text_label'], font=("Segoe UI", 10))
        self.switch_lbl.pack(side=tk.LEFT)

        self.switch_btn = tk.Label(self.switch_frame, text="Đăng ký ngay",
                                   bg=self.colors['bg'], fg=self.colors['primary'],
                                   font=("Segoe UI", 10, "bold"), cursor="hand2")
        self.switch_btn.pack(side=tk.LEFT)
        self.switch_btn.bind("<Button-1>", self.toggle_mode)

        # Bind Enter
        self.user_entry.bind('<Return>', lambda e: self.handle_action())
        self.pass_entry.bind('<Return>', lambda e: self.handle_action())
        self.display_entry.bind('<Return>', lambda e: self.handle_action())

    # --- HELPER ---

    def create_label(self, text):
        lbl = tk.Label(self.container, text=text, font=("Segoe UI", 10, "bold"),
                 bg=self.colors['bg'], fg=self.colors['text_label'])
        lbl.pack(anchor='w', pady=(0, 6))
        return lbl

    def create_input_field(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg'], highlightbackground=self.colors['border'], highlightthickness=1)
        frame.pack(fill=tk.X, ipady=4, pady=(0, 15))
        
        entry = tk.Entry(frame, font=("Segoe UI", 11), relief=tk.FLAT, bg=self.colors['bg'])
        entry.pack(fill=tk.BOTH, expand=True, padx=10)
        return frame, entry

    def toggle_password(self):
        if self.pass_entry.cget('show') == '':
            self.pass_entry.config(show='*')
            self.eye_btn.config(text='👁')
        else:
            self.pass_entry.config(show='')
            self.eye_btn.config(text='🙈')

    def toggle_mode(self, event=None):
        self.set_status("") 
        
        if self.current_mode == 'login':
            # --- CHUYỂN SANG ĐĂNG KÝ ---
            self.current_mode = 'register'
            self.title_label.config(text="Tạo tài khoản mới")
            self.action_btn.config(text="ĐĂNG KÝ")
            self.switch_lbl.config(text="Đã có tài khoản? ")
            self.switch_btn.config(text="Đăng nhập ngay")
            
            # QUAN TRỌNG: Hiện toàn bộ khung Dynamic Area
            # Dùng 'after' để đảm bảo nó chèn đúng vào sau ô Username
            self.dynamic_area.pack(fill=tk.X, after=self.user_entry_frame)
            self.display_entry.delete(0, tk.END)
            
        else:
            # --- CHUYỂN VỀ ĐĂNG NHẬP ---
            self.current_mode = 'login'
            self.title_label.config(text="Đăng nhập")
            self.action_btn.config(text="ĐĂNG NHẬP")
            self.switch_lbl.config(text="Chưa có tài khoản? ")
            self.switch_btn.config(text="Đăng ký ngay")
            
            # QUAN TRỌNG: Ẩn toàn bộ khung Dynamic Area
            self.dynamic_area.pack_forget()

    def handle_action(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        display_name = self.display_entry.get().strip()

        if not username or not password:
            self.set_status("Vui lòng nhập đầy đủ thông tin!", "red")
            return

        self.set_login_button_state(False)

        if self.current_mode == 'login':
            self.set_status("Đang kết nối...", self.colors['primary'])
            self.controller.login(username, password)
        else:
            if not display_name:
                self.set_status("Vui lòng nhập Tên hiển thị!", "red")
                self.set_login_button_state(True)
                return
            
            self.set_status("Đang đăng ký...", self.colors['primary'])
            if hasattr(self.controller, 'register'):
                self.controller.register(username, password, display_name)
            else:
                self.set_login_button_state(True)
                messagebox.showerror("Lỗi", "Chưa có chức năng đăng ký")

    def set_login_button_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        bg_color = self.colors['primary'] if enabled else '#94a3b8'
        self.action_btn.config(state=state, bg=bg_color)

    def set_status(self, text, color='red'):
        self.status_label.config(text=text, fg=color)
        if color == 'red' or 'lỗi' in text.lower():
            self.set_login_button_state(True)

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        self.frame.pack_forget()