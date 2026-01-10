import socket
import threading
import json

class CaroServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.games = {}
        self.player_counter = 0
        
    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"🚀 Caro Server started on {self.host}:{self.port}")
        
        while True:
            client, address = self.server.accept()
            print(f"🔗 New connection from {address}")
            threading.Thread(target=self.handle_client, args=(client,)).start()
    
    def handle_client(self, client):
        player_id = self.player_counter
        self.player_counter += 1
        self.clients.append({'id': player_id, 'socket': client})
        
        try:
            while True:
                data = client.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                message = json.loads(data)
                self.process_message(player_id, message)
                
        except:
            pass
        finally:
            self.disconnect_player(player_id)
    
    def process_message(self, player_id, message):
        msg_type = message.get('type')
        
        if msg_type == 'MOVE':
            game_id = message.get('game_id')
            x, y = message.get('x'), message.get('y')
            # Process move...
            response = {'type': 'MOVE_ACK', 'x': x, 'y': y, 'player': player_id}
            self.send_to_game(game_id, response)
    
    def send_to_game(self, game_id, message):
        # Send to all players in game
        pass
    
    def disconnect_player(self, player_id):
        print(f"👋 Player {player_id} disconnected")
        # Clean up...

if __name__ == "__main__":
    server = CaroServer()
    server.start()
