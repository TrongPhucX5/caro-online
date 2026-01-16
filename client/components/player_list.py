# client/components/player_list.py
import tkinter as tk


class PlayerList:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = tk.Frame(parent, bg='white', relief=tk.GROOVE, bd=1)
        
        self.player_listbox = None
        self.create_widgets()
        
    def create_widgets(self):
        """Create player list widgets"""
        tk.Label(self.frame, text="Danh sách người chơi online", 
                 font=("Segoe UI", 11, "bold"), bg='white').pack(pady=10)
        
        player_list_frame = tk.Frame(self.frame, bg='white')
        player_list_frame.pack(fill=tk.BOTH, expand=True)
        
        player_scrollbar = tk.Scrollbar(player_list_frame)
        player_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.player_listbox = tk.Listbox(
            player_list_frame,
            font=("Segoe UI", 10),
            yscrollcommand=player_scrollbar.set,
            height=20
        )
        self.player_listbox.pack(fill=tk.BOTH, expand=True)
        player_scrollbar.config(command=self.player_listbox.yview)
        
    def update(self, players):
        """Update player list with new data"""
        self.player_listbox.delete(0, tk.END)
        for player in players:
            display_name = player.get('display_name', player.get('username', 'Unknown'))
            self.player_listbox.insert(tk.END, display_name)
            
    def pack(self, **kwargs):
        """Pack the player list frame"""
        self.frame.pack(**kwargs)
        
    def pack_forget(self):
        """Hide the player list"""
        self.frame.pack_forget()