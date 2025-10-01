"""
Unit tests for Display Manager module
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from optical_mouse.display_manager import DisplayManager


class TestDisplayManager(unittest.TestCase):
    """Test cases for DisplayManager class"""
    
    @patch('mss.mss')
    def setUp(self, mock_mss):
        """Set up test fixtures"""
        self.display_manager = DisplayManager(
            window_width=800,
            window_height=600,
            show_camera=True,
            show_desktop=True,
            fps_display=True
        )
    
    def test_initialization(self):
        """Test display manager initialization"""
        self.assertEqual(self.display_manager.window_width, 800)
        self.assertEqual(self.display_manager.window_height, 600)
        self.assertTrue(self.display_manager.show_camera)
        self.assertTrue(self.display_manager.show_desktop)
        self.assertTrue(self.display_manager.fps_display)
    
    @patch('cv2.namedWindow')
    @patch('cv2.resizeWindow')
    @patch('cv2.moveWindow')
    def test_create_display_windows(self, mock_move, mock_resize, mock_named):
        """Test window creation"""
        self.display_manager.create_display_windows()
        
        self.assertEqual(mock_named.call_count, 2)
        self.assertEqual(mock_resize.call_count, 2)
        self.assertEqual(mock_move.call_count, 2)
    
    def test_draw_tracking_overlays_with_points(self):
        """Test drawing tracking overlays with points"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        points = np.array([[[100, 100]], [[200, 200]]], dtype=np.float32)
        status = np.array([1, 1])
        
        result = self.display_manager.draw_tracking_overlays(
            frame, points=points, status=status
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)
        # Result should be different from original (has drawings)
        self.assertFalse(np.array_equal(result, frame))
    
    def test_draw_tracking_overlays_with_centroid(self):
        """Test drawing centroid overlay"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        centroid = (320, 240)
        
        result = self.display_manager.draw_tracking_overlays(
            frame, centroid=centroid
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)
    
    def test_draw_tracking_overlays_with_trails(self):
        """Test drawing motion trails"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        trails = [(100, 100), (110, 105), (120, 110)]
        
        result = self.display_manager.draw_tracking_overlays(
            frame, trails=trails
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)
    
    def test_draw_cursor_highlight(self):
        """Test cursor highlighting"""
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        cursor_x, cursor_y = 400, 300
        
        result = self.display_manager.draw_cursor_highlight(
            frame, cursor_x, cursor_y
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)
    
    def test_draw_cursor_highlight_out_of_bounds(self):
        """Test cursor highlighting with out of bounds coordinates"""
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        cursor_x, cursor_y = 2000, 2000
        
        result = self.display_manager.draw_cursor_highlight(
            frame, cursor_x, cursor_y
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)
    
    def test_draw_performance_metrics(self):
        """Test performance metrics drawing"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = self.display_manager.draw_performance_metrics(
            frame, fps=30.0, tracking_points=50, latency=15.5
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)
    
    def test_draw_performance_metrics_disabled(self):
        """Test performance metrics when disabled"""
        self.display_manager.fps_display = False
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = self.display_manager.draw_performance_metrics(
            frame, fps=30.0, tracking_points=50, latency=15.5
        )
        
        # Should return original frame unchanged
        self.assertTrue(np.array_equal(result, frame))
    
    def test_calculate_fps(self):
        """Test FPS calculation"""
        import time
        
        for i in range(10):
            fps = self.display_manager.calculate_fps(time.time())
            time.sleep(0.01)
        
        self.assertGreater(fps, 0)
        self.assertLess(fps, 200)  # Reasonable upper bound
    
    @patch('cv2.waitKey')
    def test_check_exit_key_escape(self, mock_waitkey):
        """Test exit key checking - ESC"""
        mock_waitkey.return_value = 27
        
        result = self.display_manager.check_exit_key()
        
        self.assertTrue(result)
    
    @patch('cv2.waitKey')
    def test_check_exit_key_q(self, mock_waitkey):
        """Test exit key checking - Q"""
        mock_waitkey.return_value = ord('q')
        
        result = self.display_manager.check_exit_key()
        
        self.assertTrue(result)
    
    @patch('cv2.waitKey')
    def test_check_exit_key_other(self, mock_waitkey):
        """Test exit key checking - other key"""
        mock_waitkey.return_value = ord('a')
        
        result = self.display_manager.check_exit_key()
        
        self.assertFalse(result)
    
    @patch('cv2.imshow')
    def test_update_display_windows(self, mock_imshow):
        """Test display window updates"""
        camera_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        desktop_frame = np.zeros((600, 800, 3), dtype=np.uint8)
        
        self.display_manager.update_display_windows(camera_frame, desktop_frame)
        
        self.assertEqual(mock_imshow.call_count, 2)
    
    @patch('cv2.destroyAllWindows')
    def test_destroy_windows(self, mock_destroy):
        """Test window destruction"""
        self.display_manager.destroy_windows()
        
        mock_destroy.assert_called_once()


if __name__ == '__main__':
    unittest.main()
