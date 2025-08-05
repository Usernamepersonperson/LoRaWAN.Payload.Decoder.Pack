# LoRaWAN Payload Decoder Pack

Drop-in decoders for ChirpStack with Python and TypeScript implementations.

## Features

- **Cayenne LPP**: Full support for Cayenne Low Power Payload format
- **Binary Decoders**: Simple binary frame decoders for common sensor data
- **ChirpStack Compatible**: Direct integration with ChirpStack codec functions
- **Unit Tests**: Comprehensive test coverage
- **Examples**: JSON examples for testing and validation

## Structure

```
/decoders/
  /python/
    cayenne_lpp.py      # Cayenne LPP decoder
    binary_decoder.py   # Simple binary decoders
  /ts/
    cayenne_lpp.ts      # TypeScript Cayenne LPP
    binary_decoder.ts   # TypeScript binary decoders
/tests/
  test_cayenne_lpp.py   # Python tests
  test_binary_decoder.py # Binary decoder tests
/examples/
  *.json               # Test payloads and expected outputs
```

## Usage

### ChirpStack Integration

Copy the decoder files to your ChirpStack application and use the `Decode` function:

```python
# Python
from cayenne_lpp import Decode
result = Decode(fPort, bytes_payload, variables)
```

```typescript
// TypeScript
import { Decode } from './cayenne_lpp';
const result = Decode(fPort, bytes, variables);
```

### Binary Decoder Ports

- **Port 1**: Temperature (2 bytes) + Humidity (1 byte)
- **Port 2**: GPS coordinates (lat: 4 bytes, lon: 4 bytes)
- **Port 3**: Multi-sensor (battery + temp + humidity + light)

## Testing

```bash
# Python tests
python -m pytest tests/

# Individual test files
python tests/test_cayenne_lpp.py
python tests/test_binary_decoder.py
```

## References

- [ChirpStack Codec Documentation](https://www.chirpstack.io/docs/chirpstack/use/device-profiles.html#codec)
- [Cayenne LPP Specification](https://developers.mydevices.com/cayenne/docs/lora/#lora-cayenne-low-power-payload)
- [LoRaWAN Specification](https://lora-alliance.org/resource_hub/lorawan-specification-v1-0-3/)