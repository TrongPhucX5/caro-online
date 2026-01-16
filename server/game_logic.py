# server/game_logic.py
import json

class GameLogic:
    @staticmethod
    def handle_message(client_id, message, server):
        msg_type = message.get('type')
        
        if msg_type == 'MOVE':
            GameLogic.handle_move(client_id, message, server)
            
        elif msg_type == 'SURRENDER':
            GameLogic.handle_surrender(client_id, server)
            
        elif msg_type == 'PLAY_AGAIN':
            GameLogic.handle_play_again(client_id, server)
            
    @staticmethod
    def handle_move(client_id, message, server):
        client = server.user_manager.get_client(client_id)
        if not client:
            return
            
        room_id = client.get('room_id')
        if not room_id or room_id not in server.room_manager.rooms:
            return
            
        room = server.room_manager.rooms[room_id]
        board = room['board']
        
        try:
            p_idx = room['players'].index(client_id)
            player_num = p_idx + 1
        except:
            return
            
        x, y = message.get('x'), message.get('y')
        success, result = board.make_move(x, y, player_num)
        
        if success:
            opponent_id = room['players'][1 - p_idx]
            server.send_to_client(opponent_id, {
                'type': 'OPPONENT_MOVE',
                'x': x, 'y': y,
                'player': client['username']
            })
            
            if result == 'win':
                GameLogic.handle_game_over(room, client_id, server)
            elif result == 'draw':
                GameLogic.handle_game_over(room, None, server)
                
    @staticmethod
    def handle_surrender(client_id, server):
        client = server.user_manager.get_client(client_id)
        if not client:
            return
            
        room_id = client.get('room_id')
        if not room_id or room_id not in server.room_manager.rooms:
            return
            
        room = server.room_manager.rooms[room_id]
        
        # Người đầu hàng = Người thua -> Người kia thắng
        opponent_id = None
        for pid in room['players']:
            if pid != client_id:
                opponent_id = pid
                break
        
        if opponent_id:
            print(f"🏳️ {client['username']} surrendered!")
            GameLogic.handle_game_over(room, opponent_id, server)
            
    @staticmethod
    def handle_play_again(client_id, server):
        client = server.user_manager.get_client(client_id)
        if not client:
            return
            
        room_id = client.get('room_id')
        if not room_id or room_id not in server.room_manager.rooms:
            return
            
        room = server.room_manager.rooms[room_id]
        
        # Reset bàn cờ mới
        from shared.board import CaroBoard
        room['board'] = CaroBoard()
        room['status'] = 'playing'
        
        # Hoán đổi người đi trước (để công bằng)
        room['players'].reverse() # Đảo vị trí trong list
        
        # Gửi thông báo bắt đầu lại
        player_names = [server.user_manager.clients[p]['username'] for p in room['players']]
        for pid in room['players']:
            server.send_to_client(pid, {
                'type': 'ROOM_JOINED', # Tái sử dụng message này để client reset bàn cờ
                'room_id': room_id,
                'players': player_names
            })
        print(f"🔄 Room {room_id} restarted!")
        
    @staticmethod
    def handle_game_over(room, winner_id, server):
        room['status'] = 'finished'
        winner_name = server.user_manager.clients[winner_id]['username'] if winner_id else 'Draw'
        
        # Cập nhật điểm số trong database
        if winner_id and winner_id in server.user_manager.clients:
            winner_user_id = server.user_manager.clients[winner_id]['user_id']
            server.db.update_user_score(winner_user_id, 10)  # +10 điểm cho người thắng
            
            # Trừ điểm người thua (nếu không phải hòa)
            loser_id = None
            for pid in room['players']:
                if pid != winner_id:
                    loser_id = pid
                    break
            if loser_id and loser_id in server.user_manager.clients:
                loser_user_id = server.user_manager.clients[loser_id]['user_id']
                server.db.update_user_score(loser_user_id, -5)  # -5 điểm cho người thua
        
        # Gửi thông báo kết thúc game
        for pid in room['players']:
            server.send_to_client(pid, {
                'type': 'GAME_OVER',
                'message': f"GAME OVER! Winner: {winner_name}",
                'winner': winner_name if winner_id else 'Draw'
            })
        
        # Cập nhật danh sách online players
        server.user_manager.broadcast_online_players(server)