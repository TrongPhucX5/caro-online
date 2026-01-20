import json
from shared.board import CaroBoard

class RoomManager:
    def __init__(self):
        self.rooms = {}    # room_id -> {players[], board, status, owner}
        self.room_owners = {}  # room_id -> owner_client_id
        self.room_counter = 1
        
    def handle_message(self, client_id, message, server):
        msg_type = message.get('type')
        
        if msg_type == 'CREATE_ROOM':
            self.create_room(client_id, server)
            
        elif msg_type == 'JOIN_ROOM':
            room_id = message.get('room_id')
            self.join_room(client_id, room_id, server)
        
        # --- THÊM: XỬ LÝ TÌM TRẬN NHANH ---
        elif msg_type == 'QUICK_MATCH':
            self.quick_match(client_id, server)
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
        
        # Duyệt tìm phòng phù hợp
        for r_id, room in self.rooms.items():
            if room['status'] == 'waiting' and len(room['players']) == 1:
                # Đảm bảo không tự vào phòng mình vừa tạo (nếu logic client sai)
                if client_id not in room['players']:
                    found_room_id = r_id
                    break
        
        if found_room_id:
            # Tìm thấy -> Vào luôn
            self.join_room(client_id, found_room_id, server)
        else:
            # Không thấy -> Tạo phòng mới
            self.create_room(client_id, server)
            
    def create_room(self, client_id, server):
        room_id = f"room_{self.room_counter}"
        self.room_counter += 1
        self.rooms[room_id] = {
            'id': room_id,
            'players': [client_id],
            'board': CaroBoard(), 
            'status': 'waiting',
            'owner': client_id
        }
        self.room_owners[room_id] = client_id
        
        # Cập nhật room_id cho client
        client = server.user_manager.get_client(client_id)
        if client:
            client['room_id'] = room_id
        
        # Gửi thông báo tạo phòng
        server.send_to_client(client_id, {'type': 'ROOM_CREATED', 'room_id': room_id, 'player_symbol': 'X'})

        # Broadcast cập nhật danh sách
        self.broadcast_room_list(server)
        server.user_manager.broadcast_online_players(server)
        
    def join_room(self, client_id, room_id, server):
        if room_id not in self.rooms:
            server.send_error(client_id, "Phòng không tồn tại hoặc đã giải tán")
            # Gửi lại danh sách phòng mới nhất để client cập nhật
            self.send_room_list(client_id, server)
            return
            
        room = self.rooms[room_id]
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
        
        c1 = server.user_manager.get_client(p1_id)
        c2 = server.user_manager.get_client(p2_id)
        
        p1_name = c1.get('display_name', c1['username'])
        p2_name = c2.get('display_name', c2['username'])
        # ---------------------------------------------

        # Gửi thông báo vào game
        server.send_to_client(p1_id, {
            'type': 'ROOM_JOINED', 'room_id': room_id, 
            'players': [p1_name, p2_name], 'player_symbol': 'X'
        })
        server.send_to_client(p2_id, {
            'type': 'ROOM_JOINED', 'room_id': room_id,
            'players': [p1_name, p2_name], 'player_symbol': 'O'
        })
        
        # Cập nhật danh sách phòng
        self.broadcast_room_list(server)
        server.user_manager.broadcast_online_players(server)
        
    def send_room_list(self, client_id, server):
        room_list = []
        for r_id, r in self.rooms.items():
            # --- FIX: HIỂN THỊ TÊN ĐẸP TRÊN DANH SÁCH PHÒNG ---
            player_names = []
            for p_id in r['players']:
                c = server.user_manager.get_client(p_id)
                if c:
                    player_names.append(c.get('display_name', c['username']))
            # --------------------------------------------------
            
            match_text = " vs ".join(player_names) if player_names else "Chờ đối thủ..."
            if len(player_names) == 1:
                match_text = f"{player_names[0]} vs ..."
            
            room_list.append({
                'id': r_id,
                'count': len(r['players']),
                'status': r['status'],
                'players': player_names,
                'match_text': match_text
            })
            
        server.send_to_client(client_id, {
            'type': 'ROOM_LIST',
            'rooms': room_list
        })
        
    def view_match(self, client_id, room_id, server):
        if room_id not in self.rooms:
            server.send_error(client_id, "Phòng không tồn tại")
            return
            
        room = self.rooms[room_id]
        # Fix tên hiển thị khi xem
        player_names = []
        for p in room['players']:
             c = server.user_manager.get_client(p)
             player_names.append(c.get('display_name', c['username']))
        
        server.send_to_client(client_id, {
            'type': 'VIEW_MATCH_INFO',
            'room_id': room_id,
            'players': player_names,
            'status': room['status']
        })
        
    def broadcast_room_list(self, server):
        """Gửi danh sách phòng mới nhất cho tất cả mọi người"""
        # Chỉ gửi cho những người KHÔNG ở trong phòng (đang ở sảnh) để đỡ spam
        for client_id, client in server.user_manager.clients.items():
            if client.get('room_id') is None: 
                self.send_room_list(client_id, server)

    def leave_room(self, client_id, room_id, server):
        if room_id not in self.rooms:
            return
            
        room = self.rooms[room_id]
        
        # 1. Xóa người chơi khỏi list
        if client_id in room['players']:
            room['players'].remove(client_id)
            
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