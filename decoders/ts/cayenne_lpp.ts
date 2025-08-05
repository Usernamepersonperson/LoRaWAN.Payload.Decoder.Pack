/**
 * Cayenne LPP (Low Power Payload) decoder for ChirpStack
 */

interface LppType {
  name: string;
  size: number;
  decode: (data: Uint8Array) => any;
}

const LPP_TYPES: Record<number, LppType> = {
  0: { name: "digital_input", size: 1, decode: (x) => x[0] },
  1: { name: "digital_output", size: 1, decode: (x) => x[0] },
  2: { name: "analog_input", size: 2, decode: (x) => readInt16BE(x, 0) / 100.0 },
  3: { name: "analog_output", size: 2, decode: (x) => readInt16BE(x, 0) / 100.0 },
  101: { name: "illuminance", size: 2, decode: (x) => readUInt16BE(x, 0) },
  102: { name: "presence", size: 1, decode: (x) => x[0] },
  103: { name: "temperature", size: 2, decode: (x) => readInt16BE(x, 0) / 10.0 },
  104: { name: "humidity", size: 1, decode: (x) => x[0] / 2.0 },
  113: { 
    name: "accelerometer", 
    size: 6, 
    decode: (x) => ({
      x: readInt16BE(x, 0) / 1000.0,
      y: readInt16BE(x, 2) / 1000.0,
      z: readInt16BE(x, 4) / 1000.0
    })
  },
  115: { name: "barometer", size: 2, decode: (x) => readUInt16BE(x, 0) / 10.0 },
  116: { name: "voltage", size: 2, decode: (x) => readUInt16BE(x, 0) / 100.0 },
  117: { name: "current", size: 2, decode: (x) => readUInt16BE(x, 0) / 1000.0 },
  118: { name: "frequency", size: 4, decode: (x) => readUInt32BE(x, 0) },
  134: { name: "power", size: 2, decode: (x) => readUInt16BE(x, 0) },
  136: { name: "distance", size: 4, decode: (x) => readUInt32BE(x, 0) / 1000.0 },
  138: { name: "energy", size: 4, decode: (x) => readUInt32BE(x, 0) / 1000.0 },
  142: { name: "direction", size: 2, decode: (x) => readUInt16BE(x, 0) },
  188: { 
    name: "gps", 
    size: 9, 
    decode: (x) => ({
      latitude: readInt24BE(x, 0) / 10000.0,
      longitude: readInt24BE(x, 3) / 10000.0,
      altitude: readInt24BE(x, 6) / 100.0
    })
  }
};

function readInt16BE(buffer: Uint8Array, offset: number): number {
  return (buffer[offset] << 8) | buffer[offset + 1];
}

function readUInt16BE(buffer: Uint8Array, offset: number): number {
  return ((buffer[offset] << 8) | buffer[offset + 1]) >>> 0;
}

function readUInt32BE(buffer: Uint8Array, offset: number): number {
  return ((buffer[offset] << 24) | (buffer[offset + 1] << 16) | 
          (buffer[offset + 2] << 8) | buffer[offset + 3]) >>> 0;
}

function readInt24BE(buffer: Uint8Array, offset: number): number {
  let value = (buffer[offset] << 16) | (buffer[offset + 1] << 8) | buffer[offset + 2];
  return value > 0x7FFFFF ? value - 0x1000000 : value;
}

export function decode(payload: Uint8Array): Record<string, any> {
  const result: Record<string, any> = {};
  let i = 0;

  while (i < payload.length) {
    if (i + 1 >= payload.length) break;

    const channel = payload[i];
    const dataType = payload[i + 1];

    if (!(dataType in LPP_TYPES)) break;

    const typeInfo = LPP_TYPES[dataType];
    const size = typeInfo.size;

    if (i + 2 + size > payload.length) break;

    const data = payload.slice(i + 2, i + 2 + size);
    const value = typeInfo.decode(data);

    const key = `${typeInfo.name}_${channel}`;
    result[key] = value;

    i += 2 + size;
  }

  return result;
}

// ChirpStack codec interface
export function Decode(fPort: number, bytes: Uint8Array, variables: Record<string, any>): Record<string, any> {
  return decode(bytes);
}