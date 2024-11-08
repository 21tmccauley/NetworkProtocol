import socket
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
host = 'localhost'
port = 12345

server.bind((host, port))
server.listen()
print(f"Server listening on {host}:{port}")

while True:
    client_socket, address = server.accept()
    print(f"Connection from {address}")
    
    #Recieve data
    data = client_socket.recv(1024).decode('utf-8')
    print(f"Recived: {data}")

    #Respond to client
    response = "Message received!"
    client_socket.send(response.encode('utf-8'))

    client_socket.close()    
