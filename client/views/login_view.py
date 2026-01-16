# client/views/login_view.py
import tkinter as tk


class LoginView:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = tk.Frame(parent, bg='#f5f5f5')
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create login interface"""
        # Title
        tk.Label(self.frame, text="CARO GAME",
                 font=("Segoe UI", 32, "bold"),
                 bg='#f5f5f5', fg='#1e88e5').pack(pady=60)

        tk.Label(self.frame, text="99.hoangtran@gmail.com",
                 font=("Segoe UI", 12),
                 bg='#f5f5f5', fg='#666').pack(pady=(0, 40))

        # Input fields
        box = tk.Frame(self.frame, bg='#f5f5f5')
        box.pack()

        # Username
        tk.Label(box, text="Username", font=("Segoe UI", 11), 
                 bg='#f5f5f5').grid(row=0, column=0, pady=8, sticky="e", padx=(0, 10))
        self.username_entry = tk.Entry(box, width=25, font=("Segoe UI", 11))
        self.username_entry.grid(row=0, column=1)
        self.username_entry.insert(0, "player1")
        self.username_entry.bind('<Return>', lambda e: self.login())

        # Password
        tk.Label(box, text="Password", font=("Segoe UI", 11), 
                 bg='#f5f5f5').grid(row=1, column=0, pady=8, sticky="e", padx=(0, 10))
        self.password_entry = tk.Entry(box, width=25, font=("Segoe UI", 11), show="*")
        self.password_entry.grid(row=1, column=1)
        self.password_entry.insert(0, "123")
        self.password_entry.bind('<Return>', lambda e: self.login())

        # Login button
        self.login_button = tk.Button(self.frame, text="ĐĂNG NHẬP",
                  command=self.login, width=25,
                  bg="#1e88e5", fg="white",
                  font=("Segoe UI", 11, "bold"),
                  height=2)
        self.login_button.pack(pady=20)

        # Status label
        self.status_label = tk.Label(self.frame, bg='#f5f5f5', font=("Segoe UI", 10))
        self.status_label.pack()

    def login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.set_status("Username and password cannot be empty", "red")
            return
        
        self.set_status("Connecting...", "blue")
        self.set_login_button_state(False) # Disable button
        self.controller.login(username, password)

    def set_login_button_state(self, enabled):
        """Enable or disable the login button."""
        state = tk.NORMAL if enabled else tk.DISABLED
        if self.login_button:
            self.login_button.config(state=state)

    def set_status(self, text, color='black'):
        """Update status label"""
        self.status_label.config(text=text, fg=color)

    def get_username(self):
        """Get entered username"""
        return self.username_entry.get().strip()

    def show(self):
        """Show this view"""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """Hide this view"""
        self.frame.pack_forget()
        
    def handle_message(self, message):
        """Handle server messages"""
        # Login view doesn't handle many messages directly
        pass