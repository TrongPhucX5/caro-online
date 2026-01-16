# client/views/profile_view.py
import tkinter as tk
from tkinter import messagebox


class ProfileView:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = tk.Frame(parent, bg='#f0f0f0')
        
        self.profile_username = None
        self.profile_display = None
        self.old_pass_entry = None
        self.new_pass_entry = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create profile interface"""
        # Title
        tk.Label(self.frame, text="HỒ SƠ NGƯỜI CHƠI",
                 font=("Segoe UI", 24, "bold"),
                 bg='#f0f0f0', fg='#1e88e5').pack(pady=30)
        
        # Profile form
        form_frame = tk.Frame(self.frame, bg='#f0f0f0')
        form_frame.pack(pady=20)
        
        # Username (readonly)
        tk.Label(form_frame, text="Username:", 
                 font=("Segoe UI", 11), bg='#f0f0f0').grid(row=0, column=0, pady=10, sticky="e")
        self.profile_username = tk.Entry(form_frame, width=25, font=("Segoe UI", 11))
        self.profile_username.grid(row=0, column=1, padx=10)
        self.profile_username.config(state="readonly")
        
        # Display name
        tk.Label(form_frame, text="Display name:", 
                 font=("Segoe UI", 11), bg='#f0f0f0').grid(row=1, column=0, pady=10, sticky="e")
        self.profile_display = tk.Entry(form_frame, width=25, font=("Segoe UI", 11))
        self.profile_display.grid(row=1, column=1, padx=10)
        
        # Old password
        tk.Label(form_frame, text="Mật khẩu cũ:", 
                 font=("Segoe UI", 11), bg='#f0f0f0').grid(row=2, column=0, pady=10, sticky="e")
        self.old_pass_entry = tk.Entry(form_frame, width=25, font=("Segoe UI", 11), show="*")
        self.old_pass_entry.grid(row=2, column=1, padx=10)
        
        # New password
        tk.Label(form_frame, text="Mật khẩu mới:", 
                 font=("Segoe UI", 11), bg='#f0f0f0').grid(row=3, column=0, pady=10, sticky="e")
        self.new_pass_entry = tk.Entry(form_frame, width=25, font=("Segoe UI", 11), show="*")
        self.new_pass_entry.grid(row=3, column=1, padx=10)
        
        # Buttons
        button_frame = tk.Frame(self.frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Lưu thay đổi",
                  command=self.save_profile,
                  bg="#1e88e5", fg="white",
                  font=("Segoe UI", 11, "bold"),
                  width=15, height=2).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Quay lại",
                  command=lambda: self.controller.show_view('lobby'),
                  bg="#757575", fg="white",
                  font=("Segoe UI", 11, "bold"),
                  width=15, height=2).pack(side=tk.LEFT, padx=10)
        
    def load_profile(self, username, display_name):
        """Load profile data"""
        self.profile_username.config(state="normal")
        self.profile_username.delete(0, tk.END)
        self.profile_username.insert(0, username)
        self.profile_username.config(state="readonly")
        
        self.profile_display.delete(0, tk.END)
        self.profile_display.insert(0, display_name or username)
        
        self.old_pass_entry.delete(0, tk.END)
        self.new_pass_entry.delete(0, tk.END)
        
    def save_profile(self):
        """Save profile changes"""
        display = self.profile_display.get().strip()
        old = self.old_pass_entry.get().strip()
        new = self.new_pass_entry.get().strip()
        
        if not display:
            messagebox.showwarning("Warning", "Display name không được trống")
            return
            
        self.controller.update_profile(display, old, new)
        
    def handle_message(self, message):
        """Handle server messages"""
        msg_type = message.get('type')
        
        if msg_type == 'PROFILE_UPDATED':
            messagebox.showinfo("Success", "Cập nhật hồ sơ thành công!")
            # Reload profile with new data
            self.load_profile(self.controller.username, 
                            message.get('display_name', self.controller.display_name))
                            
    def show(self):
        """Show this view"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
    def hide(self):
        """Hide this view"""
        self.frame.pack_forget()