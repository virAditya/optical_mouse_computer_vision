"""
Unit tests for Utilities module
"""

import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
import time

from optical_mouse.utilities import (
    load_config, get_default_config,
    PerformanceMonitor, print_system_info
)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_get_default_config(self):
        """Test getting default configuration"""
        config = get_default_config()
        
        self.assertIn('camera', config)
        self.assertIn('tracking', config)
        self.assertIn('display', config)
        self.assertIn('cursor', config)
        self.assertIn('optical_flow', config)
        self.assertIn('color_tracking', config)
    
    def test_get_default_config_structure(self):
        """Test default config has correct structure"""
        config = get_default_config()
        
        self.assertEqual(config['camera']['source'], 0)
        self.assertEqual(config['camera']['width'], 640)
        self.assertEqual(config['tracking']['method'], 'optical_flow')
        self.assertEqual(config['cursor']['movement_mode'], 'relative')
    
    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist"""
        config = load_config('nonexistent_file.yaml')
        
        # Should return default config
        self.assertIn('camera', config)
        self.assertIn('tracking', config)
    
    @patch('builtins.print')
    def test_print_system_info(self, mock_print):
        """Test system info printing"""
        print_system_info()
        
        # Should have called print multiple times
        self.assertGreater(mock_print.call_count, 0)


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor(window_size=10)
    
    def test_initialization(self):
        """Test monitor initialization"""
        self.assertEqual(self.monitor.window_size, 10)
        self.assertEqual(len(self.monitor.frame_times), 0)
        self.assertEqual(len(self.monitor.processing_times), 0)
        self.assertIsNone(self.monitor.start_time)
    
    def test_start_frame(self):
        """Test frame start"""
        self.monitor.start_frame()
        
        self.assertIsNotNone(self.monitor.start_time)
        self.assertIsInstance(self.monitor.start_time, float)
    
    def test_end_frame(self):
        """Test frame end"""
        self.monitor.start_frame()
        time.sleep(0.01)
        latency = self.monitor.end_frame()
        
        self.assertGreater(latency, 0)
        self.assertLess(latency, 100)  # Should be less than 100ms
        self.assertEqual(len(self.monitor.processing_times), 1)
    
    def test_end_frame_without_start(self):
        """Test end frame without start"""
        latency = self.monitor.end_frame()
        
        self.assertEqual(latency, 0.0)
    
    def test_get_fps(self):
        """Test FPS calculation"""
        for _ in range(5):
            self.monitor.start_frame()
            time.sleep(0.01)
            self.monitor.end_frame()
        
        fps = self.monitor.get_fps()
        
        self.assertGreater(fps, 0)
        self.assertLess(fps, 1000)  # Reasonable upper bound
    
    def test_get_fps_insufficient_data(self):
        """Test FPS with insufficient data"""
        fps = self.monitor.get_fps()
        
        self.assertEqual(fps, 0.0)
    
    def test_get_avg_latency(self):
        """Test average latency calculation"""
        for _ in range(3):
            self.monitor.start_frame()
            time.sleep(0.01)
            self.monitor.end_frame()
        
        avg_latency = self.monitor.get_avg_latency()
        
        self.assertGreater(avg_latency, 0)
    
    def test_get_avg_latency_no_data(self):
        """Test average latency with no data"""
        avg_latency = self.monitor.get_avg_latency()
        
        self.assertEqual(avg_latency, 0.0)
    
    def test_reset(self):
        """Test monitor reset"""
        self.monitor.start_frame()
        self.monitor.end_frame()
        
        self.assertGreater(len(self.monitor.frame_times), 0)
        
        self.monitor.reset()
        
        self.assertEqual(len(self.monitor.frame_times), 0)
        self.assertEqual(len(self.monitor.processing_times), 0)
        self.assertIsNone(self.monitor.start_time)
    
    def test_window_size_limit(self):
        """Test that deques respect window size"""
        for i in range(20):
            self.monitor.start_frame()
            time.sleep(0.001)
            self.monitor.end_frame()
        
        # Should not exceed window_size
        self.assertLessEqual(len(self.monitor.frame_times), 10)
        self.assertLessEqual(len(self.monitor.processing_times), 10)


if __name__ == '__main__':
    unittest.main()
