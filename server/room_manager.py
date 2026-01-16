# server/room_manager.py
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
            
        elif msg_type == 'GET_ROOMS':
            self.send_room_list(client_id, server)
            
        elif msg_type == 'VIEW_MATCH':
            room_id = message.get('room_id')
            self.view_match(client_id, room_id, server)
            
        elif msg_type == 'LEAVE_ROOM':
            room_id = message.get('room_id')
            self.leave_room(client_id, room_id, server)
            
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
        
        # Gửi thông báo tạo phòng thành công cho người tạo
        server.send_to_client(client_id, {'type': 'ROOM_CREATED', 'room_id': room_id, 'player_symbol': 'X'})

        # Broadcast a new room list to all clients
        self.broadcast_room_list(server)
        
        # Broadcast player list to reflect status change
        server.user_manager.broadcast_online_players(server)
        
    def join_room(self, client_id, room_id, server):
        if room_id not in self.rooms:
            server.send_error(client_id, "Room not found")
            return
            
        room = self.rooms[room_id]
        if len(room['players']) >= 2:
            server.send_error(client_id, "Room is full")
            return
            
        room['players'].append(client_id)
        client = server.user_manager.get_client(client_id)
        if client:
            client['room_id'] = room_id
            
        room['status'] = 'playing'
        
        # Xác định symbol cho người chơi
        player_one_id = room['players'][0]
        player_two_id = room['players'][1]
        player_one_username = server.user_manager.get_client(player_one_id)['username']
        player_two_username = server.user_manager.get_client(player_two_id)['username']

        # Gửi thông báo cho từng người chơi
        server.send_to_client(player_one_id, {
            'type': 'ROOM_JOINED', 'room_id': room_id, 
            'players': [player_one_username, player_two_username], 'player_symbol': 'X'
        })
        server.send_to_client(player_two_id, {
            'type': 'ROOM_JOINED', 'room_id': room_id,
            'players': [player_one_username, player_two_username], 'player_symbol': 'O'
        })
        
        # Cập nhật danh sách phòng và người chơi cho tất cả client
        self.broadcast_room_list(server)
        server.user_manager.broadcast_online_players(server)
        
    def send_room_list(self, client_id, server):
        room_list = []
        for r_id, r in self.rooms.items():
            player_names = [server.user_manager.clients[p]['username'] for p in r['players']]
            
            # Tạo "Cặp đấu" từ tên người chơi
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
        player_names = [server.user_manager.clients[p]['username'] for p in room['players']]
        
        server.send_to_client(client_id, {
            'type': 'VIEW_MATCH_INFO',
            'room_id': room_id,
            'players': player_names,
            'status': room['status']
        })
        
    def broadcast_room_list(self, server):
        """Broadcasts the updated room list to all logged-in clients."""
        for client_id in list(server.user_manager.clients.keys()):
            client = server.user_manager.get_client(client_id)
            if client and client.get('username'):
                self.send_room_list(client_id, server)

    def leave_room(self, client_id, room_id, server):
        if room_id not in self.rooms:
            return
            
        room = self.rooms[room_id]
        if client_id in room['players']:
            room['players'].remove(client_id)
            
            client_left = server.user_manager.get_client(client_id)
            if client_left:
                client_left['room_id'] = None
                username_left = client_left.get('username', 'Unknown')
            else:
                username_left = 'Unknown'

            # Thông báo cho người còn lại
            if room['players']:
                opponent_id = room['players'][0]
                server.send_to_client(opponent_id, {
                    'type': 'OPPONENT_LEFT',
                    'message': f'{username_left} đã rời phòng'
                })
                room['status'] = 'waiting'
            
            # Nếu phòng trống thì xóa
            if not room['players']:
                del self.rooms[room_id]
                if room_id in self.room_owners:
                    del self.room_owners[room_id]
            
            # Cập nhật cho mọi người
            self.broadcast_room_list(server)
            server.user_manager.broadcast_online_players(server)
            
    def handle_client_disconnect(self, client_id, room_id, server):
        """Xử lý khi client disconnect (gọi từ main server)"""
        self.leave_room(client_id, room_id, server)