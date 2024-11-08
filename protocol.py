import json
import time

class Message:
    def __init__(self, msg_type, payload):
        self.data = {
            'version': '1.0',
            'type': msg_type,
            'timestamp': time.time(),
            'payload': payload
        }
    
    def encode(self):
        """Encode the message into bytes"""
        return json.dumps(self.data).encode('utf-8')
    
    @staticmethod
    def decode(data):
        """Decode bytes into a message dictionary"""
        if not data:  # Check if data is empty
            raise ValueError("Empty data received")
        try:
            return json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"Failed to decode message: {data}")
            raise e