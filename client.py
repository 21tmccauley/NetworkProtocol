# client.py
import socket
from protocol import Message

class Client:
    def __init__(self, host='localhost', port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        
    def connect(self):
        self.socket.connect((self.host, self.port))
        
        # Perform handshake
        handshake = Message('CONNECT', 'Requesting connection')
        self.socket.send(handshake.encode())
        
        # Wait for acceptance
        response = Message.decode(self.socket.recv(1024))
        if response['type'] != 'ACCEPT':
            raise Exception("Connection rejected")
        
        print("Connected to server!")
        
    def send_message(self, payload):
        message = Message('DATA', payload)
        self.socket.send(message.encode())
        
        # Wait for acknowledgment
        response = Message.decode(self.socket.recv(1024))
        return response
        
    def close(self):
        self.socket.close()

if __name__ == "__main__":
    client = Client()
    
    try:
        client.connect()
        
        # Send a test message
        response = client.send_message("Hello, this is a test message!")
        print(f"Server response: {response}")
        
    finally:
        client.close()