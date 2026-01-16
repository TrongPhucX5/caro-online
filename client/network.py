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
        buffer = ""
        while self.connected:
            try:
                data = self.client.recv(4096).decode('utf-8')
                if not data:
                    print("Disconnected from server (no data)")
                    self.disconnect()
                    break
                
                buffer += data
                
                # Process buffer for complete JSON objects
                # A simple split based on braces can be problematic, but we'll adapt
                # the server's hint of `}{` -> `}|{`
                while '}{' in buffer:
                    buffer = buffer.replace('}{', '}|{')
                
                messages = buffer.split('|')
                
                for i, msg_str in enumerate(messages):
                    if not msg_str: continue
                    try:
                        # If it's the last part and it's incomplete, keep it in buffer
                        if i == len(messages) - 1 and not msg_str.endswith('}'):
                            buffer = msg_str
                            break

                        message = json.loads(msg_str)
                        if self.msg_handler:
                            self.msg_handler(message)
                        
                        if i == len(messages) - 1: # Clear buffer if last msg was processed
                            buffer = ""

                    except json.JSONDecodeError:
                        # If a full message fails to decode, it's likely corrupt
                        print(f"⚠️ Invalid JSON received: {msg_str}")
                        if i == len(messages) - 1:
                            buffer = msg_str # Keep potentially incomplete message
                        else: # discard corrupt message part
                            pass 
            
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