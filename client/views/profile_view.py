# client/views/profile_view.py
import tkinter as tk
from tkinter import messagebox
import os
from avatar_config import AVATAR_FILENAMES, get_avatar_path


class ProfileView:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = tk.Frame(parent, bg='#f0f0f0')
        
        self.profile_username = None
        self.profile_display = None
        self.old_pass_entry = None
        self.new_pass_entry = None
        
        # Avatar State
        self.current_avatar_idx = 0
        self.avatar_label = None
        self.avatar_image = None # Keep reference
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create profile interface"""
        # Title
        tk.Label(self.frame, text="HỒ SƠ NGƯỜI CHƠI",
                 font=("Segoe UI", 24, "bold"),
                 bg='#f0f0f0', fg='#1e88e5').pack(pady=20)
        
        main_content = tk.Frame(self.frame, bg='#f0f0f0')
        main_content.pack(pady=10)
        
        # --- LEFT: AVATAR SECTION ---
        avatar_frame = tk.Frame(main_content, bg='#f0f0f0', bd=2, relief=tk.GROOVE)
        avatar_frame.pack(side=tk.LEFT, padx=30, pady=10)
        
        tk.Label(avatar_frame, text="Avatar", font=("Segoe UI", 12, "bold"), bg='#f0f0f0').pack(pady=5)
        
        # Image Display
        self.avatar_label = tk.Label(avatar_frame, text="No Image", bg="#cccccc", width=15, height=8)
        self.avatar_label.pack(padx=10, pady=10)
        
        # Controls
        ctrl_frame = tk.Frame(avatar_frame, bg='#f0f0f0')
        ctrl_frame.pack(pady=5)
        
        tk.Button(ctrl_frame, text="<", command=self.prev_avatar, width=3).pack(side=tk.LEFT, padx=5)
        self.idx_label = tk.Label(ctrl_frame, text="0", width=5, bg='#f0f0f0')
        self.idx_label.pack(side=tk.LEFT)
        tk.Button(ctrl_frame, text=">", command=self.next_avatar, width=3).pack(side=tk.LEFT, padx=5)
        
        # --- RIGHT: FORM SECTION ---
        form_wrapper = tk.Frame(main_content, bg='#f0f0f0')
        form_wrapper.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Profile form
        form_frame = tk.Frame(form_wrapper, bg='#f0f0f0')
        form_frame.pack()
        
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
        
    def load_profile(self, username, display_name, avatar_id=0):
        """Load profile data"""
        self.profile_username.config(state="normal")
        self.profile_username.delete(0, tk.END)
        if username:
            self.profile_username.insert(0, str(username))
        self.profile_username.config(state="readonly")
        
        self.profile_display.delete(0, tk.END)
        val = display_name or username
        if val:
            self.profile_display.insert(0, str(val))
        
        self.old_pass_entry.delete(0, tk.END)
        self.new_pass_entry.delete(0, tk.END)
        
        # Load Avatar
        try:
            self.current_avatar_idx = int(avatar_id)
        except:
            self.current_avatar_idx = 0
        self.update_avatar_display()
        
    def prev_avatar(self):
        self.current_avatar_idx = (self.current_avatar_idx - 1) % len(AVATAR_FILENAMES)
        self.update_avatar_display()
        
    def next_avatar(self):
        self.current_avatar_idx = (self.current_avatar_idx + 1) % len(AVATAR_FILENAMES)
        self.update_avatar_display()
        
    def update_avatar_display(self):
        self.idx_label.config(text=str(self.current_avatar_idx))
        
        # Construct path: client/assets/avatar/...
        # Note: self.controller run from root d:\myproject\caro-online
        # App.py is in client/ so assets should be in client/assets
        # But relative path depends on CWD. If CWD is root, then path is client/assets/avatar...
        
        # Code user provided: os.path.join("assets", "avatar", filename)
        # Assuming we need to prepend 'client' if running from root.
        
        # Let's try to find the file
        rel_path = get_avatar_path(self.current_avatar_idx)
        
        # Check standard locations
        possible_paths = [
            os.path.join("client", rel_path), # From root
            rel_path, # From client dir
            os.path.join(os.path.dirname(__file__), "..", "..", "client", rel_path) # Absolute-ish
        ]
        
        final_path = None
        for p in possible_paths:
            if os.path.exists(p):
                final_path = p
                break
        
        if final_path:
            try:
                img = tk.PhotoImage(file=final_path)
                self.avatar_label.config(image=img, text="", width=96, height=96)
                self.avatar_image = img # Keep ref
            except Exception as e:
                self.avatar_label.config(image="", text="Err Load", width=15, height=8)
                print(f"Error loading img {final_path}: {e}")
        else:
             self.avatar_label.config(image="", text=f"No Img\n#{self.current_avatar_idx}", width=15, height=8)

    def save_profile(self):
        """Save profile changes"""
        display = self.profile_display.get().strip()
        old = self.old_pass_entry.get().strip()
        new = self.new_pass_entry.get().strip()
        
        if not display:
            messagebox.showwarning("Warning", "Display name không được trống")
            return
            
        # Call controller update with avatar_id
        self.controller.update_profile(display, old, new, self.current_avatar_idx)
        
    def handle_message(self, message):
        """Handle server messages"""
        msg_type = message.get('type')
        
        if msg_type == 'PROFILE_UPDATED':
            messagebox.showinfo("Success", "Cập nhật hồ sơ thành công!")
            # Reload profile with new data
            self.load_profile(self.controller.username, 
                            message.get('display_name', self.controller.display_name),
                            message.get('avatar_id', self.current_avatar_idx))
                            
    def show(self):
        """Show this view"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        # Reload current data to ensure sync if needed
        # But data usually comes from lobby click
        
    def hide(self):
        """Hide this view"""
        self.frame.pack_forget()