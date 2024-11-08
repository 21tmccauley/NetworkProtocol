# Custom Network Protocol Implementation
## Overview
This project implements two custom network protocols for educational purposes:
1. A Transport Layer (Layer 4) protocol simulating TCP-like functionality over UDP
2. An Application Layer (Layer 7) protocol for client-server communication

The goal is to demonstrate fundamental networking concepts by building protocols from scratch, showing how different network layers interact, and implementing key features like reliable data transfer and connection management.

## Educational Purpose
This project helps understand:
- How transport layer protocols (like TCP) provide reliability over unreliable networks
- How application layer protocols build on transport layer services
- The relationship between different network layers
- Core networking concepts like:
  - Three-way handshake
  - Reliable data transfer
  - Flow control
  - Connection management
  - Client-server architecture

## Project Structure
```
└── 📁NetworkProtocol
    ├── Transport Layer (Layer 4)
    │   ├── segment.py      # Defines transport segment structure
    │   └── transport.py    # Implements reliable transport protocol
    │
    ├── Application Layer (Layer 7)
    │   ├── protocol.py     # Defines application message format
    │   ├── client.py       # Application client implementation
    │   └── server.py       # Application server implementation
    │
    └── README.md
```

## Protocol Specifications

### Transport Layer Protocol (Layer 4)
Simulates TCP-like functionality over UDP:

#### Segment Format
```python
{
    "seq_num": int,          # Sequence number
    "ack_num": int,          # Acknowledgment number
    "flags": str,            # Segment type (SYN, ACK, etc.)
    "payload": Optional[dict] # Application layer data
}
```

#### Segment Types
- SYN: Initialize connection
- SYN-ACK: Connection acknowledgment
- ACK: Data acknowledgment
- DATA: Carries payload
- FIN: Connection termination

### Application Layer Protocol (Layer 7)
Built on top of the transport layer:

#### Message Format
```python
{
    "version": "1.0",
    "type": str,            # Message type
    "timestamp": float,     # Unix timestamp
    "payload": Any          # Message content
}
```

#### Message Types
- CONNECT: Connection request
- ACCEPT: Connection accepted
- DATA: Application data
- ERROR: Error notification

## Implementation Status

### Completed Features
1. Transport Layer
   - ✅ Basic segment structure
   - ✅ UDP socket wrapper
   - ✅ Simple client-server communication

2. Application Layer
   - ✅ Message format definition
   - ✅ Basic protocol implementation
   - ✅ Connection handling

### In Progress
1. Transport Layer
   - ⏳ Three-way handshake
   - ⏳ Reliable data transfer
   - ⏳ Flow control
   - ⏳ Connection termination

2. Application Layer
   - ⏳ Integration with transport layer
   - ⏳ Enhanced error handling
   - ⏳ Multiple client support

## Running the Code

### Testing Transport Layer
1. Start transport server:
```bash
python transport.py server
```

2. Run transport client:
```bash
python transport.py
```

### Testing Application Layer
1. Start application server:
```bash
python server.py
```

2. Run application client:
```bash
python client.py
```

## Protocol Flow Examples

### Transport Layer Connection
```
Client          Server
  |     SYN      |
  |------------->|
  |   SYN-ACK    |
  |<-------------|
  |     ACK      |
  |------------->|
```

### Application Layer Communication
```
Client          Server
  |   CONNECT    |
  |------------->|
  |   ACCEPT     |
  |<-------------|
  |    DATA      |
  |------------->|
  |     ACK      |
  |<-------------|
```

## Development Roadmap
1. Phase 1 (Current)
   - Basic transport protocol implementation
   - Simple reliable data transfer
   - Basic application protocol

2. Phase 2
   - Enhanced reliability features
   - Flow control implementation
   - Improved error handling

3. Phase 3
   - Protocol optimization
   - Advanced features
   - Complete documentation

## Note
This is an educational implementation designed to demonstrate networking concepts. It simulates transport layer functionality over UDP rather than implementing a true Layer 4 protocol, which would require lower-level network access.
