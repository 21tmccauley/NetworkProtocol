import socket
import random
import time
from typing import Optional, Tuple, Dict, Any
from segment import Segment, SegmentType

class TransportBase:
    def __init__(self, host='localhost', port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.seq_num = random.randint(0, 1000)
        self.connected = False
        self.timeout = 5.0  # seconds
        self.max_retries = 3
    
    def send_segment(self, segment: Segment, addr: Tuple[str, int]) -> None:
        """Send a segment to the specified address"""
        try:
            print(f"Sending {segment.flags.value} segment (SEQ={segment.seq_num}, ACK={segment.ack_num})")
            self.socket.sendto(segment.to_bytes(), addr)
        except Exception as e:
            print(f"Error sending segment: {e}")
            raise
    
    def receive_segment(self, timeout: float = None) -> Tuple[Optional[Segment], Optional[Tuple[str, int]]]:
        """Receive a segment, optionally with timeout"""
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

    def close(self):
        """Close the socket"""
        self.socket.close()
        self.connected = False

class TransportClient(TransportBase):
    def connect(self) -> bool:
        """Perform three-way handshake with server"""
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

    def send_test(self) -> bool:
        """Send a test message after establishing connection"""
        if not self.connected:
            if not self.connect():
                return False

        test_segment = Segment(
            seq_num=self.seq_num,
            ack_num=0,
            flags=SegmentType.DATA,
            payload={"type": "DATA", "payload": "Test message"}
        )
        
        try:
            print("\nSending test message...")
            self.send_segment(test_segment, (self.host, self.port))
            
            print("Waiting for acknowledgment...")
            response, _ = self.receive_segment(timeout=self.timeout)
            
            if response and response.flags == SegmentType.ACK:
                print("Test successful - received acknowledgment")
                self.seq_num += 1
                return True
            else:
                print("Test failed - no valid acknowledgment received")
                return False
                
        except Exception as e:
            print(f"Test failed with error: {e}")
            return False

class TransportServer(TransportBase):
    def __init__(self, host='localhost', port=12345):
        super().__init__(host, port)
        self.socket.bind((host, port))
        print(f"Server bound to {host}:{port}")
        self.clients = {}  # Store client state

    def accept_connection(self, syn_segment: Segment, client_addr: Tuple[str, int]) -> bool:
        """Handle three-way handshake from server side"""
        print("\nHandling connection request...")
        
        try:
            # Step 2: Send SYN-ACK
            print("Step 2: Sending SYN-ACK...")
            syn_ack = Segment(
                seq_num=self.seq_num,
                ack_num=syn_segment.seq_num + 1,
                flags=SegmentType.SYN_ACK
            )
            self.send_segment(syn_ack, client_addr)
            
            # Step 3: Wait for ACK
            print("Step 3: Waiting for ACK...")
            segment, addr = self.receive_segment(timeout=self.timeout)
            
            if segment and segment.flags == SegmentType.ACK:
                print("\nThree-way handshake completed successfully!")
                self.clients[client_addr] = {
                    'seq_num': self.seq_num + 1,
                    'expected_seq': segment.seq_num
                }
                return True
                
            print("Handshake failed - didn't receive ACK")
            return False
            
        except Exception as e:
            print(f"Error in accept_connection: {e}")
            return False

    def listen(self):
        """Listen for incoming connections and data"""
        print("\nServer listening...")
        while True:
            try:
                segment, addr = self.receive_segment()
                if not segment or not addr:
                    continue

                if segment.flags == SegmentType.SYN:
                    # Handle new connection
                    self.accept_connection(segment, addr)
                    
                elif segment.flags == SegmentType.DATA:
                    # Handle data from connected client
                    if addr in self.clients:
                        print(f"\nReceived data from {addr}: {segment.payload}")
                        
                        # Send acknowledgment
                        ack = Segment(
                            seq_num=self.clients[addr]['seq_num'],
                            ack_num=segment.seq_num + 1,
                            flags=SegmentType.ACK
                        )
                        self.send_segment(ack, addr)
                        self.clients[addr]['seq_num'] += 1
                    else:
                        print(f"Received data from unknown client {addr}")
                        
            except KeyboardInterrupt:
                print("\nServer shutting down...")
                break
            except Exception as e:
                print(f"Error in server loop: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server = TransportServer()
        try:
            server.listen()
        finally:
            server.close()
    else:
        client = TransportClient()
        try:
            client.send_test()
        finally:
            client.close()