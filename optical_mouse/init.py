"""
Optical Mouse Computer Vision Package
A computer vision implementation mimicking optical mouse functionality
"""

__version__ = "1.0.0"
__author__ = "Optical Mouse CV Team"
__license__ = "MIT"

from .camera_manager import CameraManager
from .motion_tracker import MotionTracker
from .coordinate_transformer import CoordinateTransformer
from .cursor_controller import CursorController
from .display_manager import DisplayManager
from .main import OpticalMouseSystem, main

__all__ = [
    'CameraManager',
    'MotionTracker',
    'CoordinateTransformer',
    'CursorController',
    'DisplayManager',
    'OpticalMouseSystem',
    'main'
]
