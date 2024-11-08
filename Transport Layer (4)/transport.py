import socket
import random
from typing import Optional, Tuple, Dict, Any
from segment import Segment, SegmentType  # Using our previous segment implementation

class TransportBase:
    """Base class for transport layer functionality"""
    def __init__(self, host='localhost', port=12345):
        # Create UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        # Initialize sequence number randomly (like TCP does)
        self.seq_num = random.randint(0, 1000)
        
    def send_segment(self, segment: Segment, addr: Tuple[str, int]) -> None:
        """Send a segment to the specified address"""
        try:
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
            return Segment.from_bytes(data), addr
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

class TransportClient(TransportBase):
    """Client-side transport functionality"""
    def __init__(self, host='localhost', port=12345):
        super().__init__(host, port)
        self.server_addr = (host, port)
    
    def send_test(self) -> bool:
        """Send a test segment to server"""
        test_segment = Segment(
            seq_num=self.seq_num,
            ack_num=0,
            flags=SegmentType.DATA,
            payload={"type": "DATA", "payload": "Test message"}
        )
        
        try:
            print(f"Sending test segment to {self.server_addr}")
            self.send_segment(test_segment, self.server_addr)
            
            # Wait for response
            print("Waiting for response...")
            response, addr = self.receive_segment(timeout=5.0)
            
            if response and response.flags == SegmentType.ACK:
                print("Test successful - received acknowledgment")
                return True
            else:
                print("Test failed - no valid response received")
                return False
                
        except Exception as e:
            print(f"Test failed with error: {e}")
            return False

class TransportServer(TransportBase):
    """Server-side transport functionality"""
    def __init__(self, host='localhost', port=12345):
        super().__init__(host, port)
        # Bind socket for receiving
        self.socket.bind((host, port))
        print(f"Server bound to {host}:{port}")
    
    def listen(self):
        """Listen for incoming segments"""
        print("Server listening...")
        while True:
            try:
                segment, addr = self.receive_segment()
                if segment and addr:
                    print(f"Received segment from {addr}: {segment}")
                    
                    # Send acknowledgment
                    ack = Segment(
                        seq_num=self.seq_num,
                        ack_num=segment.seq_num + 1,
                        flags=SegmentType.ACK
                    )
                    self.send_segment(ack, addr)
                    print(f"Sent acknowledgment to {addr}")
                    
            except KeyboardInterrupt:
                print("\nServer shutting down...")
                break
            except Exception as e:
                print(f"Error in server loop: {e}")

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
            client.send_test()
        finally:
            client.close()