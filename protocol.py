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
            return json.dumps(self.data).encode('utf-8')
        
        @staticmethod
        def decode(data):
            return json.loads(data.decode('utf-8'))