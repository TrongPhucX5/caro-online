import json
import threading
from shared.board import CaroBoard

class RoomManager:
    def __init__(self):
        self.rooms = {}    # room_id -> {players[], board, status, owner}
        self.room_owners = {}  # room_id -> owner_client_id
        self.room_counter = 1
        self.lock = threading.Lock()
        
        # --- TIMEOUT MONITOR THREAD ---
        self.running = True
        self.monitor_thread = threading.Thread(target=self._timeout_loop, daemon=True)
        self.monitor_thread.start()
        
    def set_server(self, server):
        self.server_instance = server



    def _timeout_loop(self):
        """Luồng chạy ngầm kiểm tra hết giờ"""
        import time
        from server.game_logic import GameLogic
        
        while self.running:
            time.sleep(1) # Kiểm tra mỗi giây
            
            if not hasattr(self, 'server_instance'):
                continue

            try:
                # Dùng lock để lấy danh sách phòng an toàn
                current_rooms = []
                with self.lock:
                    # Chỉ lấy các phòng đang chơi
                    for r_id, room in self.rooms.items():
                        if room['status'] == 'playing':
                            current_rooms.append(room)
                
                # Duyệt qua từng phòng (ngoài lock để tránh treo)
                now = time.time()
                for room in current_rooms:
                    try:
                        turn_deadline = room.get('turn_deadline')
                        if turn_deadline and now > turn_deadline:
                            print(f"⏰ Active Timeout detected in {room['id']}")
                            
                            # Xác định người bị hết giờ (là người đang có lượt đi)
                            # board.current_player: 1 (X) hoặc 2 (O)
                            # room['players'][0] là X, room['players'][1] là O
                            current_turn_idx = 0 if room['board'].current_player == 1 else 1
                            
                            if len(room['players']) > current_turn_idx:
                                timeout_player_id = room['players'][current_turn_idx]
                                
                                # Đối thủ thắng
                                opponent_idx = 1 - current_turn_idx
                                if len(room['players']) > opponent_idx:
                                    winner_id = room['players'][opponent_idx]
                                    
                                    # Gọi GameLogic để xử lý thắng thua
                                    # Cần một instance 'server' để truyền vào.
                                    GameLogic.handle_game_over(room, winner_id, self.server_instance)
                    except Exception as e_inner:
                         print(f"Error checking room {room.get('id')}: {e_inner}")

            except Exception as e:
                print(f"Error in timeout loop: {e}")
        
    def handle_message(self, client_id, message, server):
        msg_type = message.get('type')
        
        if msg_type == 'CREATE_ROOM':
            password = message.get('password')
            time_limit = message.get('time_limit', 30)
            print(f"DEBUG: Creating room with time_limit={time_limit} (type: {type(time_limit)})")
            self.create_room(client_id, server, password, time_limit)
            
        elif msg_type == 'JOIN_ROOM':
            room_id = message.get('room_id')
            password = message.get('password')
            self.join_room(client_id, room_id, server, password)
        
        # --- THÊM: XỬ LÝ TÌM TRẬN NHANH ---
        elif msg_type == 'QUICK_MATCH':
            self.quick_match(client_id, server)
            
        elif msg_type == 'ACCEPT_MATCH':
            self.accept_match(client_id, message.get('room_id'), server)
            
        elif msg_type == 'DECLINE_MATCH':
            self.decline_match(client_id, message.get('room_id'), server)
        # ----------------------------------
            
        elif msg_type == 'GET_ROOMS':
            self.send_room_list(client_id, server)
            
        elif msg_type == 'VIEW_MATCH':
            room_id = message.get('room_id')
            self.view_match(client_id, room_id, server)
            
        elif msg_type == 'LEAVE_ROOM':
            room_id = message.get('room_id')
            self.leave_room(client_id, room_id, server)


    # --- HÀM MỚI: TÌM TRẬN ---
    def quick_match(self, client_id, server):
        """Tìm phòng đang chờ có 1 người, nếu không có thì tạo mới"""
        found_room_id = None
        
        # Duyệt tìm phòng phù hợp (Chỉ tìm phòng đang WAITING)
        with self.lock:
            for r_id, room in self.rooms.items():
                if room['status'] == 'waiting' and \
                   len(room['players']) == 1 and \
                   not room.get('password'):
                
                    # Đảm bảo không tự vào phòng mình vừa tạo
                    if client_id not in room['players']:
                        found_room_id = r_id
                        break
        
        if found_room_id:
            # Tìm thấy -> VÀO LUÔN (Bỏ xác nhận kép)
            self.join_room(client_id, found_room_id, server)
            
        else:
            # Không thấy -> Tạo phòng mới
            # Truyền cờ is_quick_match=True để thông báo cho client biết mà đợi
            self.create_room(client_id, server, is_quick_match=True)

    def accept_match(self, client_id, room_id, server):
        # Deprecated: No double confirmation anymore
        pass

    def decline_match(self, client_id, room_id, server):
        # Deprecated: No double confirmation anymore
        pass
            })
            
            # Client B (pending_opp) cần reset trạng thái UI về searching? 
            # Client A (owner) vẫn ở trong phòng waiting, cần reset UI ve waiting
            
    def create_room(self, client_id, server, password=None, time_limit=30, is_quick_match=False):
        room_id = f"room_{self.room_counter}"
        self.room_counter += 1
        
        with self.lock:
            self.rooms[room_id] = {
                'id': room_id,
                'players': [client_id],
                'board': CaroBoard(), 
                'status': 'waiting',
                'owner': client_id,
                'password': password,
                'time_limit': time_limit,
                'turn_deadline': None, 
                'spectators': [],
                'match_pending': False # New flag
            }
            self.room_owners[room_id] = client_id
        
        # Cập nhật room_id cho client
        client = server.user_manager.get_client(client_id)
        if client:
            client['room_id'] = room_id
        
        # Gửi thông báo tạo phòng kèm cờ is_quick_match
        server.send_to_client(client_id, {
            'type': 'ROOM_CREATED', 
            'room_id': room_id, 
            'player_symbol': 'X',
            'is_quick_match': is_quick_match
        })

        # Broadcast cập nhật danh sách
        self.broadcast_room_list(server)
        server.user_manager.broadcast_online_players(server)
        
    def join_room(self, client_id, room_id, server, password=None):
        with self.lock:
            if room_id not in self.rooms:
                server.send_error(client_id, "Phòng không tồn tại hoặc đã giải tán")
                # Gửi lại danh sách phòng mới nhất để client cập nhật
                self.send_room_list(client_id, server)
                return
                
            room = self.rooms[room_id]
            
            # Check password
            if room.get('password') and room.get('password') != password:
                server.send_error(client_id, "Sai mật khẩu phòng!")
                return
    
            if len(room['players']) >= 2:
                server.send_error(client_id, "Phòng đã đầy")
                return
            
            if client_id in room['players']:
                 return # Đã ở trong phòng rồi
                
            room['players'].append(client_id)
            client = server.user_manager.get_client(client_id)
            if client:
                client['room_id'] = room_id
                
            room['status'] = 'playing'
            
            # --- FIX: LẤY DISPLAY NAME THAY VÌ USERNAME ---
            p1_id = room['players'][0]
            p2_id = room['players'][1]
            
            # Set initial timer
            import time
            room['turn_deadline'] = time.time() + room['time_limit'] + 2 # +2s buffer for UI

        c1 = server.user_manager.get_client(p1_id)
        c2 = server.user_manager.get_client(p2_id)
        
        # Fallback if display_name is None (DB null) or key missing
        p1_name = c1.get('display_name') or c1.get('username') or f"Client {p1_id}"
        p2_name = c2.get('display_name') or c2.get('username') or f"Client {p2_id}"
        # ---------------------------------------------

        # Gửi thông báo vào game
        server.send_to_client(p1_id, {
            'type': 'ROOM_JOINED', 'room_id': room_id, 
            'players': [p1_name, p2_name], 'player_symbol': 'X',
            'time_limit': room['time_limit']
        })
        server.send_to_client(p2_id, {
            'type': 'ROOM_JOINED', 'room_id': room_id,
            'players': [p1_name, p2_name], 'player_symbol': 'O',
            'time_limit': room['time_limit']
        })
        
        # Cập nhật danh sách phòng
        self.broadcast_room_list(server)
        server.user_manager.broadcast_online_players(server)
        
    def send_room_list(self, client_id, server):
        room_list = []
        with self.lock:
            for r_id, r in self.rooms.items():
                # --- FIX: HIỂN THỊ TÊN ĐẸP TRÊN DANH SÁCH PHÒNG ---
                player_names = []
                for p_id in r['players']:
                    c = server.user_manager.get_client(p_id)
                    if c:
                        # Fallback to 'Unknown' if both display_name and username are None (should be rare)
                        name = c.get('display_name') or c.get('username') or f"Client {p_id}"
                        player_names.append(name)
                # --------------------------------------------------
                
                match_text = " vs ".join(player_names) if player_names else "Chờ đối thủ..."
                if len(player_names) == 1:
                    match_text = f"{player_names[0]} vs ..."
                
                room_list.append({
                    'id': r_id,
                    'count': len(r['players']),
                    'status': r['status'],
                    'players': player_names,
                    'match_text': match_text,
                    'has_password': bool(r.get('password'))
                })
            
        server.send_to_client(client_id, {
            'type': 'ROOM_LIST',
            'rooms': room_list
        })
        
    def view_match(self, client_id, room_id, server):
        with self.lock:
            if room_id not in self.rooms:
                server.send_error(client_id, "Phòng không tồn tại")
                return
                
            room = self.rooms[room_id]
            # Fix tên hiển thị khi xem
            player_names = []
            for p in room['players']:
                 c = server.user_manager.get_client(p)
                 if c:
                     # Fallback to 'Unknown' if both display_name and username are None
                     name = c.get('display_name') or c.get('username') or f"Client {p}"
                     player_names.append(name)
            
            server.send_to_client(client_id, {
                'type': 'VIEW_MATCH_INFO',
                'room_id': room_id,
                'players': player_names,
                'status': room['status'],
                'time_limit': room['time_limit']
            })
            
            # Add to spectators list if not already there
            if client_id not in room['spectators']:
                room['spectators'].append(client_id)
                print(f"👀 {client_id} started spectating room {room_id}")

            # Gửi trạng thái bàn cờ hiện tại (QUAN TRỌNG)
            board_state = room['board'].get_board()
            # Convert int to 'X'/'O'
            symbols = {0: '', 1: 'X', 2: 'O'}
            converted_board = [[symbols[cell] for cell in row] for row in board_state]

            server.send_to_client(client_id, {
                'type': 'BOARD_STATE',
                'board': converted_board
            })
            
            # Gửi Timer sync luôn để khán giả biết còn bao nhiêu giây
            import time
            remaining = int(room['turn_deadline'] - time.time()) if room.get('turn_deadline') else 0
            remaining = max(0, remaining)
            
            server.send_to_client(client_id, {
                'type': 'SYNC_TIMER',
                'remaining_time': remaining
            })
            
            # Tính thời gian còn lại
            import time
            remaining = 0
            if room['turn_deadline']:
                remaining = int(room['turn_deadline'] - time.time())
                if remaining < 0: remaining = 0
            
            server.send_to_client(client_id, {
                'type': 'SYNC_TIMER',
                'remaining_time': remaining
            })
            
            # Gửi toàn bộ bàn cờ hiện tại
            board_state = []
            symbols = {1: 'X', 2: 'O'} # Map int -> symbol
            for r in range(15):
                for c in range(15):
                    piece_val = room['board'].board[r][c]
                    if piece_val != 0:
                        symbol = symbols.get(piece_val, '?')
                        board_state.append({'x': c, 'y': r, 'val': symbol}) # Send symbol, not int
            
            if board_state:
                server.send_to_client(client_id, {
                    'type': 'BOARD_STATE',
                    'moves': board_state
                })
        
    def broadcast_room_list(self, server):
        """Gửi danh sách phòng mới nhất cho tất cả mọi người"""
        # Chỉ gửi cho những người KHÔNG ở trong phòng (đang ở sảnh) để đỡ spam
        # Copy keys to avoid size change during iteration (though user_manager.clients shouldn't change much, locking there is hard)
        client_ids = list(server.user_manager.clients.keys())
        for client_id in client_ids:
            client = server.user_manager.get_client(client_id)
            if client and client.get('room_id') is None: 
                self.send_room_list(client_id, server)

    def leave_room(self, client_id, room_id, server):
        with self.lock:
            if room_id not in self.rooms:
                return
                
            room = self.rooms[room_id]
            
            # 1. Xóa người chơi khỏi list
            if client_id in room['players']:
                room['players'].remove(client_id)
            elif client_id in room['spectators']:
                room['spectators'].remove(client_id)
                print(f"👋 Spectator {client_id} left room {room_id}")
                # Spectator leaving doesn't affect game state
                return
                
            # Reset room_id của client về None
            client_left = server.user_manager.get_client(client_id)
            if client_left:
                client_left['room_id'] = None
                username_left = client_left.get('display_name', client_left.get('username', 'Unknown'))
            else:
                username_left = 'Unknown'
    
            # 2. Thông báo cho người còn lại (nếu có)
            if room['players']:
                opponent_id = room['players'][0]
                server.send_to_client(opponent_id, {
                    'type': 'OPPONENT_LEFT',
                    'message': f'{username_left} đã rời phòng'
                })
                room['status'] = 'waiting'
                # Reset bàn cờ
                room['board'] = CaroBoard()
                print(f"Room {room_id}: Player left. Waiting for new opponent.")
            
            # 3. QUAN TRỌNG: Nếu phòng TRỐNG -> XÓA NGAY LẬP TỨC
            else:
                print(f"Room {room_id} is empty. Deleting...")
                del self.rooms[room_id]
                if room_id in self.room_owners:
                    del self.room_owners[room_id]
            
        # Cập nhật UI cho mọi người
        self.broadcast_room_list(server)
        server.user_manager.broadcast_online_players(server)
            
    def handle_client_disconnect(self, client_id, room_id, server):
        self.leave_room(client_id, room_id, server)