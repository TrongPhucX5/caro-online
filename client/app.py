import tkinter as tk
from tkinter import messagebox
import queue

# Đảm bảo các file này đã tồn tại
from network import NetworkClient
from views.login_view import LoginView
from views.lobby_view import LobbyView
from views.game_view import GameView
from views.profile_view import ProfileView

class CaroClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Caro Online")
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

        # Cờ kiểm soát logout (để tránh hiện popup lỗi khi tự bấm thoát)
        self.is_logging_out = False
        
        # Cờ kiểm soát hành động (tránh vào phòng khi đã hủy)
        self.pending_action = None # 'create', 'join', 'quick_match'

        # Initialize views
        self.views = {}
        
        # Timer variables
        self.time_limit = 30
        self.remaining_time = 30
        self.timer_running = False
        self.timer_id = None

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
            # THAY ĐỔI Ở ĐÂY: Thêm tham số redirect_to_login=False để chặn vòng lặp
            self.logout(send_disconnect=False, redirect_to_login=False) 

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
        try:
            msg_type = message.get('type')
            print(f"📩 UI Thread Processing: {message}")
    
            if msg_type == 'CONNECTION_SUCCESS':
                print("Connection successful...")
                
                # Kiểm tra xem đang Login hay Register
                if getattr(self, 'is_registering', False):
                    # Gửi lệnh Đăng Ký
                    print("Sending REGISTER info...")
                    self.network.send({
                        'type': 'REGISTER', 
                        'username': self.pending_username, 
                        'password': self.pending_password,
                        'display_name': self.pending_display_name
                    })
                    # Reset cờ
                    self.is_registering = False
                else:
                    # Gửi lệnh Đăng Nhập (như cũ)
                    print("Sending LOGIN info...")
                    self.network.send({
                        'type': 'LOGIN', 
                        'username': self.pending_username, 
                        'password': self.pending_password
                    })
            
            elif msg_type == 'CONNECTION_FAILED':
                # Nếu đang ở màn hình login thì hiển thị lỗi lên giao diện
                if 'login' in self.views and self.current_room is None:
                    self.views['login'].set_status(f"Lỗi kết nối: {message.get('error')}", "red")
                    self.views['login'].set_login_button_state(True)
                else:
                    messagebox.showerror("Connection Failed", f"Could not connect to server.\n{message.get('error', '')}")
            
            elif msg_type == 'DISCONNECTED':
                # CHỈ HIỆN THÔNG BÁO NẾU KHÔNG PHẢI DO NGƯỜI DÙNG BẤM LOGOUT
                if not self.is_logging_out:
                    messagebox.showinfo("Disconnected", "Mất kết nối tới máy chủ.")
                    self.show_view('login')
                self.is_logging_out = False


            elif msg_type == 'LOGIN_SUCCESS':
                self.on_login_success(message)

            elif msg_type in ['ROOM_LIST', 'ONLINE_PLAYERS']:
                if 'lobby' in self.views: self.views['lobby'].handle_message(message)

            elif msg_type == 'VIEW_MATCH_INFO':
                # Khi nhận thông tin trận đấu -> Chuyển màn hình luôn
                if 'game' in self.views: 
                    self.views['game'].handle_message(message)
                    self.show_view('game')

            elif msg_type in ['ROOM_CREATED', 'ROOM_JOINED', 'OPPONENT_MOVE', 
                             'GAME_OVER', 'OPPONENT_LEFT', 'CHAT', 'BOARD_STATE']:
                             
                # --- CHẶN VÀO PHÒNG NẾU ĐÃ HỦY ---
                if msg_type == 'ROOM_CREATED' and self.pending_action is None:
                    print("⚠️ Received ROOM_CREATED but action canceled. Leaving...")
                    room_id = message.get('room_id')
                    try:
                        self.network.send({'type': 'LEAVE_ROOM', 'room_id': room_id})
                    except: pass
                    return # Dừng xử lý
                # ---------------------------------
                
                if msg_type == 'ROOM_CREATED':
                    # Nếu là Quick Match -> KHÔNG CHUYỂN MÀN HÌNH GAME
                    is_quick = message.get('is_quick_match', False)
                    if is_quick:
                        self.current_room = message.get('room_id') # Nhưng vẫn lưu room_id
                        # Vẫn giữ pending_action là 'quick_match'
                        return 

                # Reset pending action khi vào phòng thành công (cho join hoặc created thường)
                if msg_type in ['ROOM_CREATED', 'ROOM_JOINED']:
                    self.pending_action = None

                if 'game' in self.views: 
                    self.views['game'].handle_message(message)
                    # Tự động chuyển màn hình khi vào phòng
                    if msg_type in ['ROOM_CREATED', 'ROOM_JOINED']:
                        self.show_view('game')

            elif msg_type == 'PROFILE_UPDATED':
                # Update App State
                self.display_name = message.get('display_name', self.display_name)
                self.avatar_id = message.get('avatar_id', self.avatar_id)
                
                # Update UI
                if 'lobby' in self.views:
                    self.views['lobby'].update_user_info()
                    
                if 'profile' in self.views: 
                    self.views['profile'].handle_message(message)

            elif msg_type == 'ERROR':
                err_msg = message.get('message', 'Unknown Error')
                
                # Nếu đang ở màn hình login (chưa vào phòng) -> Hiển thị lỗi lên form đăng nhập
                if self.current_room is None and 'login' in self.views:
                     self.views['login'].set_status(err_msg, "red")
                     self.views['login'].set_login_button_state(True)
                else:
                    # Nếu đang chơi hoặc ở lobby -> Hiện popup
                    messagebox.showerror("Error", err_msg)

        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()

    def on_login_success(self, message):
        """Handle successful login"""
        self.username = self.pending_username
        self.display_name = message.get('display_name', self.username)
        self.avatar_id = message.get('avatar_id', 0) # Store avatar_id
        self.window.title(f"Caro Game - {self.username}")
        
        self.pending_username = None
        self.pending_password = None
        
        self.show_view('lobby')
        if 'lobby' in self.views:
            self.views['lobby'].update_user_info()
        
        self.refresh_all_data()
        
        if hasattr(self.views['profile'], 'load_profile'):
            self.views['profile'].load_profile(self.username, self.display_name, self.avatar_id)

    # ================= NETWORK ACTIONS =================

    def login(self, username, password):
        """Start the login process."""
        if not username or not password:
            if 'login' in self.views:
                self.views['login'].set_status("Vui lòng nhập đầy đủ thông tin", "red")
            return

        # Disable login button
        if 'login' in self.views:
            self.views['login'].set_login_button_state(False)
        
        self.pending_username = username
        self.pending_password = password

        # --- FIX LỖI: TẠO MỚI SOCKET KHI LOGIN LẠI ---
        try:
            self.network.disconnect()
        except:
            pass
            
        self.network = NetworkClient()
        self.network.set_handler(self.queue_server_message)
        # ---------------------------------------------

        self.network.start_connection()

    def register(self, username, password, display_name):
        """Start the registration process."""
        self.pending_username = username
        self.pending_password = password
        self.pending_display_name = display_name
        self.is_registering = True # Cờ báo hiệu login này là để đăng ký
        
        # Disable login/reg button
        if 'login' in self.views:
            self.views['login'].set_login_button_state(False)

        # Reset connection logic clone from login
        try:
            self.network.disconnect()
        except:
            pass
            
        self.network = NetworkClient()
        self.network.set_handler(self.queue_server_message)
        self.network.start_connection()

    def logout(self, send_disconnect=True, redirect_to_login=True):
        """Logout and return to login screen"""
        self.is_logging_out = True
        
        if send_disconnect:
            try:
                self.network.disconnect()
            except:
                pass
                
        self.username = None
        self.display_name = None
        self.current_room = None
        self.game_active = False
        
        if 'login' in self.views:
            self.views['login'].set_status("") 
            self.views['login'].set_login_button_state(True)

        # THAY ĐỔI Ở ĐÂY: Chỉ chuyển màn hình nếu được phép
        if redirect_to_login:
            self.show_view('login')

    def create_room(self, password=None, time_limit=30):
        self.pending_action = 'create'
        self.network.send({
            'type': 'CREATE_ROOM',
            'password': password,
            'time_limit': time_limit
        })

    def find_match(self):
        """Gửi yêu cầu tìm trận nhanh"""
        self.pending_action = 'quick_match'
        self.network.send({'type': 'QUICK_MATCH'})

    def join_room(self, room_id, password=None):
        self.pending_action = 'join'
        self.network.send({
            'type': 'JOIN_ROOM', 
            'room_id': room_id,
            'password': password
        })

    def send_move(self, x, y):
        self.network.send({'type': 'MOVE', 'x': x, 'y': y, 'room_id': self.current_room})

    def send_chat(self, message):
        self.network.send({'type': 'CHAT', 'message': message, 'room_id': self.current_room})

    def surrender(self):
        self.network.send({'type': 'SURRENDER', 'room_id': self.current_room})

    def accept_match(self, room_id):
        self.network.send({'type': 'ACCEPT_MATCH', 'room_id': room_id})

    def decline_match(self, room_id):
        self.network.send({'type': 'DECLINE_MATCH', 'room_id': room_id})

    def refresh_all_data(self):
        self.refresh_rooms()
        self.refresh_online_players()

    def refresh_rooms(self):
        self.network.send({'type': 'GET_ROOMS'})

    def refresh_online_players(self):
        self.network.send({'type': 'GET_ONLINE_PLAYERS'})

    def view_match(self, room_id):
        self.network.send({'type': 'VIEW_MATCH', 'room_id': room_id})

    def update_profile(self, display_name, old_password, new_password, avatar_id=None):
        self.network.send({
            'type': 'EDIT_PROFILE',
            'display_name': display_name,
            'old_password': old_password,
            'new_password': new_password,
            'avatar_id': avatar_id
        })

    # ================= GAME STATE =================

    def set_game_state(self, room_id, player_symbol, game_active=True):
        self.current_room = room_id
        self.player_symbol = player_symbol
        self.game_active = game_active
        self.current_turn = 'X' 

    def get_game_state(self):
        return {
            'room_id': self.current_room,
            'player_symbol': self.player_symbol,
            'game_active': self.game_active,
            'current_turn': self.current_turn,
            'board_size': self.board_size,
            'cell_size': self.cell_size
        }

    def switch_turn(self):
        self.current_turn = 'O' if self.current_turn == 'X' else 'X'

    # ================= UTILITIES =================

    def on_close(self):
        """Handle window close"""
        self.is_logging_out = True # Tránh lỗi khi đóng app
        try:
            self.network.disconnect()
        except:
            pass
        self.window.destroy()

    def run(self):
        self.process_message_queue()
        self.window.mainloop()

if __name__ == "__main__":
    app = CaroClient()
    app.run()