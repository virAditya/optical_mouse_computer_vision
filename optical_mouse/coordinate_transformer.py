"""
Coordinate Transformer Module
Handles coordinate mapping and movement smoothing
"""

import numpy as np
import logging
from typing import Tuple, Dict, Optional
from collections import deque
import json

logger = logging.getLogger(__name__)


class CoordinateTransformer:
    """Transforms coordinates between camera and screen space"""
    
    def __init__(self, camera_width: int, camera_height: int,
                 screen_width: int, screen_height: int,
                 smoothing_factor: float = 0.3):
        """
        Initialize Coordinate Transformer
        
        Args:
            camera_width: Camera frame width
            camera_height: Camera frame height
            screen_width: Screen resolution width
            screen_height: Screen resolution height
            smoothing_factor: Smoothing coefficient (0-1)
        """
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.smoothing_factor = smoothing_factor
        
        # Movement history for smoothing
        self.movement_buffer = deque(maxlen=10)
        
        # Calibration data
        self.calibration_data = self._initialize_calibration()
        
        logger.info(f"Coordinate Transformer initialized: "
                   f"{camera_width}x{camera_height} -> {screen_width}x{screen_height}")
    
    def _initialize_calibration(self) -> Dict:
        """
        Initialize calibration parameters
        
        Returns:
            Dictionary containing calibration data
        """
        # Calculate scaling factors
        scale_x = self.screen_width / self.camera_width
        scale_y = self.screen_height / self.camera_height
        
        calibration = {
            'scale_x': scale_x,
            'scale_y': scale_y,
            'offset_x': 0,
            'offset_y': 0,
            'rotation': 0,
            'sensitivity': 1.0
        }
        
        return calibration
    
    def transform_coordinates(self, camera_x: float, camera_y: float) -> Tuple[int, int]:
        """
        Transform camera coordinates to screen coordinates
        
        Args:
            camera_x: X position in camera frame
            camera_y: Y position in camera frame
            
        Returns:
            Tuple of (screen_x, screen_y)
        """
        # Apply scaling
        screen_x = camera_x * self.calibration_data['scale_x']
        screen_y = camera_y * self.calibration_data['scale_y']
        
        # Apply offset
        screen_x += self.calibration_data['offset_x']
        screen_y += self.calibration_data['offset_y']
        
        # Apply sensitivity
        screen_x *= self.calibration_data['sensitivity']
        screen_y *= self.calibration_data['sensitivity']
        
        # Clamp to screen bounds
        screen_x = max(0, min(self.screen_width - 1, screen_x))
        screen_y = max(0, min(self.screen_height - 1, screen_y))
        
        return int(screen_x), int(screen_y)
    
    def apply_movement_smoothing(self, delta_x: float, delta_y: float) -> Tuple[float, float]:
        """
        Apply smoothing to movement deltas
        
        Args:
            delta_x: Raw X displacement
            delta_y: Raw Y displacement
            
        Returns:
            Tuple of (smoothed_x, smoothed_y)
        """
        # Add to buffer
        self.movement_buffer.append((delta_x, delta_y))
        
        if len(self.movement_buffer) == 0:
            return 0.0, 0.0
        
        # Exponential moving average
        smoothed_x = delta_x * self.smoothing_factor
        smoothed_y = delta_y * self.smoothing_factor
        
        if len(self.movement_buffer) > 1:
            prev_deltas = list(self.movement_buffer)[:-1]
            for prev_dx, prev_dy in prev_deltas:
                weight = (1 - self.smoothing_factor) / len(prev_deltas)
                smoothed_x += prev_dx * weight
                smoothed_y += prev_dy * weight
        
        return smoothed_x, smoothed_y
    
    def set_sensitivity(self, sensitivity: float) -> None:
        """
        Set movement sensitivity
        
        Args:
            sensitivity: Sensitivity multiplier (default 1.0)
        """
        self.calibration_data['sensitivity'] = max(0.1, min(5.0, sensitivity))
        logger.info(f"Sensitivity set to {self.calibration_data['sensitivity']}")
    
    def set_smoothing_factor(self, factor: float) -> None:
        """
        Set smoothing factor
        
        Args:
            factor: Smoothing coefficient (0-1)
        """
        self.smoothing_factor = max(0.0, min(1.0, factor))
        logger.info(f"Smoothing factor set to {self.smoothing_factor}")
    
    def reset_buffer(self) -> None:
        """Clear movement buffer"""
        self.movement_buffer.clear()
