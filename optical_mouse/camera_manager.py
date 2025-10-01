"""
Camera Manager Module
Handles camera connection, initialization, and frame capture
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple, Union

logger = logging.getLogger(__name__)


class CameraManager:
    """Manages camera connection and frame capture operations"""
    
    def __init__(self, source: Union[int, str] = 0, width: int = 640, 
                 height: int = 480, fps: int = 30):
        """
        Initialize Camera Manager
        
        Args:
            source: Camera source (0 for webcam, URL for IP camera)
            width: Frame width in pixels
            height: Frame height in pixels
            fps: Target frames per second
        """
        self.source = source
        self.width = width
        self.height = height
        self.fps = fps
        self.capture = None
        self.is_connected = False
        
    def initialize_camera(self) -> bool:
        """
        Establish connection to camera and configure settings
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Initializing camera with source: {self.source}")
            self.capture = cv2.VideoCapture(self.source)
            
            if not self.capture.isOpened():
                logger.error("Failed to open camera")
                return False
            
            # Set camera properties
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Verify settings
            actual_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.capture.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Capture a single frame from camera
        
        Returns:
            Tuple of (success flag, frame)
        """
        if not self.is_connected or self.capture is None:
            logger.warning("Camera not connected")
            return False, None
        
        try:
            ret, frame = self.capture.read()
            
            if not ret:
                logger.warning("Failed to read frame")
                return False, None
            
            return True, frame
            
        except Exception as e:
            logger.error(f"Frame read error: {e}")
            return False, None
    
    def read_frame_with_retry(self, max_retries: int = 3) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read frame with retry mechanism for transient failures
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (success flag, frame)
        """
        for attempt in range(max_retries):
            ret, frame = self.read_frame()
            if ret:
                return True, frame
            logger.warning(f"Read attempt {attempt + 1} failed, retrying...")
        
        return False, None
    
    def get_frame_dimensions(self) -> Tuple[int, int]:
        """
        Get current frame dimensions
        
        Returns:
            Tuple of (width, height)
        """
        if self.capture is not None:
            width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return self.width, self.height
    
    def release_camera(self) -> None:
        """Release camera resources and close connection"""
        if self.capture is not None:
            self.capture.release()
            self.is_connected = False
            logger.info("Camera released")
    
    def __enter__(self):
        """Context manager entry"""
        self.initialize_camera()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release_camera()
