import socket
import threading
import json
import time
import ssl
import os

class NetworkClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.client = None
        self.connected = False
        self.reconnect_enabled = True # Control flag for auto-reconnect
        self.is_reconnecting = False
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
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # --- SSL CONFIGURATION ---
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cert_path = os.path.join(base_dir, "certs", "server.crt")
            
            if os.path.exists(cert_path):
                try:
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                    context.load_verify_locations(cert_path)
                    context.check_hostname = False # Localhost dev environment
                    
                    self.client = context.wrap_socket(raw_socket, server_hostname=self.host)
                    print(f"🔒 SSL/TLS Enabled using {cert_path}")
                except Exception as e:
                    print(f"⚠️ SSL Config Error: {e}, falling back to plain text")
                    self.client = raw_socket
            else:
                print("⚠️ No cert found, connecting via PLAIN TEXT...")
                self.client = raw_socket

            self.client.connect(self.addr)
            self.connected = True
            print(f"✅ Connected to server at {self.host}:{self.port}")
            
            if self.msg_handler and not self.is_reconnecting:
                self.msg_handler({'type': 'CONNECTION_SUCCESS'})
            
            # Start the listing thread
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()

            # Start Heartbeat
            threading.Thread(target=self.start_heartbeat, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            
            if self.msg_handler and not self.is_reconnecting:
                self.msg_handler({'type': 'CONNECTION_FAILED', 'error': str(e)})

            # Trigger auto-reconnect even on initial failure
            if self.reconnect_enabled and not self.is_reconnecting:
                 threading.Thread(target=self.reconnect, daemon=True).start()

    def set_handler(self, handler_func):
        self.msg_handler = handler_func

    def send(self, data):
        if not self.connected or not self.client:
            return

        try:
            json_data = json.dumps(data)
            # print(f"📤 Sending: {json_data}") # Debug log
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

    def disconnect(self, manual=False):
        if manual:
            self.reconnect_enabled = False

        if not self.connected:
            # Even if already disconnected, if it wasn't manual and we want to reconnect
            if not manual and self.reconnect_enabled and not self.is_reconnecting:
                  threading.Thread(target=self.reconnect, daemon=True).start()
            return
            
        self.connected = False
        try:
            if self.client:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
        except OSError as e:
            # print(f"Error while disconnecting: {e}")
            pass
        finally:
            self.client = None
            print("🔌 Disconnected.")
            # Notify the main app of disconnection
            if self.msg_handler:
                self.msg_handler({'type': 'DISCONNECTED'})

            # Trigger auto-reconnect if not manual
            if not manual and self.reconnect_enabled and not self.is_reconnecting:
                threading.Thread(target=self.reconnect, daemon=True).start()

    def reconnect(self):
        self.is_reconnecting = True
        print("🔄 Connection lost. Auto-reconnecting enabled.")
        
        while self.reconnect_enabled and not self.connected:
            print("⏳ Retrying in 3 seconds...")
            time.sleep(3)
            if not self.reconnect_enabled: break
            
            print("🔄 Trying to reconnect...")
            # We reuse the logic from _threaded_connect but we are already in a thread
            # Avoid spawning new threads for connect logic, just call the logic directly?
            # _threaded_connect spawns threads for receive/heartbeat ON SUCCESS.
            # So calling it is fine, but it swallows exceptions.
            # We need to know if it succeeded.
            
            # Hack: Check self.connected after a short delay or modify _threaded_connect
            # Better: refactor _threaded_connect to separate connect_socket vs start_threads
            # But for minimal changes:
            self._threaded_connect()
            
            if self.connected:
                print("✅ Reconnected successfully!")
                self.is_reconnecting = False
                if self.msg_handler:
                    self.msg_handler({'type': 'RECONNECTED'})
                return
        
        self.is_reconnecting = False

    def start_heartbeat(self):
        """Send PING every 5s to keep connection alive"""
        while self.connected:
            time.sleep(5)
            if self.connected:
                # Don't use self.send() logging to avoid cluttering console
                try:
                    self.send({'type': 'PING'})
                except:
                    break