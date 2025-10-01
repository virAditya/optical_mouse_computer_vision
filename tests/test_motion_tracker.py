"""
Unit tests for Motion Tracker module
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch

from optical_mouse.motion_tracker import MotionTracker


class TestMotionTracker(unittest.TestCase):
    """Test cases for MotionTracker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker_optical = MotionTracker(method="optical_flow")
        self.tracker_color = MotionTracker(method="color_tracking")
    
    def test_initialization_optical_flow(self):
        """Test optical flow tracker initialization"""
        self.assertEqual(self.tracker_optical.method, "optical_flow")
        self.assertIsNone(self.tracker_optical.prev_gray)
        self.assertIsNone(self.tracker_optical.prev_points)
    
    def test_initialization_color_tracking(self):
        """Test color tracking initialization"""
        self.assertEqual(self.tracker_color.method, "color_tracking")
        self.assertIsNotNone(self.tracker_color.lower_hsv)
        self.assertIsNotNone(self.tracker_color.upper_hsv)
    
    @patch('cv2.goodFeaturesToTrack')
    def test_initialize_optical_flow(self, mock_features):
        """Test optical flow initialization"""
        test_frame = np.zeros((480, 640), dtype=np.uint8)
        mock_points = np.array([[[100, 100]], [[200, 200]]], dtype=np.float32)
        mock_features.return_value = mock_points
        
        points = self.tracker_optical.initialize_optical_flow(test_frame)
        
        self.assertIsNotNone(points)
        self.assertEqual(len(points), 2)
        mock_features.assert_called_once()
    
    @patch('cv2.goodFeaturesToTrack')
    def test_initialize_optical_flow_no_features(self, mock_features):
        """Test optical flow initialization with no features found"""
        test_frame = np.zeros((480, 640), dtype=np.uint8)
        mock_features.return_value = None
        
        points = self.tracker_optical.initialize_optical_flow(test_frame)
        
        self.assertEqual(len(points), 0)
    
    def test_calculate_movement_delta_no_points(self):
        """Test movement calculation with no points"""
        prev_points = np.array([])
        curr_points = np.array([])
        status = np.array([])
        
        delta_x, delta_y = self.tracker_optical.calculate_movement_delta(
            prev_points, curr_points, status
        )
        
        self.assertEqual(delta_x, 0.0)
        self.assertEqual(delta_y, 0.0)
    
    def test_calculate_movement_delta_with_points(self):
        """Test movement calculation with valid points"""
        prev_points = np.array([[[100, 100]], [[200, 200]]], dtype=np.float32)
        curr_points = np.array([[[105, 103]], [[205, 203]]], dtype=np.float32)
        status = np.array([1, 1])
        
        delta_x, delta_y = self.tracker_optical.calculate_movement_delta(
            prev_points, curr_points, status
        )
        
        self.assertAlmostEqual(delta_x, 5.0, places=1)
        self.assertAlmostEqual(delta_y, 3.0, places=1)
    
    def test_calculate_movement_delta_partial_status(self):
        """Test movement calculation with partial tracking success"""
        prev_points = np.array([[[100, 100]], [[200, 200]]], dtype=np.float32)
        curr_points = np.array([[[105, 103]], [[205, 203]]], dtype=np.float32)
        status = np.array([1, 0])  # Only first point tracked
        
        delta_x, delta_y = self.tracker_optical.calculate_movement_delta(
            prev_points, curr_points, status
        )
        
        self.assertAlmostEqual(delta_x, 5.0, places=1)
        self.assertAlmostEqual(delta_y, 3.0, places=1)
    
    @patch('cv2.findContours')
    @patch('cv2.inRange')
    @patch('cv2.cvtColor')
    def test_detect_object_by_color_no_object(self, mock_cvt, mock_inrange, mock_contours):
        """Test color detection with no object"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cvt.return_value = test_frame
        mock_inrange.return_value = np.zeros((480, 640), dtype=np.uint8)
        mock_contours.return_value = ([], None)
        
        centroid = self.tracker_color.detect_object_by_color(test_frame)
        
        self.assertIsNone(centroid)
    
    def test_validate_tracking_quality_good(self):
        """Test tracking quality validation - good quality"""
        status = np.array([1, 1, 1, 1, 1])
        error = np.array([10, 15, 12, 11, 13])
        
        result = self.tracker_optical.validate_tracking_quality(status, error, threshold=50)
        
        self.assertTrue(result)
    
    def test_validate_tracking_quality_poor(self):
        """Test tracking quality validation - poor quality"""
        status = np.array([1, 0, 0, 0, 0])
        error = np.array([10, 0, 0, 0, 0])
        
        result = self.tracker_optical.validate_tracking_quality(status, error, threshold=50)
        
        self.assertFalse(result)
    
    def test_validate_tracking_quality_high_error(self):
        """Test tracking quality validation - high error"""
        status = np.array([1, 1, 1, 1, 1])
        error = np.array([60, 65, 70, 55, 75])
        
        result = self.tracker_optical.validate_tracking_quality(status, error, threshold=50)
        
        self.assertFalse(result)
    
    def test_validate_tracking_quality_empty(self):
        """Test tracking quality validation - empty arrays"""
        status = np.array([])
        error = np.array([])
        
        result = self.tracker_optical.validate_tracking_quality(status, error)
        
        self.assertFalse(result)
    
    def test_get_tracked_points(self):
        """Test getting tracked points"""
        self.tracker_optical.prev_points = np.array([[[100, 100]]])
        
        points = self.tracker_optical.get_tracked_points()
        
        self.assertIsNotNone(points)
        self.assertEqual(len(points), 1)


if __name__ == '__main__':
    unittest.main()
