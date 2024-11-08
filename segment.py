from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import json

class SegmentType(Enum):
    """Types of segments in our transport protocol"""
    SYN = "SYN"           # Synchronize - Initialize connection
    SYN_ACK = "SYN_ACK"   # Synchronize-Acknowledge - Accept connection
    ACK = "ACK"           # Acknowledge - Confirm receipt
    DATA = "DATA"         # Data - Carry payload
    FIN = "FIN"          # Finish - End connection

@dataclass
class Segment:
    """Represent a transport layer segment"""
    seq_num: int 
    ack_num: int
    flags: SegmentType
    payload: Optional[Dict[str, Any]] = None

    def to_bytes(self) -> bytes:
        """Convert segment to bytes for transmission"""
        data = {
            "seq_num": self.seq_num,
            "ack_num": self.ack_num,
            "flags": self.flags.value,
            "payload": self.payload
        }
        return json.dumps(data).encode('utf-8')
    
    @staticmethod
    def from_bytes(data: bytes) -> 'Segment':
        """Create segment from received bytes"""
        try:
            decoded = json.loads(data.decode('utf-8'))
            return Segment(
                seq_num=decoded["seq_num"],
                ack_num=decoded["ack_num"],
                flags=SegmentType(decoded["flags"]),
                payload=decoded.get("payload")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid segment format: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        
# Example usage and testing
if __name__ == "__main__":
    # Create a test segment
    test_segment = Segment(
        seq_num=1,
        ack_num=0,
        flags=SegmentType.SYN,
        payload={"message": "Hello"}
    )
    
    # Convert to bytes (simulate sending)
    segment_bytes = test_segment.to_bytes()
    print(f"Segment as bytes: {segment_bytes}")
    
    # Convert back from bytes (simulate receiving)
    received_segment = Segment.from_bytes(segment_bytes)
    print(f"\nReceived segment:")
    print(f"Sequence number: {received_segment.seq_num}")
    print(f"Acknowledge number: {received_segment.ack_num}")
    print(f"Flags: {received_segment.flags}")
    print(f"Payload: {received_segment.payload}")
    
    # Test error handling
    try:
        Segment.from_bytes(b"invalid json")
    except ValueError as e:
        print(f"\nHandled error with invalid data: {e}")