"""Unit tests for Cayenne LPP decoder."""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'decoders', 'python'))

from cayenne_lpp import decode, Decode

class TestCayenneLPP(unittest.TestCase):
    
    def test_temperature_sensor(self):
        # Channel 1, Type 103 (temperature), Value 27.2°C
        payload = bytes([0x01, 0x67, 0x01, 0x10])
        result = decode(payload)
        self.assertAlmostEqual(result['temperature_1'], 27.2, places=1)
    
    def test_humidity_sensor(self):
        # Channel 2, Type 104 (humidity), Value 68%
        payload = bytes([0x02, 0x68, 0x88])
        result = decode(payload)
        self.assertEqual(result['humidity_2'], 68.0)
    
    def test_gps_sensor(self):
        # Channel 3, Type 188 (GPS)
        payload = bytes([0x03, 0xBC, 0x42, 0x6F, 0x00, 0xFF, 0x33, 0xD0, 0x00, 0x00, 0x96])
        result = decode(payload)
        self.assertIn('gps_3', result)
        self.assertIn('latitude', result['gps_3'])
        self.assertIn('longitude', result['gps_3'])
    
    def test_multiple_sensors(self):
        # Temperature + Humidity
        payload = bytes([0x01, 0x67, 0x01, 0x10, 0x02, 0x68, 0x88])
        result = decode(payload)
        self.assertIn('temperature_1', result)
        self.assertIn('humidity_2', result)
    
    def test_chirpstack_interface(self):
        payload = bytes([0x01, 0x67, 0x01, 0x10])
        result = Decode(1, payload, {})
        self.assertIn('temperature_1', result)

if __name__ == '__main__':
    unittest.main()