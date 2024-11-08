import socket
import random
import time
from typing import Optional, Tuple, Dict, Any, List
from collections import deque
from segment import Segment, SegmentType

class TransportBase:
    """
    Base class for transport layer functionality. This implements reliability features
    on top of UDP, similar to how TCP works. This class provides the core functionality
    that both client and server will use.
    
    Key Features:
    - Reliable data transfer using sequence numbers and acknowledgments
    - In-order delivery of data
    - Buffer management for out-of-order segments
    - Timeout and retransmission handling
    """
    def __init__(self, host='localhost', port=12345):
        # Create UDP socket - we'll build TCP-like features on top of this
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        
        # Initialize sequence number randomly (like TCP does)
        # This helps prevent sequence number conflicts between connections
        self.seq_num = random.randint(0, 1000)
        
        # Track the next expected sequence number for incoming data
        self.expected_seq = None
        
        # Connection state
        self.connected = False
        
        # Reliability parameters
        self.timeout = 5.0  # seconds to wait before retransmission
        self.max_retries = 3  # maximum number of retransmission attempts
        
        # Buffer management
        # Store out-of-order segments until they can be processed
        self.receive_buffer = {}  # seq_num -> segment
        # Track segments waiting for acknowledgment
        self.unacked_segments = {}  # seq_num -> {segment, addr, timestamp}
        # Simple flow control - fixed window size
        self.window_size = 4  # number of segments that can be sent without acknowledgment

    def send_segment(self, segment: Segment, addr: Tuple[str, int]) -> None:
        """
        Send a segment to the specified address and handle bookkeeping for reliability.
        
        Args:
            segment: The Segment object to send
            addr: Tuple of (host, port) to send to
            
        If the segment is a DATA segment, it's stored in unacked_segments for
        potential retransmission if acknowledgment isn't received.
        """
        try:
            print(f"Sending {segment.flags.value} segment (SEQ={segment.seq_num}, ACK={segment.ack_num})")
            self.socket.sendto(segment.to_bytes(), addr)
            
            # Store data segments for potential retransmission
            if segment.flags == SegmentType.DATA:
                self.unacked_segments[segment.seq_num] = {
                    'segment': segment,
                    'addr': addr,
                    'timestamp': time.time()
                }
        except Exception as e:
            print(f"Error sending segment: {e}")
            raise

    def receive_segment(self, timeout: float = None) -> Tuple[Optional[Segment], Optional[Tuple[str, int]]]:
        """
        Receive a segment from the network, with optional timeout.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            Tuple of (received segment, sender address) or (None, None) if error/timeout
        """
        try:
            if timeout:
                self.socket.settimeout(timeout)
            data, addr = self.socket.recvfrom(1024)
            segment = Segment.from_bytes(data)
            print(f"Received {segment.flags.value} segment (SEQ={segment.seq_num}, ACK={segment.ack_num})")
            return segment, addr
        except socket.timeout:
            return None, None
        except Exception as e:
            print(f"Error receiving segment: {e}")
            return None, None
        finally:
            if timeout:
                self.socket.settimeout(None)

    def reliable_send(self, payload: Dict, addr: Tuple[str, int]) -> bool:
        """
        Send data with reliability guarantees (like TCP).
        
        This implements reliable data transfer using:
        - Sequence numbers
        - Acknowledgments
        - Retransmission on timeout
        
        Args:
            payload: Data to send
            addr: Destination address
            
        Returns:
            bool: True if data was successfully acknowledged, False otherwise
        """
        if not self.connected:
            print("Not connected")
            return False

        segment = Segment(
            seq_num=self.seq_num,
            ack_num=self.expected_seq,
            flags=SegmentType.DATA,
            payload=payload
        )

        # Try sending with retransmission
        for attempt in range(self.max_retries):
            try:
                self.send_segment(segment, addr)
                
                # Wait for acknowledgment
                ack_segment, _ = self.receive_segment(timeout=self.timeout)
                if (ack_segment and 
                    ack_segment.flags == SegmentType.ACK and 
                    ack_segment.ack_num == self.seq_num + 1):
                    
                    # Acknowledgment received, remove from unacked segments
                    self.unacked_segments.pop(self.seq_num, None)
                    self.seq_num += 1
                    return True
                
            except socket.timeout:
                print(f"Timeout waiting for ACK, attempt {attempt + 1}/{self.max_retries}")
                continue

        return False

    def handle_received_data(self, segment: Segment, addr: Tuple[str, int]) -> Optional[Dict]:
        """
        Handle received data segments with proper ordering.
        
        This implements in-order delivery by:
        - Processing segments that arrive in order immediately
        - Buffering out-of-order segments
        - Sending acknowledgments
        
        Args:
            segment: Received segment
            addr: Sender's address
            
        Returns:
            Optional[Dict]: Payload if segment was processed, None if buffered
        """
        if segment.seq_num == self.expected_seq:
            # Segment arrived in order
            self.expected_seq += 1
            
            # Send acknowledgment
            ack = Segment(
                seq_num=self.seq_num,
                ack_num=segment.seq_num + 1,
                flags=SegmentType.ACK
            )
            self.send_segment(ack, addr)
            
            # Process any buffered segments that are now in order
            while self.expected_seq in self.receive_buffer:
                buffered = self.receive_buffer.pop(self.expected_seq)
                self.expected_seq += 1
            
            return segment.payload
            
        elif segment.seq_num > self.expected_seq:
            # Future segment received, buffer it
            self.receive_buffer[segment.seq_num] = segment
            
            # Send ACK for last correctly received segment
            ack = Segment(
                seq_num=self.seq_num,
                ack_num=self.expected_seq,
                flags=SegmentType.ACK
            )
            self.send_segment(ack, addr)
            
        return None

    def check_timeouts(self):
        """
        Check for and retransmit any timed-out segments.
        
        This is a key part of reliability - if a segment isn't acknowledged
        within the timeout period, we assume it was lost and retransmit it.
        """
        current_time = time.time()
        for seq_num, data in list(self.unacked_segments.items()):
            if current_time - data['timestamp'] > self.timeout:
                print(f"Retransmitting segment {seq_num}")
                self.send_segment(data['segment'], data['addr'])
                data['timestamp'] = current_time

    def close(self):
        """Close the socket and cleanup"""
        self.socket.close()
        self.connected = False

