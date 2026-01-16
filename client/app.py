# client/app.py
import tkinter as tk
from tkinter import messagebox
import queue

from network import NetworkClient
from views.login_view import LoginView
from views.lobby_view import LobbyView
from views.game_view import GameView
from views.profile_view import ProfileView


class CaroClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Caro Online - 99.hoangtran@gmail.com")
        self.window.geometry("900x650")

        # Message queue for thread-safe UI updates
        self.message_queue = queue.Queue()

        # Network
        self.network = NetworkClient()
        self.network.set_handler(self.queue_server_message)

        # State
        self.username = None
        self.display_name = None
        self.player_symbol = 'X'
        self.current_turn = 'X'
        self.game_active = False
        self.board_size = 15
        self.cell_size = 30
        self.current_room = None
        
        # For async login
        self.pending_username = None
        self.pending_password = None

        # Initialize views
        self.views = {}
        self.setup_views()
        
        self.show_view('login')
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_views(self):
        """Initialize all views"""
        self.views['login'] = LoginView(self.window, self)
        self.views['lobby'] = LobbyView(self.window, self)
        self.views['game'] = GameView(self.window, self)
        self.views['profile'] = ProfileView(self.window, self)

    def show_view(self, view_name):
        """Switch between views"""
        # If switching back to login, ensure user is logged out
        if view_name == 'login':
            self.logout(False) # Don't send disconnect message if already disconnected

        for view in self.views.values():
            view.hide()
        
        if view_name in self.views:
            self.views[view_name].show()
            
            if view_name == 'lobby':
                self.window.geometry("900x650")
                self.refresh_all_data()
            elif view_name == 'game':
                self.window.geometry("1000x700")

    # ================= NETWORK HANDLER =================

    def queue_server_message(self, message):
        """Queue messages from the network thread to be processed in the main thread."""
        self.message_queue.put(message)

    def process_message_queue(self):
        """Process messages from the queue in the main thread."""
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                self._process_server_message(message)
        except queue.Empty:
            pass
        finally:
            self.window.after(100, self.process_message_queue)

    def _process_server_message(self, message):
        """Process a single message from the server."""
        msg_type = message.get('type')
        print(f"📩 UI Thread Processing: {message}")

        if msg_type == 'CONNECTION_SUCCESS':
            print("Connection successful, sending login info...")
            self.network.send({
                'type': 'LOGIN', 
                'username': self.pending_username, 
                'password': self.pending_password
            })
        elif msg_type == 'CONNECTION_FAILED':
            messagebox.showerror("Connection Failed", f"Could not connect to server.\n{message.get('error', '')}")
            self.views['login'].set_login_button_state(True) # Re-enable button
        elif msg_type == 'DISCONNECTED':
            messagebox.showinfo("Disconnected", "You have been disconnected from the server.")
            self.show_view('login')
        elif msg_type == 'LOGIN_SUCCESS':
            self.on_login_success(message)
        elif msg_type in ['ROOM_LIST', 'ONLINE_PLAYERS', 'VIEW_MATCH_INFO']:
            if 'lobby' in self.views: self.views['lobby'].handle_message(message)
        elif msg_type in ['ROOM_CREATED', 'ROOM_JOINED', 'OPPONENT_MOVE', 
                         'GAME_OVER', 'OPPONENT_LEFT', 'CHAT']:
            if 'game' in self.views: self.views['game'].handle_message(message)
        elif msg_type == 'PROFILE_UPDATED':
            if 'profile' in self.views: self.views['profile'].handle_message(message)
        elif msg_type == 'ERROR':
            messagebox.showerror("Error", message.get('message'))
            # If login fails, re-enable the button
            if 'Login Failed' in message.get('message', ''):
                self.views['login'].set_login_button_state(True)

    def on_login_success(self, message):
        """Handle successful login"""
        self.username = self.pending_username
        self.display_name = message.get('display_name', self.username)
        self.window.title(f"Caro Game - {self.username}")
        
        # Clear pending credentials
        self.pending_username = None
        self.pending_password = None
        
        self.show_view('lobby')
        self.refresh_all_data()
        
        if hasattr(self.views['profile'], 'load_profile'):
            self.views['profile'].load_profile(self.username, self.display_name)

    # ================= NETWORK ACTIONS =================

    def login(self, username, password):
        """Start the login process."""
        if not username or not password:
            messagebox.showwarning("Login", "Username and password cannot be empty.")
            return

        # Disable login button to prevent multiple clicks
        self.views['login'].set_login_button_state(False)
        
        self.pending_username = username
        self.pending_password = password
        self.network.start_connection()

    def logout(self, send_disconnect=True):
        """Logout and return to login screen"""
        if send_disconnect:
            self.network.disconnect()
        self.username = None
        self.display_name = None
        self.current_room = None
        self.game_active = False
        # Do not call show_view here to avoid loops. It's handled by the caller.

    def create_room(self):
        """Create new room"""
        self.network.send({'type': 'CREATE_ROOM'})

    def join_room(self, room_id):
        """Join existing room"""
        self.network.send({'type': 'JOIN_ROOM', 'room_id': room_id})

    def send_move(self, x, y):
        """Send move to server"""
        self.network.send({'type': 'MOVE', 'x': x, 'y': y, 'room_id': self.current_room})

    def send_chat(self, message):
        """Send chat message"""
        self.network.send({'type': 'CHAT', 'message': message, 'room_id': self.current_room})

    def surrender(self):
        """Surrender current game"""
        self.network.send({'type': 'SURRENDER', 'room_id': self.current_room})

    def refresh_all_data(self):
        """Refresh both rooms and online players"""
        self.refresh_rooms()
        self.refresh_online_players()

    def refresh_rooms(self):
        """Request room list"""
        self.network.send({'type': 'GET_ROOMS'})

    def refresh_online_players(self):
        """Request online players list"""
        self.network.send({'type': 'GET_ONLINE_PLAYERS'})

    def view_match(self, room_id):
        """Request to view match"""
        self.network.send({'type': 'VIEW_MATCH', 'room_id': room_id})

    def update_profile(self, display_name, old_password, new_password):
        """Update user profile"""
        self.network.send({
            'type': 'EDIT_PROFILE',
            'display_name': display_name,
            'old_password': old_password,
            'new_password': new_password
        })

    # ================= GAME STATE =================

    def set_game_state(self, room_id, player_symbol, game_active=True):
        """Set current game state"""
        self.current_room = room_id
        self.player_symbol = player_symbol
        self.game_active = game_active
        self.current_turn = 'X'  # Reset turn

    def get_game_state(self):
        """Get current game state"""
        return {
            'room_id': self.current_room,
            'player_symbol': self.player_symbol,
            'game_active': self.game_active,
            'current_turn': self.current_turn,
            'board_size': self.board_size,
            'cell_size': self.cell_size
        }

    def switch_turn(self):
        """Switch turn between players"""
        self.current_turn = 'O' if self.current_turn == 'X' else 'X'

    # ================= UTILITIES =================

    def on_close(self):
        """Handle window close"""
        self.network.disconnect()
        self.window.destroy()

    def run(self):
        """Start the application"""
        self.process_message_queue()
        self.window.mainloop()

if __name__ == "__main__":
    app = CaroClient()
    app.run()