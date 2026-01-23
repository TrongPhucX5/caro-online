"""
Chat History Manager
Lưu và load lịch sử chat của người chơi
"""
import os
import json
from datetime import datetime

class ChatHistoryManager:
    def __init__(self, username=None):
        self.username = username
        self.history_dir = os.path.join(os.path.dirname(__file__), '..', 'chat_logs')
        self.ensure_history_dir()
        
    def ensure_history_dir(self):
        """Tạo thư mục lưu chat nếu chưa có"""
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
            
    def get_chat_file_path(self, room_id):
        """Lấy đường dẫn file chat cho phòng cụ thể"""
        if not self.username:
            return None
        filename = f"{self.username}_room_{room_id}.json"
        return os.path.join(self.history_dir, filename)
        
    def save_message(self, room_id, sender, message):
        """Lưu một tin nhắn vào lịch sử"""
        filepath = self.get_chat_file_path(room_id)
        if not filepath:
            return
            
        # Load existing history
        history = self.load_history(room_id)
        
        # Thêm message mới
        history.append({
            'sender': sender,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Giới hạn chỉ lưu 100 tin nhắn gần nhất
        if len(history) > 100:
            history = history[-100:]
            
        # Lưu vào file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CHAT HISTORY] Error saving: {e}")
            
    def load_history(self, room_id):
        """Load lịch sử chat của phòng"""
        filepath = self.get_chat_file_path(room_id)
        if not filepath or not os.path.exists(filepath):
            return []
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[CHAT HISTORY] Error loading: {e}")
            return []
            
    def clear_history(self, room_id):
        """Xóa lịch sử chat của phòng"""
        filepath = self.get_chat_file_path(room_id)
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"[CHAT HISTORY] Error clearing: {e}")
                
    def get_all_chat_files(self):
        """Lấy danh sách tất cả file chat của user"""
        if not self.username:
            return []
            
        try:
            files = [f for f in os.listdir(self.history_dir) 
                    if f.startswith(f"{self.username}_room_") and f.endswith('.json')]
            return files
        except Exception as e:
            print(f"[CHAT HISTORY] Error getting files: {e}")
            return []
            
    def export_history(self, room_id, output_path):
        """Export lịch sử chat ra file text"""
        history = self.load_history(room_id)
        if not history:
            return False
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"=== Chat History - Room {room_id} ===\n")
                f.write(f"User: {self.username}\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                for msg in history:
                    f.write(f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}\n")
                    
            return True
        except Exception as e:
            print(f"[CHAT HISTORY] Error exporting: {e}")
            return False
