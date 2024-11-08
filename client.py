import socket

#create client socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 12345

#Connect to the server
client.connect((host, port))

#Send a message to the server
message = "Hello Server!"
client.send(message.encoude('utf-8'))

#Receive a response
response = client.recv(1024).decode('utf-8')
print(f"Server response: {response}")

client.close()