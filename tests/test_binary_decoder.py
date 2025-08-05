"""Unit tests for binary decoder."""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'decoders', 'python'))

from binary_decoder import decode_temperature_humidity, decode_gps_simple, decode_sensor_data, Decode

class TestBinaryDecoder(unittest.TestCase):
    
    def test_temperature_humidity(self):
        # 25.67°C, 65% humidity
        payload = bytes([0x0A, 0x07, 0x41])
        result = decode_temperature_humidity(payload)
        self.assertAlmostEqual(result['temperature'], 25.67, places=2)
        self.assertEqual(result['humidity'], 65)
    
    def test_gps_simple(self):
        # Simple GPS test with known values
        payload = bytes([0x03, 0x20, 0x08, 0x20, 0x00, 0xCC, 0x5E, 0x60])
        result = decode_gps_simple(payload)
        self.assertAlmostEqual(result['latitude'], 52.43088, places=4)
        self.assertAlmostEqual(result['longitude'], 13.393504, places=4)
    
    def test_sensor_data(self):
        # Battery: 85%, Temp: 23.45°C, Humidity: 60%, Light: 1200 lux
        payload = bytes([0x55, 0x09, 0x29, 0x3C, 0x04, 0xB0])
        result = decode_sensor_data(payload)
        self.assertEqual(result['battery'], 85)
        self.assertAlmostEqual(result['temperature'], 23.45, places=2)
        self.assertEqual(result['humidity'], 60)
        self.assertEqual(result['light'], 1200)
    
    def test_chirpstack_interface(self):
        payload = bytes([0x0A, 0x07, 0x41])
        result = Decode(1, payload, {})
        self.assertIn('temperature', result)
        self.assertIn('humidity', result)
    
    def test_invalid_port(self):
        payload = bytes([0x01, 0x02])
        result = Decode(99, payload, {})
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()