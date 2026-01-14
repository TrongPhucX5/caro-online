# server/main.py (BẢN FIX LỖI LOGIN & LOGIC NGÀY 2)
import socket
import threading
import json
import time
import sys
import os

# Thêm đường dẫn để import được module từ thư mục cha
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import CaroDatabase
from shared.board import CaroBoard

class CaroServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # KẾT NỐI DATABASE
        self.db = CaroDatabase("database/caro.db")
        
        self.clients = {}  # client_id -> {socket, username, user_id, room_id}
        self.rooms = {}    # room_id -> {players[], board, status}
        
        self.room_counter = 1
        self.client_counter = 1
        self.running = False
        
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
        self.clients[client_id] = {
            'socket': client_socket,
            'username': None,
            'user_id': None,
            'room_id': None
        }
        
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data: break
                
                try:
                    # Xử lý dính gói tin (TCP sticky packets)
                    buffer = data.decode('utf-8')
                    messages = []
                    temp = buffer.replace('}{', '}|{')
                    for part in temp.split('|'):
                        messages.append(part)

                    for msg_str in messages:
                        if not msg_str.strip(): continue
                        message = json.loads(msg_str)
                        self.process_message(client_id, message)
                        
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON from {client_id}")
                    
        except Exception as e:
            print(f"Error client {client_id}: {e}")
        finally:
            self.disconnect_client(client_id)

    def process_message(self, client_id, message):
        msg_type = message.get('type')
        client = self.clients[client_id]
        
        # --- 1. XỬ LÝ LOGIN / REGISTER ---
        if msg_type == 'LOGIN':
            username = message.get('username')
            # QUAN TRỌNG: Lấy password thật từ Client
            password = message.get('password') 
            
            print(f"🔍 Auth request: User={username}, Pass={password}")

            # Bước 1: Thử đăng nhập
            success, result = self.db.authenticate_user(username, password)
            
            if success:
                client['username'] = result['username']
                client['user_id'] = result['id']
                self.send_to_client(client_id, {
                    'type': 'LOGIN_SUCCESS',
                    'message': f"Welcome back, {result['username']}! (Score: {result['score']})"
                })
                print(f"✅ User {username} logged in.")
            else:
                # Bước 2: Nếu thất bại, thử Đăng ký mới
                reg_success, reg_result = self.db.register_user(username, password)
                if reg_success:
                    client['username'] = username
                    client['user_id'] = reg_result['user_id']
                    self.send_to_client(client_id, {
                        'type': 'LOGIN_SUCCESS',
                        'message': "Account created & Logged in!"
                    })
                    print(f"✅ User {username} registered.")
                else:
                    # Nếu đăng ký cũng thất bại (do trùng tên mà sai pass)
                    print(f"❌ Login failed for {username}")
                    self.send_error(client_id, "Login Failed: Wrong password or Username taken.")

        # --- 2. QUẢN LÝ PHÒNG ---
        elif msg_type == 'CREATE_ROOM':
            room_id = f"room_{self.room_counter}"
            self.room_counter += 1
            
            self.rooms[room_id] = {
                'id': room_id,
                'players': [client_id],
                'board': CaroBoard(), 
                'status': 'waiting'
            }
            client['room_id'] = room_id
            
            self.send_to_client(client_id, {'type': 'ROOM_CREATED', 'room_id': room_id})
            print(f"🏠 Room {room_id} created")

        elif msg_type == 'JOIN_ROOM':
            room_id = message.get('room_id')
            if room_id in self.rooms:
                room = self.rooms[room_id]
                if len(room['players']) < 2:
                    room['players'].append(client_id)
                    client['room_id'] = room_id
                    room['status'] = 'playing'
                    
                    # Báo cho cả 2 người
                    player_names = [self.clients[p]['username'] for p in room['players']]
                    for pid in room['players']:
                        self.send_to_client(pid, {
                            'type': 'ROOM_JOINED',
                            'room_id': room_id,
                            'players': player_names
                        })
                    print(f"✅ Client {client_id} joined {room_id}")
                else:
                    self.send_error(client_id, "Room is full")
            else:
                self.send_error(client_id, "Room not found")

        # --- 3. XỬ LÝ GAME (Moves) ---
        elif msg_type == 'MOVE':
            room_id = client.get('room_id')
            if room_id and room_id in self.rooms:
                room = self.rooms[room_id]
                board = room['board']
                
                try:
                    p_idx = room['players'].index(client_id)
                    player_num = p_idx + 1
                except: return

                x, y = message.get('x'), message.get('y')
                
                # Logic Board check
                success, result = board.make_move(x, y, player_num)
                
                if success:
                    # Gửi cho đối thủ
                    opponent_id = room['players'][1 - p_idx]
                    self.send_to_client(opponent_id, {
                        'type': 'OPPONENT_MOVE',
                        'x': x, 'y': y,
                        'player': client['username']
                    })
                    
                    if result == 'win':
                        self.handle_game_over(room, winner_id=client_id)
                    elif result == 'draw':
                        self.handle_game_over(room, winner_id=None)

    def handle_game_over(self, room, winner_id):
        room['status'] = 'finished'
        winner_name = self.clients[winner_id]['username'] if winner_id else 'Draw'
        msg = f"GAME OVER! Winner: {winner_name}"

        for pid in room['players']:
            self.send_to_client(pid, {
                'type': 'GAME_OVER',
                'message': msg,
                'winner': winner_name
            })
            
        # TODO: Lưu kết quả vào DB (Ngày 4)

    def send_to_client(self, client_id, message):
        if client_id in self.clients:
            try:
                self.clients[client_id]['socket'].send(json.dumps(message).encode('utf-8'))
            except: pass

    def send_error(self, client_id, msg):
        self.send_to_client(client_id, {'type': 'ERROR', 'message': msg})

    def disconnect_client(self, client_id):
        if client_id in self.clients:
            username = self.clients[client_id].get('username', 'Unknown')
            room_id = self.clients[client_id].get('room_id')
            
            if room_id and room_id in self.rooms:
                other_players = [p for p in self.rooms[room_id]['players'] if p != client_id]
                for pid in other_players:
                    self.send_to_client(pid, {'type': 'OPPONENT_LEFT', 'message': f'{username} disconnected'})
                
                if client_id in self.rooms[room_id]['players']:
                    self.rooms[room_id]['players'].remove(client_id)
                if not self.rooms[room_id]['players']:
                    del self.rooms[room_id]
            
            try: self.clients[client_id]['socket'].close()
            except: pass
            del self.clients[client_id]
            print(f"👋 {username} disconnected")

if __name__ == "__main__":
    server = CaroServer()
    server.start()