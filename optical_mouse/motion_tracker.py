"""
Motion Tracker Module
Implements optical flow and color-based tracking algorithms
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List
from collections import deque

logger = logging.getLogger(__name__)


class MotionTracker:
    """Tracks motion using optical flow or color-based methods"""
    
    def __init__(self, method: str = "optical_flow", **kwargs):
        """
        Initialize Motion Tracker
        
        Args:
            method: Tracking method ("optical_flow" or "color_tracking")
            **kwargs: Additional parameters for tracking algorithms
        """
        self.method = method
        self.prev_gray = None
        self.prev_points = None
        self.motion_history = deque(maxlen=10)
        
        # Optical Flow Parameters
        self.feature_params = dict(
            maxCorners=kwargs.get('max_corners', 100),
            qualityLevel=kwargs.get('quality_level', 0.3),
            minDistance=kwargs.get('min_distance', 7),
            blockSize=kwargs.get('block_size', 7)
        )
        
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        
        # Color Tracking Parameters
        self.lower_hsv = np.array(kwargs.get('lower_hsv', [35, 50, 50]))
        self.upper_hsv = np.array(kwargs.get('upper_hsv', [85, 255, 255]))
        self.prev_centroid = None
        
        logger.info(f"Motion Tracker initialized with method: {method}")
    
    def initialize_optical_flow(self, frame: np.ndarray) -> np.ndarray:
        """
        Initialize optical flow tracking with first frame
        
        Args:
            frame: Initial grayscale frame
            
        Returns:
            Array of detected feature points
        """
        self.prev_gray = frame.copy()
        
        # Detect good features to track
        points = cv2.goodFeaturesToTrack(
            self.prev_gray, 
            mask=None, 
            **self.feature_params
        )
        
        if points is not None:
            self.prev_points = points
            logger.info(f"Initialized {len(points)} tracking points")
        else:
            self.prev_points = np.array([])
            logger.warning("No features detected for tracking")
        
        return self.prev_points
    
    def calculate_optical_flow(self, curr_gray: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate optical flow between frames
        
        Args:
            curr_gray: Current grayscale frame
            
        Returns:
            Tuple of (new_points, status, error)
        """
        if self.prev_gray is None or self.prev_points is None or len(self.prev_points) == 0:
            logger.warning("Optical flow not initialized")
            return np.array([]), np.array([]), np.array([])
        
        # Calculate optical flow
        new_points, status, error = cv2.calcOpticalFlowPyrLK(
            self.prev_gray,
            curr_gray,
            self.prev_points,
            None,
            **self.lk_params
        )
        
        return new_points, status, error
    
    def calculate_movement_delta(self, prev_points: np.ndarray, 
                                 curr_points: np.ndarray, 
                                 status: np.ndarray) -> Tuple[float, float]:
        """
        Calculate average movement from tracked points
        
        Args:
            prev_points: Previous point positions
            curr_points: Current point positions
            status: Tracking status for each point
            
        Returns:
            Tuple of (delta_x, delta_y)
        """
        if len(prev_points) == 0 or len(curr_points) == 0:
            return 0.0, 0.0
        
        # Filter good points
        good_new = curr_points[status == 1]
        good_old = prev_points[status == 1]
        
        if len(good_new) == 0:
            return 0.0, 0.0
        
        # Calculate displacement vectors
        displacements = good_new - good_old

        # Ensure displacements is 2D (N, 2)
        if len(displacements.shape) == 3:
            displacements = displacements.reshape(-1, 2)

        # Average displacement
        delta_x = float(np.mean(displacements[:, 0]))
        delta_y = float(np.mean(displacements[:, 1]))
        
        return delta_x, delta_y
    
    def detect_object_by_color(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Detect colored object and return centroid
        
        Args:
            frame: BGR color frame
            
        Returns:
            Tuple of (centroid_x, centroid_y) or None
        """
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        # Morphological operations to clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(largest_contour) < 100:  # Minimum area threshold
            return None
        
        # Calculate centroid
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy
        
        return None
    
    def track_motion(self, frame: np.ndarray) -> Tuple[float, float, np.ndarray]:
        """
        Main tracking function that routes to appropriate method
        
        Args:
            frame: Current BGR frame
            
        Returns:
            Tuple of (delta_x, delta_y, visualization_data)
        """
        if self.method == "optical_flow":
            return self._track_optical_flow(frame)
        elif self.method == "color_tracking":
            return self._track_color(frame)
        else:
            logger.error(f"Unknown tracking method: {self.method}")
            return 0.0, 0.0, frame
    
    def _track_optical_flow(self, frame: np.ndarray) -> Tuple[float, float, np.ndarray]:
        """Internal method for optical flow tracking"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Initialize on first frame
        if self.prev_gray is None:
            self.initialize_optical_flow(gray)
            return 0.0, 0.0, frame
        
        # Calculate optical flow
        new_points, status, error = self.calculate_optical_flow(gray)
        
        # Calculate movement
        delta_x, delta_y = 0.0, 0.0
        if len(new_points) > 0:
            delta_x, delta_y = self.calculate_movement_delta(
                self.prev_points, new_points, status
            )
        
        # Check tracking quality and reinitialize if needed
        if self.validate_tracking_quality(status, error):
            # Update for next iteration
            good_new = new_points[status == 1]
            self.prev_points = good_new.reshape(-1, 1, 2)
            self.prev_gray = gray.copy()
        else:
            logger.info("Tracking quality low, reinitializing...")
            self.initialize_optical_flow(gray)
        
        return delta_x, delta_y, new_points
    
    def _track_color(self, frame: np.ndarray) -> Tuple[float, float, Optional[Tuple[int, int]]]:
        """Internal method for color-based tracking"""
        centroid = self.detect_object_by_color(frame)
        
        delta_x, delta_y = 0.0, 0.0
        
        if centroid is not None and self.prev_centroid is not None:
            delta_x = float(centroid[0] - self.prev_centroid[0])
            delta_y = float(centroid[1] - self.prev_centroid[1])
        
        self.prev_centroid = centroid
        
        return delta_x, delta_y, centroid
    
    def validate_tracking_quality(self, status: np.ndarray, 
                                  error: np.ndarray, 
                                  threshold: float = 50.0) -> bool:
        """
        Assess quality of optical flow tracking
        
        Args:
            status: Tracking status flags
            error: Tracking error values
            threshold: Maximum acceptable error
            
        Returns:
            True if tracking is reliable
        """
        if len(status) == 0:
            return False
        
        # Calculate percentage of successfully tracked points
        success_rate = np.sum(status) / len(status)
        
        # Check if enough points are tracked successfully
        if success_rate < 0.5:  # Less than 50% success
            return False
        
        # Check error magnitudes
        if len(error) > 0:
            avg_error = np.mean(error[status == 1])
            if avg_error > threshold:
                return False
        
        return True
    
    def reset_tracking(self, frame: np.ndarray) -> None:
        """
        Reset tracking features
        
        Args:
            frame: Frame to detect new features from
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.initialize_optical_flow(gray)
        self.prev_centroid = None
        logger.info("Tracking reset")
    
    def get_tracked_points(self) -> Optional[np.ndarray]:
        """Get currently tracked points"""
        return self.prev_points
