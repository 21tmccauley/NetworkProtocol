# Custom Network Protocol Implementation

## Project Overview
A custom implementation of a network protocol demonstrating fundamental concepts of network programming and client-server architecture. This project showcases the development of a reliable communication protocol with features similar to real-world protocols like TCP/IP.

## Features
- Custom message format using JSON
- Handshake mechanism for connection establishment
- Reliable message delivery with acknowledgments
- Error handling and connection management


## Technical Stack
- Python 3.x
- Socket Programming
- JSON for message serialization

## Project Structure
```
└── 📁NetworkProtocol
    └── client.py
    └── protocol.py
    └── README.md
    └── server.py
```

## Protocol Specifications

### Message Format
Each message in the protocol follows this JSON structure:
```json
{
    "version": "1.0",
    "type": "<message_type>",
    "timestamp": "<unix_timestamp>",
    "payload": "<message_data>"
}
```
### Message Types
- CONNECT: Initial connection request from client to server
- ACCEPT: Server's acceptance of connection request
- DATA: Standard data transmission message
- ACK: Acknowledgment of received message
- ERROR: Error notification message
- DISCONNECT: Connection termination request

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/project-name.git

# Navigate to the project directory
cd project-name

# Install dependencies (if any)
pip install -r requirements.txt

```
## Example Communication Flow

### Starting the Server
```bash
python server.py
```
Server will start listening on localhost:12345

### Running the Client
```bash
python client.py
```
### Protocol Flow

1. Connection Establishment:

```
CopyClient → Server: CONNECT message
Server → Client: ACCEPT message
```

2. Data Transmission:
```
CopyClient → Server: DATA message
Server → Client: ACK message
```
3. Connection Termination:
```
CopyClient → Server: DISCONNECT message
Server: Closes connection
```
## Development Notes
### Current Implementation
- Basic client-server communication established
- JSON-based message formatting
- Handshake mechanism implemented
- Error handling for common network issues
- Connection state management

### Future Enhancements
1. Short Term
   - Multiple client support using threading
   - Enhanced error handling and recovery
   - Connection timeout implementation

2. Medium Term
   - File transfer capabilities
   - Basic encryption
   - Message Compression(?)


