# client/network.py
import socket
import threading
import json

class NetworkClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.client = None
        self.connected = False
        self.msg_handler = None 

    def start_connection(self):
        """Starts the connection process in a new thread."""
        if self.connected:
            if self.msg_handler:
                self.msg_handler({'type': 'CONNECTION_SUCCESS'})
            return

        connect_thread = threading.Thread(target=self._threaded_connect, daemon=True)
        connect_thread.start()

    def _threaded_connect(self):
        """Tries to connect to the server. For internal use in a thread."""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(self.addr)
            self.connected = True
            print(f"✅ Connected to server at {self.host}:{self.port}")

            if self.msg_handler:
                self.msg_handler({'type': 'CONNECTION_SUCCESS'})
            
            # Start the listening thread
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            if self.msg_handler:
                self.msg_handler({'type': 'CONNECTION_FAILED', 'error': str(e)})

    def set_handler(self, handler_func):
        self.msg_handler = handler_func

    def send(self, data):
        if not self.connected or not self.client:
            return

        try:
            json_data = json.dumps(data)
            self.client.sendall(json_data.encode('utf-8')) # Use sendall for reliability
        except socket.error as e:
            print(f"❌ Send error: {e}")
            self.disconnect()

    def receive_messages(self):
        import codecs
        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        buffer = ""
        while self.connected:
            try:
                # Use raw bytes recv then decode incrementally
                chunk = self.client.recv(4096)
                if not chunk:
                    print("Disconnected from server (no data)")
                    self.disconnect()
                    break
                
                # Decode chunk safely
                data = decoder.decode(chunk, final=False)
                buffer += data
                
                # Logic tách JSON an toàn hơn (đếm ngoặc nhọn)
                while True:
                    try:
                        # Tìm vị trí start object
                        start = buffer.find('{')
                        if start == -1:
                            buffer = "" # Không có JSON -> Xóa rác
                            break
                            
                        # Tìm vị trí end object (đơn giản, giả sử không có lồng phức tạp hoặc string chứa })
                        # Cách tốt hơn: Đếm ngoặc (Stack-based)
                        brace_count = 0
                        json_end = -1
                        in_string = False
                        escape = False
                        
                        for i, char in enumerate(buffer[start:], start):
                            if char == '"' and not escape:
                                in_string = not in_string
                            elif char == '\\' and in_string:
                                escape = not escape
                            elif not escape:
                                if not in_string:
                                    if char == '{': brace_count += 1
                                    elif char == '}': 
                                        brace_count -= 1
                                        if brace_count == 0:
                                            json_end = i
                                            break
                            else:
                                escape = False  # Reset escape for next char
                                
                        if json_end != -1:
                            json_str = buffer[start:json_end+1]
                            buffer = buffer[json_end+1:]
                            
                            try:
                                message = json.loads(json_str)
                                if isinstance(message, dict):
                                    if self.msg_handler:
                                        self.msg_handler(message)
                                else:
                                    print(f"⚠️ Ignored non-dict message: {message}")
                            except json.JSONDecodeError:
                                print(f"⚠️ Invalid JSON ignored: {json_str[:50]}...")
                        else:
                            # Chưa nhận đủ packet -> Đợi loop sau
                            break
                            
                    except Exception as e:
                        print(f"Error parsing packet: {e}")
                        break 
            
            except Exception as e:
                print(f"❌ Receive error: {e}")
                self.disconnect()
                break

    def disconnect(self):
        if not self.connected:
            return
            
        self.connected = False
        try:
            if self.client:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
        except OSError as e:
            print(f"Error while disconnecting: {e}")
        finally:
            self.client = None
            print("🔌 Disconnected.")
            # Notify the main app of disconnection
            if self.msg_handler:
                self.msg_handler({'type': 'DISCONNECTED'})