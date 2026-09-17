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
        # Channel 1, Type 136 (GPS) -- the myDevices spec vector, negative longitude
        payload = bytes.fromhex("018806765ff2960a0003e8")
        gps = decode(payload)['gps_1']
        self.assertAlmostEqual(gps['latitude'], 42.3519, places=4)
        self.assertAlmostEqual(gps['longitude'], -87.9094, places=4)
        self.assertAlmostEqual(gps['altitude'], 10.0, places=2)

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