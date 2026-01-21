import socket
import threading
import json
import sys
import os

# Thêm đường dẫn để import được module từ thư mục cha
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import CaroDatabase
from server.room_manager import RoomManager
from server.user_manager import UserManager

class CaroServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # KẾT NỐI DATABASE
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "../database/caro.db")
        self.db = CaroDatabase(db_path)
        
        # Khởi tạo managers
        self.user_manager = UserManager(self.db)
        self.room_manager = RoomManager()
        
        self.client_counter = 1
        self.running = False
        
    @property
    def clients(self):
        return self.user_manager.clients
    
    @property
    def rooms(self):
        return self.room_manager.rooms
        
    def start(self):
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🚀 Caro Server running on {self.host}:{self.port}")
            print("💾 Database connected successfully")
            
            while self.running:
                client_socket, address = self.server_socket.accept()
                print(f"🔗 New connection: {address}")
                thread = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)
                thread.start()
                
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.db.close()

    def handle_client(self, client_socket):
        client_id = self.client_counter
        self.client_counter += 1
        self.user_manager.add_client(client_id, client_socket)
        
        buffer = ""
        try:
            while self.running:
                try:
                    data = client_socket.recv(4096)
                    if not data: break
                    buffer += data.decode('utf-8')
                except Exception as e:
                    print(f"⚠️ Socket receive error for {client_id}: {e}")
                    break
                
                # --- ROBUST JSON PARSING (BRACE COUNTING) ---
                while True:
                    start_index = buffer.find('{')
                    if start_index == -1:
                        buffer = "" # Discard garbage
                        break
                        
                    brace_count = 0
                    end_index = -1
                    
                    for i, char in enumerate(buffer[start_index:], start=start_index):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_index = i
                                break
                    
                    if end_index != -1:
                        json_str = buffer[start_index : end_index + 1]
                        buffer = buffer[end_index + 1:] # Keep remainder
                        
                        try:
                            message = json.loads(json_str)
                            # --- SAFE MESSAGE PROCESSING ---
                            try:
                                self.process_message(client_id, message)
                            except Exception as e:
                                print(f"❌ Error processing message from {client_id}: {e}")
                                import traceback
                                traceback.print_exc()
                        except json.JSONDecodeError:
                            print(f"⚠️ Invalid JSON from {client_id}: {json_str[:50]}...")
                    else:
                        break # Incomplete message, wait for more data

        except Exception as e:
            print(f"Error client {client_id}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.disconnect_client(client_id)

    def process_message(self, client_id, message):
        msg_type = message.get('type')
        client = self.user_manager.get_client(client_id)
        
        if not client:
            return
            
        print(f"📩 Recv [{client_id}]: {msg_type}") # Log để debug

        # --- PHÂN LOẠI MESSAGE ---
        
        # Nhóm User & Hệ thống
        # THÊM 'REGISTER' VÀO ĐÂY
        if msg_type in ['LOGIN', 'REGISTER', 'EDIT_PROFILE', 'GET_ONLINE_PLAYERS']:
            self.user_manager.handle_message(client_id, message, self)
            
        # Nhóm Phòng & Trận đấu
        # THÊM 'QUICK_MATCH' VÀO ĐÂY
        elif msg_type in ['CREATE_ROOM', 'JOIN_ROOM', 'GET_ROOMS', 'LEAVE_ROOM', 'VIEW_MATCH', 'QUICK_MATCH']:
            self.room_manager.handle_message(client_id, message, self)
            
        # Nhóm Gameplay
        elif msg_type in ['MOVE', 'SURRENDER', 'PLAY_AGAIN']:
            from server.game_logic import GameLogic
            GameLogic.handle_message(client_id, message, self)
            
        # Nhóm Chat
        elif msg_type == 'CHAT':
            self.handle_chat_message(client_id, message)
            
        else:
            print(f"Unknown message type: {msg_type}")

    def handle_chat_message(self, client_id, message):
        """Xử lý tin nhắn chat"""
        client = self.user_manager.get_client(client_id)
        if not client: return
            
        room_id = client.get('room_id')
        message_content = message.get('message')
        
        if room_id and room_id in self.room_manager.rooms:
            room = self.room_manager.rooms[room_id]
            # Gửi tên hiển thị thay vì username (Fallback nếu None)
            sender_name = client.get('display_name') or client.get('username') or f"Client {client_id}"
            
            for pid in room['players']:
                if pid != client_id:
                    self.send_to_client(pid, {
                        'type': 'CHAT',
                        'sender': sender_name,
                        'message': message_content
                    })
                    
            # Broadcast to Spectators
            for spec_id in room.get('spectators', []):
                 # Don't send back to self if spectator is chatting (though spectators usually can't chat)
                 if spec_id != client_id:
                    self.send_to_client(spec_id, {
                        'type': 'CHAT',
                        'sender': sender_name,
                        'message': message_content
                    })

    def send_to_client(self, client_id, message):
        self.user_manager.send_to_client(client_id, message)

    def send_error(self, client_id, msg):
        self.send_to_client(client_id, {'type': 'ERROR', 'message': msg})

    def disconnect_client(self, client_id):
        client = self.user_manager.get_client(client_id)
        if not client: return
            
        print(f"❌ Client {client_id} disconnected")
        
        # Xử lý rời phòng trước khi xóa client
        room_id = client.get('room_id')
        if room_id and room_id in self.room_manager.rooms:
            self.room_manager.handle_client_disconnect(client_id, room_id, self)
        
        # Xóa client khỏi user manager
        self.user_manager.remove_client(client_id)
        
        # Broadcast danh sách online mới
        self.user_manager.broadcast_online_players(self)

if __name__ == "__main__":
    server = CaroServer()
    server.start()