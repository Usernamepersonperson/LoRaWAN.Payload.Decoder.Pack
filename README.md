# LoRaWAN Payload Decoder Pack

Cayenne LPP and port-routed binary uplink decoders in three forms: a JavaScript codec you paste into ChirpStack or The Things Stack, and Python / TypeScript decoders for your own application code. All three are tested against the same regression vectors.

## What runs where

| You want to decode... | Use | Entry point |
|---|---|---|
| inside **ChirpStack v4** (device profile -> Codec -> JavaScript functions) | `decoders/js/*.js` | `decodeUplink(input)` -> `{ data, warnings }` / `{ errors }` |
| inside **The Things Stack v3** (payload formatter -> Custom JavaScript) | `decoders/js/*.js` | `decodeUplink(input)` (same signature) |
| inside **ChirpStack v3** (custom JavaScript codec) | `decoders/js/*.js` | `Decode(fPort, bytes, variables)` |
| in your own **Python** service (MQTT / HTTP integration consumer) | `decoders/python/*.py` | `decode(bytes)`, `decode_detailed(bytes)`, `Decode(fPort, bytes, variables)` |
| in your own **TypeScript / Node** service | `decoders/ts/*.ts` | `decode(bytes)`, `Decode(fPort, bytes, variables)` |

ChirpStack and The Things Stack only execute JavaScript codecs. The Python and TypeScript files are for decoding on your side of the integration; they cannot be pasted into those platforms.

**How this was verified:** the JS codecs are plain ES5 with no imports and are exercised under Node against `examples/*.json`, calling them exactly the way the platforms do. They have not been run on a live ChirpStack or The Things Stack instance yet. Encoding (downlink) is not included.

## Cayenne LPP coverage

Original myDevices types: digital in/out (0, 1), analog in/out (2, 3), illuminance (101), presence (102), temperature (103), humidity (104), accelerometer (113), barometer (115), gyrometer (134), GPS (136).
Extended types (ElectronicCats / TTN CayenneLPP libraries): generic (100), voltage (116), current (117), frequency (118), percentage (120), altitude (121), concentration (125), power (128), distance (130), energy (131), direction (132), unix time (133), colour (135), switch (142).

Output keys are `<type>_<channel>`, e.g. `temperature_1`. Signed fields (temperature, analog, accelerometer, gyrometer, altitude, GPS) decode negative values correctly. An unknown type or a truncated field stops decoding, keeps everything decoded so far, and reports a warning (`decode_detailed` in Python, `warnings` in the JS codec) instead of failing silently.

## Binary decoder (template)

A worked example of port-based routing to edit for your own device:

- **Port 1**: temperature int16 BE /100 (2 bytes) + humidity (1 byte)
- **Port 2**: latitude, longitude as int32 BE /1e6 (4 + 4 bytes)
- **Port 3**: battery (1) + temperature (2) + humidity (1) + light (2)

## Structure

```
decoders/js/        cayenne_lpp.js, binary_decoder.js   (ChirpStack / The Things Stack codecs)
decoders/python/    cayenne_lpp.py, binary_decoder.py
decoders/ts/        cayenne_lpp.ts, binary_decoder.ts
examples/           regression vectors shared by every test suite
tests/              pytest + node:test
```

## Usage

ChirpStack v4: Device profile -> Codec -> "JavaScript functions" -> paste the whole of `decoders/js/cayenne_lpp.js`. The Things Stack: Payload formatters -> Uplink -> "Custom Javascript formatter" -> paste the same file.

```python
from cayenne_lpp import decode_detailed
decode_detailed(bytes.fromhex("018806765ff2960a0003e8"))
# {'data': {'gps_1': {'latitude': 42.3519, 'longitude': -87.9094, 'altitude': 10.0}}, 'warnings': []}
```

```typescript
import { decode } from './cayenne_lpp';
const data = decode(bytes); // Uint8Array in, Record<string, any> out
```

## Testing

```bash
python -m pytest tests/     # Python decoders + regression vectors (29 tests)
node --test                 # JS codecs + TypeScript decoders against the same vectors (20 tests)
npm test                    # both
```

The TypeScript check needs Node >= 22.18 (native type stripping); on older Node it is skipped and says so.

## Changes

- **1.1.0 (2026-09-18)** - Added pasteable JavaScript codecs for ChirpStack v3/v4 and The Things Stack. Corrected Cayenne LPP type IDs to the published tables (GPS was 188, now 136; power 128, distance 130, energy 131, direction 132; added gyrometer, generic, percentage, altitude, concentration, unix time, colour, switch). Fixed negative GPS coordinates in Python and negative int16 values (sub-zero temperatures) in TypeScript. Replaced example files whose expected values did not match their payloads; examples now drive the tests in all three languages. **Breaking** if you relied on the old non-standard type IDs.
- **1.0.0** - Initial Python + TypeScript decoders.

## References

- [ChirpStack Codec Documentation](https://www.chirpstack.io/docs/chirpstack/use/device-profiles.html#codec)
- [Cayenne LPP Specification](https://developers.mydevices.com/cayenne/docs/lora/#lora-cayenne-low-power-payload)
- [LoRaWAN Specification](https://lora-alliance.org/resource_hub/lorawan-specification-v1-0-3/)
