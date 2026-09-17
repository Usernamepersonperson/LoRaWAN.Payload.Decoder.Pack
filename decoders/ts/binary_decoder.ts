/**
 * Simple binary frame decoder for ChirpStack
 */

function readInt16BE(buffer: Uint8Array, offset: number): number {
  const value = (buffer[offset] << 8) | buffer[offset + 1];
  return value & 0x8000 ? value - 0x10000 : value; // signed: sub-zero readings
}

function readUInt16BE(buffer: Uint8Array, offset: number): number {
  return ((buffer[offset] << 8) | buffer[offset + 1]) >>> 0;
}

function readInt32BE(buffer: Uint8Array, offset: number): number {
  return (buffer[offset] << 24) | (buffer[offset + 1] << 16) | 
         (buffer[offset + 2] << 8) | buffer[offset + 3];
}

export function decodeTemperatureHumidity(payload: Uint8Array): Record<string, any> {
  if (payload.length < 3) {
    return { error: "Payload too short" };
  }

  const temp = readInt16BE(payload, 0) / 100.0;
  const humidity = payload[2];

  return {
    temperature: temp,
    humidity: humidity
  };
}

export function decodeGpsSimple(payload: Uint8Array): Record<string, any> {
  if (payload.length < 8) {
    return { error: "Payload too short" };
  }

  const lat = readInt32BE(payload, 0) / 1000000.0;
  const lon = readInt32BE(payload, 4) / 1000000.0;

  return {
    latitude: lat,
    longitude: lon
  };
}

export function decodeSensorData(payload: Uint8Array): Record<string, any> {
  if (payload.length < 6) {
    return { error: "Payload too short" };
  }

  const battery = payload[0];
  const temp = readInt16BE(payload, 1) / 100.0;
  const humidity = payload[3];
  const light = readUInt16BE(payload, 4);

  return {
    battery: battery,
    temperature: temp,
    humidity: humidity,
    light: light
  };
}

// ChirpStack codec interface
export function Decode(fPort: number, bytes: Uint8Array, variables: Record<string, any>): Record<string, any> {
  const decoders: Record<number, (payload: Uint8Array) => Record<string, any>> = {
    1: decodeTemperatureHumidity,
    2: decodeGpsSimple,
    3: decodeSensorData
  };

  const decoder = decoders[fPort];
  if (decoder) {
    return decoder(bytes);
  }

  return { error: `No decoder for port ${fPort}` };
}