"""Cayenne LPP (Low Power Payload) decoder -- application-side Python.

For a codec you can paste into ChirpStack or The Things Stack, use
decoders/js/cayenne_lpp.js (those platforms run JavaScript, not Python).
"""

import struct
from typing import Dict, Any, List

def _s24(x: bytes) -> int:
    """Signed 24-bit big-endian (GPS fields can be negative)."""
    value = int.from_bytes(x, "big")
    return value - 0x1000000 if value & 0x800000 else value


def _xyz(x: bytes, scale: float) -> Dict[str, float]:
    return {axis: struct.unpack(">h", x[i:i + 2])[0] / scale
            for axis, i in (("x", 0), ("y", 2), ("z", 4))}


# Cayenne LPP data types. IDs 0-115 + 134/136 are the original myDevices spec
# (IPSO id - 3200); the rest are the extended set used by the ElectronicCats /
# TTN CayenneLPP libraries. Sizes in bytes, big-endian.
LPP_TYPES = {
    0: {"name": "digital_input", "size": 1, "decode": lambda x: x[0]},
    1: {"name": "digital_output", "size": 1, "decode": lambda x: x[0]},
    2: {"name": "analog_input", "size": 2, "decode": lambda x: struct.unpack(">h", x)[0] / 100.0},
    3: {"name": "analog_output", "size": 2, "decode": lambda x: struct.unpack(">h", x)[0] / 100.0},
    100: {"name": "generic", "size": 4, "decode": lambda x: struct.unpack(">I", x)[0]},
    101: {"name": "illuminance", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0]},
    102: {"name": "presence", "size": 1, "decode": lambda x: x[0]},
    103: {"name": "temperature", "size": 2, "decode": lambda x: struct.unpack(">h", x)[0] / 10.0},
    104: {"name": "humidity", "size": 1, "decode": lambda x: x[0] / 2.0},
    113: {"name": "accelerometer", "size": 6, "decode": lambda x: _xyz(x, 1000.0)},
    115: {"name": "barometer", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0] / 10.0},
    116: {"name": "voltage", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0] / 100.0},
    117: {"name": "current", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0] / 1000.0},
    118: {"name": "frequency", "size": 4, "decode": lambda x: struct.unpack(">I", x)[0]},
    120: {"name": "percentage", "size": 1, "decode": lambda x: x[0]},
    121: {"name": "altitude", "size": 2, "decode": lambda x: struct.unpack(">h", x)[0]},
    125: {"name": "concentration", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0]},
    128: {"name": "power", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0]},
    130: {"name": "distance", "size": 4, "decode": lambda x: struct.unpack(">I", x)[0] / 1000.0},
    131: {"name": "energy", "size": 4, "decode": lambda x: struct.unpack(">I", x)[0] / 1000.0},
    132: {"name": "direction", "size": 2, "decode": lambda x: struct.unpack(">H", x)[0]},
    133: {"name": "unixtime", "size": 4, "decode": lambda x: struct.unpack(">I", x)[0]},
    134: {"name": "gyrometer", "size": 6, "decode": lambda x: _xyz(x, 100.0)},
    135: {"name": "colour", "size": 3, "decode": lambda x: {"r": x[0], "g": x[1], "b": x[2]}},
    136: {"name": "gps", "size": 9, "decode": lambda x: {
        "latitude": _s24(x[0:3]) / 10000.0,
        "longitude": _s24(x[3:6]) / 10000.0,
        "altitude": _s24(x[6:9]) / 100.0
    }},
    142: {"name": "switch", "size": 1, "decode": lambda x: x[0]},
}


def decode_detailed(payload: bytes) -> Dict[str, Any]:
    """Decode and say why decoding stopped, if it stopped early.

    Returns {"data": {...}, "warnings": [...]} -- the shape ChirpStack v4 and
    The Things Stack expect from decodeUplink. Everything decoded before a bad
    field is kept; a field can never be half-decoded.
    """
    data: Dict[str, Any] = {}
    warnings: List[str] = []
    i = 0
    while i < len(payload):
        if i + 1 >= len(payload):
            warnings.append(f"trailing byte at offset {i} ignored")
            break
        channel, data_type = payload[i], payload[i + 1]
        type_info = LPP_TYPES.get(data_type)
        if type_info is None:
            warnings.append(f"unknown LPP type {data_type} at offset {i + 1}; rest of payload skipped")
            break
        size = type_info["size"]
        if i + 2 + size > len(payload):
            warnings.append(f"{type_info['name']} on channel {channel} is truncated; field skipped")
            break
        data[f"{type_info['name']}_{channel}"] = type_info["decode"](payload[i + 2:i + 2 + size])
        i += 2 + size
    return {"data": data, "warnings": warnings}


def decode(payload: bytes) -> Dict[str, Any]:
    """Decode Cayenne LPP payload to a flat dict (warnings dropped)."""
    return decode_detailed(payload)["data"]

# ChirpStack-v3-shaped interface
def Decode(fPort: int, bytes_payload: bytes, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Same call shape as a ChirpStack v3 codec, for symmetry with the JS codec."""
    return decode(bytes_payload)