import socket
from protocol import Message

class Client:
    def __init__(self, host='localhost', port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        
    def connect(self):
        print(f"Connecting to {self.host}:{self.port}")
        self.socket.connect((self.host, self.port))
        
        # Perform handshake
        print("Sending CONNECT message")
        handshake = Message('CONNECT', 'Requesting connection')
        self.socket.send(handshake.encode())
        
        # Wait for acceptance
        print("Waiting for server response")
        data = self.socket.recv(1024)
        if not data:
            raise ConnectionError("No response from server")
            
        response = Message.decode(data)
        print(f"Received response: {response}")
        
        if response['type'] != 'ACCEPT':
            raise Exception(f"Connection rejected: {response}")
        
        print("Connected to server!")
        
    def send_message(self, payload):
        message = Message('DATA', payload)
        self.socket.send(message.encode())
        
        # Wait for acknowledgment
        data = self.socket.recv(1024)
        if not data:
            raise ConnectionError("No response from server")
            
        response = Message.decode(data)
        return response
        
    def close(self):
        self.socket.close()
        print("Connection closed")

if __name__ == "__main__":
    client = Client()
    
    try:
        client.connect()
        
        # Send a test message
        print("Sending test message")
        response = client.send_message("Hello, this is a test message!")
        print(f"Server response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()