# server/main.py
import socket
import threading
import json
import time

class CaroServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # client_id -> {'socket': socket, 'username': name}
        self.rooms = {}    # room_id -> {'players': [client_ids], 'game': None}
        self.room_counter = 1
        self.client_counter = 1
        self.running = False
        
    def start(self):
        """Start the server"""
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🚀 Caro Server started on {self.host}:{self.port}")
            print("📡 Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"🔗 New connection from {address}")
                    
                    # Create client handler thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        client_id = self.client_counter
        self.client_counter += 1
        
        self.clients[client_id] = {
            'socket': client_socket,
            'address': address,
            'username': None,
            'room_id': None
        }
        
        try:
            while self.running:
                # Receive data
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Parse JSON message
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.process_message(client_id, message)
                except json.JSONDecodeError:
                    print(f"Invalid JSON from client {client_id}")
                    self.send_error(client_id, "Invalid message format")
                
        except ConnectionError:
            print(f"Client {client_id} disconnected")
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            self.disconnect_client(client_id)
    
    def process_message(self, client_id, message):
        """Process incoming message from client"""
        msg_type = message.get('type')
        
        if msg_type == 'LOGIN':
            username = message.get('username', f'Player{client_id}')
            self.clients[client_id]['username'] = username
            
            # Send welcome message
            response = {
                'type': 'LOGIN_SUCCESS',
                'client_id': client_id,
                'username': username,
                'message': f'Welcome {username}!'
            }
            self.send_to_client(client_id, response)
            
            print(f"✅ {username} logged in (ID: {client_id})")
            
        elif msg_type == 'CREATE_ROOM':
            room_id = f"room_{self.room_counter}"
            self.room_counter += 1
            
            self.rooms[room_id] = {
                'id': room_id,
                'players': [client_id],
                'status': 'waiting',
                'created_at': time.time()
            }
            
            # Update client's room
            self.clients[client_id]['room_id'] = room_id
            
            response = {
                'type': 'ROOM_CREATED',
                'room_id': room_id,
                'message': f'Room {room_id} created'
            }
            self.send_to_client(client_id, response)
            
            print(f"🎮 Room {room_id} created by {self.clients[client_id]['username']}")
            
        elif msg_type == 'JOIN_ROOM':
            room_id = message.get('room_id')
            
            if room_id in self.rooms:
                room = self.rooms[room_id]
                
                if len(room['players']) < 2:  # Max 2 players
                    room['players'].append(client_id)
                    self.clients[client_id]['room_id'] = room_id
                    
                    # Notify both players
                    for pid in room['players']:
                        self.send_to_client(pid, {
                            'type': 'ROOM_JOINED',
                            'room_id': room_id,
                            'players': [self.clients[p]['username'] for p in room['players']]
                        })
                    
                    print(f"✅ {self.clients[client_id]['username']} joined room {room_id}")
                else:
                    self.send_error(client_id, "Room is full")
            else:
                self.send_error(client_id, "Room not found")
                
        elif msg_type == 'MOVE':
            room_id = self.clients[client_id].get('room_id')
            if room_id and room_id in self.rooms:
                # Broadcast move to other player
                room = self.rooms[room_id]
                for pid in room['players']:
                    if pid != client_id:  # Send to opponent
                        self.send_to_client(pid, {
                            'type': 'OPPONENT_MOVE',
                            'x': message.get('x'),
                            'y': message.get('y'),
                            'player': self.clients[client_id]['username']
                        })
    
    def send_to_client(self, client_id, message):
        """Send message to specific client"""
        if client_id in self.clients:
            try:
                client_socket = self.clients[client_id]['socket']
                data = json.dumps(message).encode('utf-8')
                client_socket.send(data)
            except Exception as e:
                print(f"Failed to send to client {client_id}: {e}")
    
    def send_error(self, client_id, error_message):
        """Send error message to client"""
        self.send_to_client(client_id, {
            'type': 'ERROR',
            'message': error_message
        })
    
    def disconnect_client(self, client_id):
        """Handle client disconnection"""
        if client_id in self.clients:
            username = self.clients[client_id].get('username', 'Unknown')
            room_id = self.clients[client_id].get('room_id')
            
            # Remove from room
            if room_id and room_id in self.rooms:
                self.rooms[room_id]['players'] = [
                    pid for pid in self.rooms[room_id]['players'] 
                    if pid != client_id
                ]
                
                # Notify other player
                for pid in self.rooms[room_id]['players']:
                    self.send_to_client(pid, {
                        'type': 'OPPONENT_LEFT',
                        'message': f'{username} left the game'
                    })
                
                # Clean empty rooms
                if len(self.rooms[room_id]['players']) == 0:
                    del self.rooms[room_id]
                    print(f"🗑 Room {room_id} removed")
            
            # Close socket
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
            
            # Remove from clients dict
            del self.clients[client_id]
            
            print(f"👋 {username} disconnected")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Close all client sockets
        for client_id in list(self.clients.keys()):
            self.disconnect_client(client_id)
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("🛑 Server stopped")
    
    def get_status(self):
        """Get server status"""
        return {
            'clients': len(self.clients),
            'rooms': len(self.rooms),
            'running': self.running
        }

def main():
    server = CaroServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n⚠️ Server interrupted by user")
        server.stop()

if __name__ == "__main__":
    main()