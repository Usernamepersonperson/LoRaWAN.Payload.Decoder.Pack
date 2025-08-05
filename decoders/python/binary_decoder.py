"""Simple binary frame decoder for ChirpStack."""

import struct
from typing import Dict, Any

def decode_temperature_humidity(payload: bytes) -> Dict[str, Any]:
    """Decode temperature (2 bytes) + humidity (1 byte) payload."""
    if len(payload) < 3:
        return {"error": "Payload too short"}
    
    temp = struct.unpack(">h", payload[0:2])[0] / 100.0
    humidity = payload[2]
    
    return {
        "temperature": temp,
        "humidity": humidity
    }

def decode_gps_simple(payload: bytes) -> Dict[str, Any]:
    """Decode simple GPS payload (lat: 4 bytes, lon: 4 bytes)."""
    if len(payload) < 8:
        return {"error": "Payload too short"}
    
    lat = struct.unpack(">i", payload[0:4])[0] / 1000000.0
    lon = struct.unpack(">i", payload[4:8])[0] / 1000000.0
    
    return {
        "latitude": lat,
        "longitude": lon
    }

def decode_sensor_data(payload: bytes) -> Dict[str, Any]:
    """Decode multi-sensor payload: battery (1) + temp (2) + humidity (1) + light (2)."""
    if len(payload) < 6:
        return {"error": "Payload too short"}
    
    battery = payload[0]
    temp = struct.unpack(">h", payload[1:3])[0] / 100.0
    humidity = payload[3]
    light = struct.unpack(">H", payload[4:6])[0]
    
    return {
        "battery": battery,
        "temperature": temp,
        "humidity": humidity,
        "light": light
    }

# ChirpStack codec interface
def Decode(fPort: int, bytes_payload: bytes, variables: Dict[str, Any]) -> Dict[str, Any]:
    """ChirpStack decoder function with port-based routing."""
    decoders = {
        1: decode_temperature_humidity,
        2: decode_gps_simple,
        3: decode_sensor_data
    }
    
    decoder = decoders.get(fPort)
    if decoder:
        return decoder(bytes_payload)
    
    return {"error": f"No decoder for port {fPort}"}