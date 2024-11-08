import socket
from protocol import Message

class Server:
    def __init__(self, host='localhost', port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        
    def start(self):
        self.socket.listen()
        print(f"Server listening on {self.socket.getsockname()}")
        
        while True:
            client_socket, address = self.socket.accept()
            print(f"Connection from {address}")
            
            try:
                # Handle handshake
                data = client_socket.recv(1024)
                if not data:
                    continue
                    
                message = Message.decode(data)
                print(f"Received message: {message}")
                
                if message['type'] == 'CONNECT':
                    # Send acceptance
                    response = Message('ACCEPT', 'Connection established')
                    client_socket.send(response.encode())
                    print("Sent ACCEPT response")
                    
                    # Handle client messages
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                            
                        message = Message.decode(data)
                        print(f"Received: {message}")
                        
                        # Echo back with acknowledgment
                        response = Message('ACK', message['payload'])
                        client_socket.send(response.encode())
                        
            except Exception as e:
                print(f"Error handling client: {e}")
            finally:
                client_socket.close()
                print(f"Connection closed with {address}")

if __name__ == "__main__":
    server = Server()
    server.start()