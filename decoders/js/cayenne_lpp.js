// Cayenne LPP uplink codec -- paste this whole file into the codec editor.
//
//   ChirpStack v4 / The Things Stack v3:  decodeUplink(input)  -> { data, warnings }
//   ChirpStack v3:                        Decode(fPort, bytes) -> data
//
// Plain ES5, no imports, no globals besides the entry points. Type table matches
// decoders/python/cayenne_lpp.py; both are tested against examples/*.json.

var LPP_TYPES = {
  0:   { name: "digital_input",  size: 1, decode: function (b) { return b[0]; } },
  1:   { name: "digital_output", size: 1, decode: function (b) { return b[0]; } },
  2:   { name: "analog_input",   size: 2, decode: function (b) { return s16(b, 0) / 100; } },
  3:   { name: "analog_output",  size: 2, decode: function (b) { return s16(b, 0) / 100; } },
  100: { name: "generic",        size: 4, decode: function (b) { return u32(b, 0); } },
  101: { name: "illuminance",    size: 2, decode: function (b) { return u16(b, 0); } },
  102: { name: "presence",       size: 1, decode: function (b) { return b[0]; } },
  103: { name: "temperature",    size: 2, decode: function (b) { return s16(b, 0) / 10; } },
  104: { name: "humidity",       size: 1, decode: function (b) { return b[0] / 2; } },
  113: { name: "accelerometer",  size: 6, decode: function (b) { return xyz(b, 1000); } },
  115: { name: "barometer",      size: 2, decode: function (b) { return u16(b, 0) / 10; } },
  116: { name: "voltage",        size: 2, decode: function (b) { return u16(b, 0) / 100; } },
  117: { name: "current",        size: 2, decode: function (b) { return u16(b, 0) / 1000; } },
  118: { name: "frequency",      size: 4, decode: function (b) { return u32(b, 0); } },
  120: { name: "percentage",     size: 1, decode: function (b) { return b[0]; } },
  121: { name: "altitude",       size: 2, decode: function (b) { return s16(b, 0); } },
  125: { name: "concentration",  size: 2, decode: function (b) { return u16(b, 0); } },
  128: { name: "power",          size: 2, decode: function (b) { return u16(b, 0); } },
  130: { name: "distance",       size: 4, decode: function (b) { return u32(b, 0) / 1000; } },
  131: { name: "energy",         size: 4, decode: function (b) { return u32(b, 0) / 1000; } },
  132: { name: "direction",      size: 2, decode: function (b) { return u16(b, 0); } },
  133: { name: "unixtime",       size: 4, decode: function (b) { return u32(b, 0); } },
  134: { name: "gyrometer",      size: 6, decode: function (b) { return xyz(b, 100); } },
  135: { name: "colour",         size: 3, decode: function (b) { return { r: b[0], g: b[1], b: b[2] }; } },
  136: { name: "gps",            size: 9, decode: function (b) {
    return { latitude: s24(b, 0) / 10000, longitude: s24(b, 3) / 10000, altitude: s24(b, 6) / 100 };
  } },
  142: { name: "switch",         size: 1, decode: function (b) { return b[0]; } }
};

function u16(b, o) { return (b[o] << 8) | b[o + 1]; }
function s16(b, o) { var v = u16(b, o); return v & 0x8000 ? v - 0x10000 : v; }
function s24(b, o) { var v = (b[o] << 16) | (b[o + 1] << 8) | b[o + 2]; return v & 0x800000 ? v - 0x1000000 : v; }
function u32(b, o) { return ((b[o] << 24) | (b[o + 1] << 16) | (b[o + 2] << 8) | b[o + 3]) >>> 0; }
function xyz(b, scale) { return { x: s16(b, 0) / scale, y: s16(b, 2) / scale, z: s16(b, 4) / scale }; }

function decodeLpp(bytes) {
  var data = {};
  var warnings = [];
  var i = 0;
  while (i < bytes.length) {
    if (i + 1 >= bytes.length) {
      warnings.push("trailing byte at offset " + i + " ignored");
      break;
    }
    var channel = bytes[i];
    var type = LPP_TYPES[bytes[i + 1]];
    if (!type) {
      warnings.push("unknown LPP type " + bytes[i + 1] + " at offset " + (i + 1) + "; rest of payload skipped");
      break;
    }
    if (i + 2 + type.size > bytes.length) {
      warnings.push(type.name + " on channel " + channel + " is truncated; field skipped");
      break;
    }
    data[type.name + "_" + channel] = type.decode(bytes.slice(i + 2, i + 2 + type.size));
    i += 2 + type.size;
  }
  return { data: data, warnings: warnings };
}

// ChirpStack v4 + The Things Stack v3
function decodeUplink(input) {
  return decodeLpp(input.bytes);
}

// ChirpStack v3
function Decode(fPort, bytes, variables) {
  return decodeLpp(bytes).data;
}

if (typeof module !== "undefined") {
  module.exports = { decodeUplink: decodeUplink, Decode: Decode };
}
