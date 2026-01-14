# client/network.py (BẢN FIX LỖI 10056)
import socket
import threading
import json

class NetworkClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.msg_handler = None 

    def connect(self):
        """Kết nối đến server"""
        # 1. Nếu đang kết nối rồi thì báo thành công luôn, không connect lại
        if self.connected:
            return True

        try:
            # 2. Quan trọng: Tạo socket mới nếu socket cũ đã bị đóng
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            self.client.connect(self.addr)
            self.connected = True
            print(f"✅ Connected to server at {self.host}:{self.port}")
            
            # Bắt đầu luồng lắng nghe
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            return False

    def set_handler(self, handler_func):
        self.msg_handler = handler_func

    def send(self, data):
        if not self.connected:
            # print("⚠️ Not connected to server") # Bớt spam log
            return

        try:
            json_data = json.dumps(data)
            self.client.send(json_data.encode('utf-8'))
        except socket.error as e:
            print(f"❌ Send error: {e}")
            self.disconnect() # Ngắt kết nối nếu gửi lỗi

    def receive_messages(self):
        while self.connected:
            try:
                message = self.client.recv(4096).decode('utf-8')
                if not message:
                    print("Disconnected from server")
                    self.disconnect()
                    break
                
                try:
                    # Xử lý dính gói tin đơn giản
                    # (Server đã xử lý kỹ, Client xử lý cơ bản)
                    messages = message.replace('}{', '}|{').split('|')
                    for msg in messages:
                        data = json.loads(msg)
                        if self.msg_handler:
                            self.msg_handler(data)
                except json.JSONDecodeError:
                    pass
                    
            except Exception as e:
                print(f"❌ Receive error: {e}")
                self.disconnect()
                break

    def disconnect(self):
        self.connected = False
        try:
            self.client.close()
        except:
            pass