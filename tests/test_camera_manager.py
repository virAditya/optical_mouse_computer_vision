"""
Unit tests for Camera Manager module
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import cv2

from optical_mouse.camera_manager import CameraManager


class TestCameraManager(unittest.TestCase):
    """Test cases for CameraManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.camera_manager = CameraManager(source=0, width=640, height=480, fps=30)
    
    def tearDown(self):
        """Clean up after tests"""
        if self.camera_manager.capture is not None:
            self.camera_manager.release_camera()
    
    @patch('cv2.VideoCapture')
    def test_initialize_camera_success(self, mock_video_capture):
        """Test successful camera initialization"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = [640, 480, 30]
        mock_video_capture.return_value = mock_capture
        
        result = self.camera_manager.initialize_camera()
        
        self.assertTrue(result)
        self.assertTrue(self.camera_manager.is_connected)
        mock_video_capture.assert_called_once_with(0)
    
    @patch('cv2.VideoCapture')
    def test_initialize_camera_failure(self, mock_video_capture):
        """Test failed camera initialization"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = False
        mock_video_capture.return_value = mock_capture
        
        result = self.camera_manager.initialize_camera()
        
        self.assertFalse(result)
        self.assertFalse(self.camera_manager.is_connected)
    
    def test_read_frame_not_connected(self):
        """Test reading frame when camera not connected"""
        ret, frame = self.camera_manager.read_frame()
        
        self.assertFalse(ret)
        self.assertIsNone(frame)
    
    @patch('cv2.VideoCapture')
    def test_read_frame_success(self, mock_video_capture):
        """Test successful frame reading"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = [640, 480, 30]
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_capture.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_capture
        
        self.camera_manager.initialize_camera()
        ret, frame = self.camera_manager.read_frame()
        
        self.assertTrue(ret)
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (480, 640, 3))
    
    @patch('cv2.VideoCapture')
    def test_read_frame_failure(self, mock_video_capture):
        """Test failed frame reading"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = [640, 480, 30]
        mock_capture.read.return_value = (False, None)
        mock_video_capture.return_value = mock_capture
        
        self.camera_manager.initialize_camera()
        ret, frame = self.camera_manager.read_frame()
        
        self.assertFalse(ret)
        self.assertIsNone(frame)
    
    def test_get_frame_dimensions(self):
        """Test getting frame dimensions"""
        width, height = self.camera_manager.get_frame_dimensions()
        
        self.assertEqual(width, 640)
        self.assertEqual(height, 480)
    
    @patch('cv2.VideoCapture')
    def test_release_camera(self, mock_video_capture):
        """Test camera release"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = [640, 480, 30]
        mock_video_capture.return_value = mock_capture
        
        self.camera_manager.initialize_camera()
        self.assertTrue(self.camera_manager.is_connected)
        
        self.camera_manager.release_camera()
        
        self.assertFalse(self.camera_manager.is_connected)
        mock_capture.release.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_context_manager(self, mock_video_capture):
        """Test context manager functionality"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = [640, 480, 30]
        mock_video_capture.return_value = mock_capture
        
        with CameraManager(source=0) as cam:
            self.assertTrue(cam.is_connected)
        
        mock_capture.release.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_read_frame_with_retry_success(self, mock_video_capture):
        """Test frame reading with retry - success on second attempt"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = [640, 480, 30]
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_capture.read.side_effect = [(False, None), (True, test_frame)]
        mock_video_capture.return_value = mock_capture
        
        self.camera_manager.initialize_camera()
        ret, frame = self.camera_manager.read_frame_with_retry(max_retries=3)
        
        self.assertTrue(ret)
        self.assertIsNotNone(frame)
    
    @patch('cv2.VideoCapture')
    def test_read_frame_with_retry_failure(self, mock_video_capture):
        """Test frame reading with retry - all attempts fail"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = [640, 480, 30]
        mock_capture.read.return_value = (False, None)
        mock_video_capture.return_value = mock_capture
        
        self.camera_manager.initialize_camera()
        ret, frame = self.camera_manager.read_frame_with_retry(max_retries=3)
        
        self.assertFalse(ret)
        self.assertIsNone(frame)


if __name__ == '__main__':
    unittest.main()
