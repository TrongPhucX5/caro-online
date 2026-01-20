import json

class UserManager:
    def __init__(self, db):
        self.db = db
        # client_id -> {socket, username, user_id, room_id, display_name}
        self.clients = {}  
        
    def add_client(self, client_id, socket):
        self.clients[client_id] = {
            'socket': socket,
            'username': None,
            'user_id': None,
            'room_id': None,
            'display_name': None # Thêm trường này để cache
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
        # client = self.get_client(client_id) # Không cần lấy ở đây, để từng hàm tự lấy
        
        if msg_type == 'LOGIN':
            self.handle_login(client_id, message, server)
            
        elif msg_type == 'REGISTER': # --- MỚI: Xử lý đăng ký riêng ---
            self.handle_register(client_id, message, server)
            
        elif msg_type == 'EDIT_PROFILE':
            self.handle_edit_profile(client_id, message, server)
            
        elif msg_type == 'GET_ONLINE_PLAYERS':
            self.send_online_players(client_id, server)
            
    def handle_login(self, client_id, message, server):
        """Xử lý đăng nhập thuần túy"""
        username = message.get('username')
        password = message.get('password') 
        print(f"🔍 Login request: {username}")

        success, result = self.db.authenticate_user(username, password)
        
        if success:
            client = self.get_client(client_id)
            if not client: return

            # Lấy thông tin chi tiết (display_name)
            user_info = self.db.get_user_info(result['id'])
            display_name = user_info.get('display_name', result['username']) if user_info else result['username']
            
            # Lưu vào RAM để dùng sau này (Cache)
            client['username'] = result['username']
            client['user_id'] = result['id']
            client['display_name'] = display_name
            
            # Phản hồi cho Client
            server.send_to_client(client_id, {
                'type': 'LOGIN_SUCCESS',
                'message': f"Chào mừng trở lại, {display_name}!",
                'display_name': display_name
            })
            
            # Gửi dữ liệu cần thiết sau khi login
            server.room_manager.send_room_list(client_id, server)
            self.broadcast_online_players(server)
            
        else:
            server.send_error(client_id, "Sai tên đăng nhập hoặc mật khẩu!")

    def handle_register(self, client_id, message, server):
        """Xử lý đăng ký tài khoản mới"""
        username = message.get('username')
        password = message.get('password')
        display_name = message.get('display_name', username) # Lấy tên hiển thị
        
        print(f"📝 Register request: {username} ({display_name})")
        
        # 1. Gọi DB để tạo user (Username + Pass)
        # Giả sử db.register_user chỉ nhận username, password
        reg_success, reg_result = self.db.register_user(username, password)
        
        if reg_success:
            user_id = reg_result.get('user_id')
            
            # 2. Cập nhật ngay Display Name vào DB
            self.db.update_user_profile(user_id, display_name=display_name)
            
            # 3. Tự động Login luôn cho người dùng
            client = self.get_client(client_id)
            if client:
                client['username'] = username
                client['user_id'] = user_id
                client['display_name'] = display_name
            
            server.send_to_client(client_id, {
                'type': 'LOGIN_SUCCESS',
                'message': "Đăng ký thành công!",
                'display_name': display_name
            })
            
            # Gửi dữ liệu bàn chơi
            server.room_manager.send_room_list(client_id, server)
            self.broadcast_online_players(server)
            
        else:
            server.send_error(client_id, "Đăng ký thất bại: Tên đăng nhập đã tồn tại.")

    def handle_edit_profile(self, client_id, message, server):
        client = self.get_client(client_id)
        if not client: return
            
        user_id = client.get('user_id')
        display_name = message.get('display_name', '').strip()
        old_password = message.get('old_password', '').strip()
        new_password = message.get('new_password', '').strip()
        
        if not display_name:
            server.send_error(client_id, "Tên hiển thị không được để trống")
            return
            
        # Kiểm tra mật khẩu cũ nếu muốn đổi pass
        if new_password:
            if not old_password:
                server.send_error(client_id, "Cần mật khẩu cũ để đổi mật khẩu mới")
                return
            # Check pass cũ
            auth_success, _ = self.db.authenticate_user(client['username'], old_password)
            if not auth_success:
                server.send_error(client_id, "Mật khẩu cũ không đúng")
                return
        
        # Update DB
        success = self.db.update_user_profile(
            user_id=user_id,
            display_name=display_name,
            new_password=new_password if new_password else None
        )
        
        if success:
            # Cập nhật Cache trong RAM
            client['display_name'] = display_name
            
            server.send_to_client(client_id, {
                'type': 'PROFILE_UPDATED',
                'message': 'Cập nhật hồ sơ thành công!'
            })
            # Thông báo cho mọi người biết mình đổi tên
            self.broadcast_online_players(server)
            # Cập nhật lại danh sách phòng (vì tên trong phòng có thể thay đổi)
            server.room_manager.broadcast_room_list(server)
        else:
            server.send_error(client_id, "Lỗi hệ thống: Cập nhật thất bại")
            
    def send_online_players(self, client_id, server):
        online_players = self.get_online_players()
        server.send_to_client(client_id, {
            'type': 'ONLINE_PLAYERS',
            'players': online_players
        })
        
    def get_online_players(self):
        """Lấy danh sách online từ RAM (nhanh hơn gọi DB)"""
        online_players = []
        for cid, cdata in self.clients.items():
            if cdata.get('username'): # Chỉ lấy người đã login
                # Ưu tiên lấy display_name từ RAM, nếu không có thì lấy username
                d_name = cdata.get('display_name') or cdata.get('username')
                
                online_players.append({
                    'username': cdata['username'],
                    'display_name': d_name,
                    'user_id': cdata['user_id']
                })
        return online_players
        
    def broadcast_online_players(self, server):
        """Gửi danh sách người chơi online cho tất cả client"""
        online_players = self.get_online_players()
        
        for cid in list(self.clients.keys()):
            if self.clients[cid].get('username'):
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