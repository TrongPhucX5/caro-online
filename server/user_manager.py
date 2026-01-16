# server/user_manager.py
import json

class UserManager:
    def __init__(self, db):
        self.db = db
        self.clients = {}  # client_id -> {socket, username, user_id, room_id}
        
    def add_client(self, client_id, socket):
        self.clients[client_id] = {
            'socket': socket,
            'username': None,
            'user_id': None,
            'room_id': None
        }
        
    def get_client(self, client_id):
        return self.clients.get(client_id)
        
    def remove_client(self, client_id):
        if client_id in self.clients:
            try: 
                self.clients[client_id]['socket'].close()
            except: 
                pass
            del self.clients[client_id]
            
    def handle_message(self, client_id, message, server):
        msg_type = message.get('type')
        client = self.get_client(client_id)
        
        if msg_type == 'LOGIN':
            self.handle_login(client_id, message, server)
            
        elif msg_type == 'EDIT_PROFILE':
            self.handle_edit_profile(client_id, message, server)
            
        elif msg_type == 'GET_ONLINE_PLAYERS':
            self.send_online_players(client_id, server)
            
    def handle_login(self, client_id, message, server):
        username = message.get('username')
        password = message.get('password') 
        print(f"🔍 Auth request: User={username}, Pass={password}")

        success, result = self.db.authenticate_user(username, password)
        if success:
            client = self.get_client(client_id)
            client['username'] = result['username']
            client['user_id'] = result['id']
            # Lấy display_name từ database
            user_info = self.db.get_user_info(result['id'])
            display_name = user_info.get('display_name', result['username']) if user_info else result['username']
            
            server.send_to_client(client_id, {
                'type': 'LOGIN_SUCCESS',
                'message': f"Welcome back, {result['username']}! (Score: {result['score']})",
                'display_name': display_name
            })
            
            # Send current room list to the new user
            server.room_manager.send_room_list(client_id, server)
            
            # Broadcast new online players list to everyone
            self.broadcast_online_players(server)
            
        else:
            reg_success, reg_result = self.db.register_user(username, password)
            if reg_success:
                client = self.get_client(client_id)
                client['username'] = username
                client['user_id'] = reg_result['user_id']
                server.send_to_client(client_id, {
                    'type': 'LOGIN_SUCCESS',
                    'message': "Account created & Logged in!",
                    'display_name': username
                })
                
                # Send current room list to the new user
                server.room_manager.send_room_list(client_id, server)
                
                # Broadcast new online players list to everyone
                self.broadcast_online_players(server)
            else:
                server.send_error(client_id, "Login Failed: Wrong password or Username taken.")
                
    def handle_edit_profile(self, client_id, message, server):
        client = self.get_client(client_id)
        if not client:
            return
            
        user_id = client.get('user_id')
        display_name = message.get('display_name', '').strip()
        old_password = message.get('old_password', '').strip()
        new_password = message.get('new_password', '').strip()
        
        if not display_name:
            server.send_error(client_id, "Display name không được để trống")
            return
            
        # Kiểm tra mật khẩu cũ nếu muốn đổi mật khẩu
        if new_password:
            if not old_password:
                server.send_error(client_id, "Nhập mật khẩu cũ để đổi mật khẩu mới")
                return
                
            # Xác thực mật khẩu cũ
            auth_success, _ = self.db.authenticate_user(client['username'], old_password)
            if not auth_success:
                server.send_error(client_id, "Mật khẩu cũ không đúng")
                return
        
        # Cập nhật thông tin
        success = self.db.update_user_profile(
            user_id=user_id,
            display_name=display_name,
            new_password=new_password if new_password else None
        )
        
        if success:
            server.send_to_client(client_id, {
                'type': 'PROFILE_UPDATED',
                'message': 'Cập nhật hồ sơ thành công!'
            })
            # Broadcast danh sách online mới
            self.broadcast_online_players(server)
        else:
            server.send_error(client_id, "Cập nhật thất bại")
            
    def send_online_players(self, client_id, server):
        online_players = self.get_online_players()
        server.send_to_client(client_id, {
            'type': 'ONLINE_PLAYERS',
            'players': online_players
        })
        
    def get_online_players(self):
        online_players = []
        for cid, cdata in self.clients.items():
            if cdata.get('username'):
                # Lấy display name từ database
                user_info = self.db.get_user_info(cdata['user_id'])
                display_name = user_info.get('display_name', cdata['username']) if user_info else cdata['username']
                
                online_players.append({
                    'username': cdata['username'],
                    'display_name': display_name,
                    'user_id': cdata['user_id']
                })
        return online_players
        
    def broadcast_online_players(self, server):
        """Gửi danh sách người chơi online cho tất cả client"""
        online_players = self.get_online_players()
        
        for cid in list(self.clients.keys()):
            if self.clients[cid].get('username'):  # Chỉ gửi cho client đã login
                server.send_to_client(cid, {
                    'type': 'ONLINE_PLAYERS',
                    'players': online_players
                })
                
    def send_to_client(self, client_id, message):
        if client_id in self.clients:
            try:
                self.clients[client_id]['socket'].send(json.dumps(message).encode('utf-8'))
            except: 
                pass