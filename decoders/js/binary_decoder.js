// Port-routed binary uplink codec -- paste this whole file into the codec editor.
// A worked template: edit the three frame layouts below to match your device.
//
//   ChirpStack v4 / The Things Stack v3:  decodeUplink(input)  -> { data } or { errors }
//   ChirpStack v3:                        Decode(fPort, bytes) -> data
//
//   fPort 1: temperature int16 BE /100 degC, humidity uint8 %            (3 bytes)
//   fPort 2: latitude int32 BE /1e6, longitude int32 BE /1e6             (8 bytes)
//   fPort 3: battery uint8 %, temperature int16 BE /100, humidity uint8,
//            light uint16 BE lux                                          (6 bytes)

function s16(b, o) { var v = (b[o] << 8) | b[o + 1]; return v & 0x8000 ? v - 0x10000 : v; }
function u16(b, o) { return (b[o] << 8) | b[o + 1]; }
function s32(b, o) { return (b[o] << 24) | (b[o + 1] << 16) | (b[o + 2] << 8) | b[o + 3]; }

var FRAMES = {
  1: { size: 3, decode: function (b) { return { temperature: s16(b, 0) / 100, humidity: b[2] }; } },
  2: { size: 8, decode: function (b) { return { latitude: s32(b, 0) / 1000000, longitude: s32(b, 4) / 1000000 }; } },
  3: { size: 6, decode: function (b) {
    return { battery: b[0], temperature: s16(b, 1) / 100, humidity: b[3], light: u16(b, 4) };
  } }
};

function decodeFrame(fPort, bytes) {
  var frame = FRAMES[fPort];
  if (!frame) return { errors: ["No decoder for port " + fPort] };
  if (bytes.length < frame.size) return { errors: ["Payload too short"] };
  return { data: frame.decode(bytes) };
}

// ChirpStack v4 + The Things Stack v3
function decodeUplink(input) {
  return decodeFrame(input.fPort, input.bytes);
}

// ChirpStack v3 (same error shape as the Python/TypeScript decoders)
function Decode(fPort, bytes, variables) {
  var out = decodeFrame(fPort, bytes);
  return out.errors ? { error: out.errors[0] } : out.data;
}

if (typeof module !== "undefined") {
  module.exports = { decodeUplink: decodeUplink, Decode: Decode };
}
