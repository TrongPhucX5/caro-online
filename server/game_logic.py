# server/game_logic.py
import json
import time

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
            
        # Check Timer
        if room['turn_deadline'] and time.time() > room['turn_deadline']:
            print(f"⏳ Time expired for {client['username']}")
            # Auto lose logic
            GameLogic.handle_game_over(room, room['players'][1 - p_idx], server) # Opponent wins
            return
            
        # Check Freeze (Pause)
        if room.get('is_frozen'):
            server.send_error(client_id, "Game đang tạm dừng chờ đối thủ kết nối lại.")
            return
            
        # Check if it's the player's turn
        # p_idx is 0 for player 1 (X), 1 for player 2 (O)
        # board.current_player is 1 for X, 2 for O
        if p_idx != (0 if room['board'].current_player == 1 else 1):
            print(f"⚠️ Move rejected: Not player's turn. Client: {client_id}, Board Turn: {room['board'].current_player}")
            return
            
        x, y = message.get('x'), message.get('y')
        success, result = board.make_move(x, y, player_num)
        
        if success:
            print(f"✅ Move valid: {x},{y} by {client_id}. Result: {result}")
            opponent_id = room['players'][1 - p_idx]
            player_name = client.get('display_name', client['username'])
            symbol = 'X' if player_num == 1 else 'O'
            
            try:
                server.send_to_client(opponent_id, {
                    'type': 'OPPONENT_MOVE',
                    'x': x, 'y': y,
                    'player': client['username'],
                    'symbol': symbol
                })
                print(f"📡 Sent OPPONENT_MOVE to {opponent_id}")
            except Exception as e:
                print(f"❌ Failed to send move to opponent {opponent_id}: {e}")
            
            # Broadcast to Spectators
            for spec_id in room.get('spectators', []):
                server.send_to_client(spec_id, {
                    'type': 'OPPONENT_MOVE',
                    'x': x, 'y': y,
                    'player': client['username'], # Or display_name if needed
                    'symbol': symbol
                })
            
            # Reset Timer
            room['turn_deadline'] = time.time() + room['time_limit']
            
            
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
        if not client: return
            
        room_id = client.get('room_id')
        if not room_id or room_id not in server.room_manager.rooms: return
            
        room = server.room_manager.rooms[room_id]
        
        # 1. Reset trạng thái phòng
        from shared.board import CaroBoard
        room['board'] = CaroBoard()
        room['status'] = 'playing'
        
        # 2. Hoán đổi vị trí (Người thắng ván trước đi sau, hoặc đổi lượt)
        if len(room['players']) < 2:
            print(f"⚠️ Cannot restart room {room.get('id')}: Not enough players.")
            server.send_error(client_id, "Đối thủ đã rời phòng. Không thể chơi lại.")
            return

        room['players'].reverse() 
        
        # 3. Lấy tên hiển thị chuẩn để gửi về Client
        p1_id = room['players'][0]
        p2_id = room['players'][1]
        c1 = server.user_manager.get_client(p1_id)
        c2 = server.user_manager.get_client(p2_id)
        
        p1_name = c1.get('display_name', c1['username'])
        p2_name = c2.get('display_name', c2['username'])
        
        # 4. Gửi thông báo start game cho TỪNG người với Symbol cụ thể
        # Người đầu tiên trong list luôn là X, người thứ 2 là O
        for i, pid in enumerate(room['players']):
            symbol = 'X' if i == 0 else 'O'
            server.send_to_client(pid, {
                'type': 'ROOM_JOINED', 
                'room_id': room_id,
                'players': [p1_name, p2_name],
                'player_symbol': symbol # <--- QUAN TRỌNG: Phải gửi cái này client mới biết ai đánh
            })
            
        # Reset Timer
        room['turn_deadline'] = time.time() + room['time_limit'] + 2 # buffer
            
        print(f"🔄 Room {room_id} restarted! X: {p1_name}, O: {p2_name}")
        
    @staticmethod
    def handle_game_over(room, winner_id, server):
        room['status'] = 'finished'
        
        # Lấy thông tin người thắng để hiển thị
        winner_username = 'Draw'
        winner_display_name = 'Draw'
        
        if winner_id:
            w_client = server.user_manager.get_client(winner_id)
            if w_client:
                winner_username = w_client['username']
                winner_display_name = w_client.get('display_name', w_client['username'])
        
        # --- CẬP NHẬT ĐIỂM SỐ (DATABASE) ---
        if winner_id and winner_id in server.user_manager.clients:
            # Cộng điểm người thắng
            winner_user_id = server.user_manager.clients[winner_id]['user_id']
            server.db.update_user_score(winner_user_id, 10)
            
            # Trừ điểm người thua
            loser_id = None
            for pid in room['players']:
                if pid != winner_id:
                    loser_id = pid
                    break
            
            if loser_id and loser_id in server.user_manager.clients:
                loser_user_id = server.user_manager.clients[loser_id]['user_id']
                server.db.update_user_score(loser_user_id, -5)
        
        # --- GỬI THÔNG BÁO ---
        for pid in room['players']:
            server.send_to_client(pid, {
                'type': 'GAME_OVER',
                'message': f"Kết thúc! Người thắng: {winner_display_name}" if winner_id else "Hòa cờ!",
                'winner': winner_username if winner_id else 'Draw' 
            })
            
        # Broadcast to Spectators
        for spec_id in room.get('spectators', []):
             server.send_to_client(spec_id, {
                'type': 'GAME_OVER',
                'message': f"Kết thúc! Người thắng: {winner_display_name}" if winner_id else "Hòa cờ!",
                'winner': winner_username if winner_id else 'Draw' 
            })
        
        # Cập nhật lại danh sách điểm số ngoài sảnh chờ
        server.user_manager.broadcast_online_players(server)