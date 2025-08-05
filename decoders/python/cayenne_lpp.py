"""Cayenne LPP (Low Power Payload) decoder for ChirpStack."""

import struct
from typing import Dict, Any, List

# Cayenne LPP data types
LPP_TYPES = {
    0: {"name": "digital_input", "size": 1, "decode": lambda x: x[0]},
    1: {"name": "digital_output", "size": 1, "decode": lambda x: x[0]},
    2: {"name": "analog_input", "size": 2, "decode": lambda x: struct.unpack(">h", x)[0] / 100.0},
    3: {"name": "analog_output", "size": 2, "decode": lambda x: struct.unpack(">h", x)[0] / 100.0},
    101: {"name": "illuminance", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0]},
    102: {"name": "presence", "size": 1, "decode": lambda x: x[0]},
    103: {"name": "temperature", "size": 2, "decode": lambda x: struct.unpack(">h", x)[0] / 10.0},
    104: {"name": "humidity", "size": 1, "decode": lambda x: x[0] / 2.0},
    113: {"name": "accelerometer", "size": 6, "decode": lambda x: {
        "x": struct.unpack(">h", x[0:2])[0] / 1000.0,
        "y": struct.unpack(">h", x[2:4])[0] / 1000.0,
        "z": struct.unpack(">h", x[4:6])[0] / 1000.0
    }},
    115: {"name": "barometer", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0] / 10.0},
    116: {"name": "voltage", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0] / 100.0},
    117: {"name": "current", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0] / 1000.0},
    118: {"name": "frequency", "size": 4, "decode": lambda x: struct.unpack(">I", x)[0]},
    134: {"name": "power", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0]},
    136: {"name": "distance", "size": 4, "decode": lambda x: struct.unpack(">I", x)[0] / 1000.0},
    138: {"name": "energy", "size": 4, "decode": lambda x: struct.unpack(">I", x)[0] / 1000.0},
    142: {"name": "direction", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0]},
    188: {"name": "gps", "size": 9, "decode": lambda x: {
        "latitude": struct.unpack(">i", b"\x00" + x[0:3])[0] / 10000.0,
        "longitude": struct.unpack(">i", b"\x00" + x[3:6])[0] / 10000.0,
        "altitude": struct.unpack(">i", b"\x00" + x[6:9])[0] / 100.0
    }}
}

def decode(payload: bytes) -> Dict[str, Any]:
    """Decode Cayenne LPP payload."""
    result = {}
    i = 0
    
    while i < len(payload):
        if i + 1 >= len(payload):
            break
            
        channel = payload[i]
        data_type = payload[i + 1]
        
        if data_type not in LPP_TYPES:
            break
            
        type_info = LPP_TYPES[data_type]
        size = type_info["size"]
        
        if i + 2 + size > len(payload):
            break
            
        data = payload[i + 2:i + 2 + size]
        value = type_info["decode"](data)
        
        key = f"{type_info['name']}_{channel}"
        result[key] = value
        
        i += 2 + size
    
    return result

# ChirpStack codec interface
def Decode(fPort: int, bytes_payload: bytes, variables: Dict[str, Any]) -> Dict[str, Any]:
    """ChirpStack decoder function."""
    return decode(bytes_payload)