class TransportClient(TransportBase):
    """
    Client-side transport implementation.
    
    This class handles:
    - Initiating connections (like TCP client)
    - Sending data reliably
    - Managing client-side connection state
    """
    def __init__(self, host='localhost', port=12345):
        super().__init__(host, port)
        self.server_addr = (host, port)

    def connect(self) -> bool:
        """
        Perform three-way handshake with server (similar to TCP).
        
        The three-way handshake:
        1. Client sends SYN
        2. Server responds with SYN-ACK
        3. Client sends ACK
        
        This establishes sequence numbers for both sides and ensures
        both parties are ready to communicate.
        
        Returns:
            bool: True if connection established, False otherwise
        """
        if self.connected:
            return True

        print("\nInitiating three-way handshake...")
        
        # Step 1: Send SYN
        syn_segment = Segment(
            seq_num=self.seq_num,
            ack_num=0,
            flags=SegmentType.SYN
        )
        
        for attempt in range(self.max_retries):
            try:
                print("\nStep 1: Sending SYN...")
                self.send_segment(syn_segment, (self.host, self.port))
                
                # Step 2: Wait for SYN-ACK
                print("Step 2: Waiting for SYN-ACK...")
                segment, addr = self.receive_segment(timeout=self.timeout)
                
                if segment and segment.flags == SegmentType.SYN_ACK:
                    # Store server's sequence number
                    server_seq = segment.seq_num
                    
                    # Step 3: Send ACK
                    print("Step 3: Sending ACK...")
                    ack_segment = Segment(
                        seq_num=self.seq_num + 1,
                        ack_num=server_seq + 1,
                        flags=SegmentType.ACK
                    )
                    self.send_segment(ack_segment, addr)
                    
                    self.seq_num += 1
                    self.connected = True
                    print("\nThree-way handshake completed successfully!")
                    return True
                    
            except socket.timeout:
                print(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
                continue
                
        print("Failed to establish connection")
        return False

    def send_message(self, payload: Dict) -> bool:
        """
        Send a message reliably to the server.
        
        Args:
            payload: The message to send
            
        Returns:
            bool: True if message was acknowledged, False otherwise
        """
        return self.reliable_send(payload, self.server_addr)

class TransportServer(TransportBase):
    """
    Server-side transport implementation.
    
    This class handles:
    - Accepting connections
    - Receiving data reliably
    - Managing server-side connection state
    - Managing multiple clients
    
    The server maintains separate state for each connected client, including:
    - Sequence numbers
    - Expected sequence numbers
    - Connection status
    """
    def __init__(self, host='localhost', port=12345):
        """
        Initialize the server with specific host and port.
        
        The server needs to bind to a specific address where it will listen
        for incoming connections.
        
        Args:
            host: Host address to bind to
            port: Port number to bind to
        """
        super().__init__(host, port)
        self.socket.bind((host, port))
        print(f"Server bound to {host}:{port}")
        # Dictionary to store per-client connection state
        self.clients = {}  # addr -> {seq_num, expected_seq}

    def accept_connection(self, syn_segment: Segment, client_addr: Tuple[str, int]) -> bool:
        """
        Handle incoming connection request (three-way handshake from server side).
        
        This method implements the server side of the TCP-like three-way handshake:
        1. Receive SYN from client
        2. Send SYN-ACK to client
        3. Receive ACK from client
        
        The server also initializes sequence number tracking for the new client.
        
        Args:
            syn_segment: The SYN segment received from client
            client_addr: Client's address tuple (host, port)
            
        Returns:
            bool: True if connection established successfully, False otherwise
        """
        print("\nHandling connection request...")
        
        try:
            # Step 2: Send SYN-ACK
            print("Step 2: Sending SYN-ACK...")
            syn_ack = Segment(
                seq_num=self.seq_num,
                ack_num=syn_segment.seq_num + 1,  # Acknowledge client's SYN
                flags=SegmentType.SYN_ACK
            )
            self.send_segment(syn_ack, client_addr)
            
            # Step 3: Wait for ACK
            print("Step 3: Waiting for ACK...")
            segment, addr = self.receive_segment(timeout=self.timeout)
            
            if segment and segment.flags == SegmentType.ACK:
                print("\nThree-way handshake completed successfully!")
                # Initialize client state with sequence numbers
                self.clients[client_addr] = {
                    'seq_num': self.seq_num + 1,  # Next sequence number to use
                    'expected_seq': segment.seq_num  # Next expected sequence from client
                }
                # Initialize base expected sequence for this connection
                self.expected_seq = segment.seq_num
                return True
                
            print("Handshake failed - didn't receive ACK")
            return False
            
        except Exception as e:
            print(f"Error in accept_connection: {e}")
            return False

    def listen(self):
        """
        Main server loop - listen for and handle incoming segments.
        
        This method continuously:
        1. Checks for timed-out segments that need retransmission
        2. Receives incoming segments
        3. Processes different types of segments:
           - SYN: New connection requests
           - DATA: Data from connected clients
        
        For DATA segments, the server:
        1. Verifies the client is known
        2. Updates sequence number tracking
        3. Processes the data in order
        4. Sends acknowledgments
        
        The loop continues until interrupted (Ctrl+C) or an unrecoverable error occurs.
        """
        print("\nServer listening...")
        while True:
            try:
                # Check for timed-out segments that need retransmission
                self.check_timeouts()
                
                # Short timeout for non-blocking behavior
                segment, addr = self.receive_segment(timeout=0.1)
                if not segment or not addr:
                    continue

                if segment.flags == SegmentType.SYN:
                    # Handle new connection request
                    self.accept_connection(segment, addr)
                    
                elif segment.flags == SegmentType.DATA:
                    if addr in self.clients:
                        print(f"\nReceived DATA segment from {addr}")
                        # Use client-specific sequence number tracking
                        self.expected_seq = self.clients[addr]['expected_seq']
                        
                        # Process data with reliability guarantees
                        payload = self.handle_received_data(segment, addr)
                        if payload:
                            print(f"Processed in-order data: {payload}")
                            # Update client's expected sequence number
                            self.clients[addr]['expected_seq'] = self.expected_seq
                    else:
                        print(f"Received data from unknown client {addr}")
                        
            except KeyboardInterrupt:
                print("\nServer shutting down...")
                break
            except Exception as e:
                print(f"Error in server loop: {e}")

class TransportClient(TransportBase):
    """
    Client-side transport implementation.
    
    This class handles:
    - Initiating connections (like TCP client)
    - Sending data reliably
    - Managing client-side connection state
    
    The client maintains sequence numbers for:
    - Its own outgoing data
    - Expected incoming acknowledgments
    """
    def __init__(self, host='localhost', port=12345):
        """
        Initialize the client with server address information.
        
        Args:
            host: Server's host address
            port: Server's port number
        """
        super().__init__(host, port)
        self.server_addr = (host, port)

    def connect(self) -> bool:
        """
        Perform three-way handshake with server (similar to TCP).
        
        The three-way handshake:
        1. Client sends SYN with initial sequence number
        2. Server responds with SYN-ACK, acknowledging client's sequence number
           and providing its own initial sequence number
        3. Client sends ACK, acknowledging server's sequence number
        
        This process:
        - Establishes sequence numbers for both sides
        - Ensures both parties are ready to communicate
        - Sets up initial connection state
        
        Returns:
            bool: True if connection established, False otherwise
        """
        if self.connected:
            return True

        print("\nInitiating three-way handshake...")
        
        # Step 1: Send SYN
        syn_segment = Segment(
            seq_num=self.seq_num,
            ack_num=0,  # Initial ACK is 0
            flags=SegmentType.SYN
        )
        
        for attempt in range(self.max_retries):
            try:
                print("\nStep 1: Sending SYN...")
                self.send_segment(syn_segment, (self.host, self.port))
                
                # Step 2: Wait for SYN-ACK
                print("Step 2: Waiting for SYN-ACK...")
                segment, addr = self.receive_segment(timeout=self.timeout)
                
                if segment and segment.flags == SegmentType.SYN_ACK:
                    # Initialize sequence number tracking
                    self.expected_seq = segment.seq_num + 1  # Next expected from server
                    
                    # Step 3: Send ACK
                    print("Step 3: Sending ACK...")
                    ack_segment = Segment(
                        seq_num=self.seq_num + 1,  # Increment our sequence number
                        ack_num=segment.seq_num + 1,  # Acknowledge server's sequence number
                        flags=SegmentType.ACK
                    )
                    self.send_segment(ack_segment, addr)
                    
                    # Update connection state
                    self.seq_num += 1
                    self.connected = True
                    print("\nThree-way handshake completed successfully!")
                    return True
                    
            except socket.timeout:
                print(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
                continue
                
        print("Failed to establish connection")
        return False

    def send_message(self, payload: Dict) -> bool:
        """
        Send a message reliably to the server.
        
        This method:
        1. Ensures connection is established
        2. Creates a DATA segment with the payload
        3. Sends it using reliable transmission
        
        Args:
            payload: The message data to send
            
        Returns:
            bool: True if message was acknowledged, False otherwise
        """
        return self.reliable_send(payload, self.server_addr)
# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Run as server
        server = TransportServer()
        try:
            server.listen()
        finally:
            server.close()
    else:
        # Run as client
        client = TransportClient()
        try:
            # Send test message
            if client.connect():
                test_payload = {
                    "type": "DATA",
                    "payload": "Test message"
                }
                if client.send_message(test_payload):
                    print("Test message sent and acknowledged successfully")
                else:
                    print("Failed to send test message")
        finally:
            client.close()