"""
Unit tests for Coordinate Transformer module
"""

import unittest
import numpy as np
from collections import deque

from optical_mouse.coordinate_transformer import CoordinateTransformer


class TestCoordinateTransformer(unittest.TestCase):
    """Test cases for CoordinateTransformer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.transformer = CoordinateTransformer(
            camera_width=640,
            camera_height=480,
            screen_width=1920,
            screen_height=1080,
            smoothing_factor=0.3
        )
    
    def test_initialization(self):
        """Test transformer initialization"""
        self.assertEqual(self.transformer.camera_width, 640)
        self.assertEqual(self.transformer.camera_height, 480)
        self.assertEqual(self.transformer.screen_width, 1920)
        self.assertEqual(self.transformer.screen_height, 1080)
        self.assertEqual(self.transformer.smoothing_factor, 0.3)
        self.assertIsNotNone(self.transformer.calibration_data)
    
    def test_calibration_initialization(self):
        """Test calibration data initialization"""
        calibration = self.transformer.calibration_data
        
        self.assertIn('scale_x', calibration)
        self.assertIn('scale_y', calibration)
        self.assertIn('sensitivity', calibration)
        self.assertEqual(calibration['sensitivity'], 1.0)
    
    def test_transform_coordinates(self):
        """Test coordinate transformation"""
        camera_x, camera_y = 100, 100
        
        screen_x, screen_y = self.transformer.transform_coordinates(camera_x, camera_y)
        
        self.assertIsInstance(screen_x, int)
        self.assertIsInstance(screen_y, int)
        self.assertGreaterEqual(screen_x, 0)
        self.assertGreaterEqual(screen_y, 0)
        self.assertLess(screen_x, 1920)
        self.assertLess(screen_y, 1080)
    
    def test_transform_coordinates_boundary_negative(self):
        """Test coordinate transformation with negative values"""
        screen_x, screen_y = self.transformer.transform_coordinates(-100, -100)
        
        self.assertEqual(screen_x, 0)
        self.assertEqual(screen_y, 0)
    
    def test_transform_coordinates_boundary_overflow(self):
        """Test coordinate transformation beyond screen"""
        screen_x, screen_y = self.transformer.transform_coordinates(10000, 10000)
        
        self.assertEqual(screen_x, 1919)
        self.assertEqual(screen_y, 1079)
    
    def test_apply_movement_smoothing(self):
        """Test movement smoothing"""
        delta_x, delta_y = 10.0, 5.0
        
        smooth_x, smooth_y = self.transformer.apply_movement_smoothing(delta_x, delta_y)
        
        self.assertIsInstance(smooth_x, float)
        self.assertIsInstance(smooth_y, float)
        # Smoothed values should be less than or equal to original
        self.assertLessEqual(abs(smooth_x), abs(delta_x) + 1)
        self.assertLessEqual(abs(smooth_y), abs(delta_y) + 1)
    
    def test_apply_movement_smoothing_multiple_calls(self):
        """Test movement smoothing with multiple calls"""
        values = [(10.0, 5.0), (12.0, 6.0), (8.0, 4.0)]
        
        for dx, dy in values:
            smooth_x, smooth_y = self.transformer.apply_movement_smoothing(dx, dy)
            self.assertIsInstance(smooth_x, float)
            self.assertIsInstance(smooth_y, float)
    
    def test_set_sensitivity(self):
        """Test sensitivity setting"""
        self.transformer.set_sensitivity(2.0)
        self.assertEqual(self.transformer.calibration_data['sensitivity'], 2.0)
        
        # Test clamping to maximum
        self.transformer.set_sensitivity(20.0)
        self.assertEqual(self.transformer.calibration_data['sensitivity'], 5.0)
        
        # Test clamping to minimum
        self.transformer.set_sensitivity(0.01)
        self.assertEqual(self.transformer.calibration_data['sensitivity'], 0.1)
    
    def test_set_smoothing_factor(self):
        """Test smoothing factor setting"""
        self.transformer.set_smoothing_factor(0.5)
        self.assertEqual(self.transformer.smoothing_factor, 0.5)
        
        # Test clamping to maximum
        self.transformer.set_smoothing_factor(1.5)
        self.assertEqual(self.transformer.smoothing_factor, 1.0)
        
        # Test clamping to minimum
        self.transformer.set_smoothing_factor(-0.5)
        self.assertEqual(self.transformer.smoothing_factor, 0.0)
    
    def test_reset_buffer(self):
        """Test buffer reset"""
        self.transformer.movement_buffer.append((1, 1))
        self.transformer.movement_buffer.append((2, 2))
        
        self.assertEqual(len(self.transformer.movement_buffer), 2)
        
        self.transformer.reset_buffer()
        
        self.assertEqual(len(self.transformer.movement_buffer), 0)
    
    def test_movement_buffer_max_length(self):
        """Test movement buffer respects max length"""
        for i in range(20):
            self.transformer.movement_buffer.append((i, i))
        
        # Buffer should be capped at maxlen=10
        self.assertEqual(len(self.transformer.movement_buffer), 10)


if __name__ == '__main__':
    unittest.main()
