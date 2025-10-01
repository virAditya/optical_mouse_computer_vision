"""
Utilities Module
Helper functions for configuration, logging, and performance monitoring
"""

import logging
import yaml
import time
import numpy as np
from typing import Dict, Any, Optional
from collections import deque
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    logger.info(f"Logging configured at {log_level} level")


def load_config(config_path: str) -> Dict[str, Any]:
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return get_default_config()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    return {
        'camera': {
            'source': 0,
            'width': 640,
            'height': 480,
            'fps': 30
        },
        'tracking': {
            'method': 'optical_flow',
            'sensitivity': 1.0,
            'smoothing_factor': 0.3
        },
        'optical_flow': {
            'max_corners': 100,
            'quality_level': 0.3,
            'min_distance': 7,
            'block_size': 7
        },
        'color_tracking': {
            'lower_hsv': [35, 50, 50],
            'upper_hsv': [85, 255, 255]
        },
        'display': {
            'show_camera': True,
            'show_desktop': True,
            'window_width': 800,
            'window_height': 600,
            'fps_display': True
        },
        'cursor': {
            'movement_mode': 'relative',
            'boundary_margin': 50
        }
    }


class PerformanceMonitor:
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times = deque(maxlen=window_size)
        self.processing_times = deque(maxlen=window_size)
        self.start_time = None
    
    def start_frame(self) -> None:
        self.start_time = time.time()
    
    def end_frame(self) -> float:
        if self.start_time is None:
            return 0.0
        
        end_time = time.time()
        processing_time = (end_time - self.start_time) * 1000
        self.processing_times.append(processing_time)
        self.frame_times.append(end_time)
        
        return processing_time
    
    def get_fps(self) -> float:
        if len(self.frame_times) < 2:
            return 0.0
        
        time_span = self.frame_times[-1] - self.frame_times[0]
        if time_span > 0:
            return len(self.frame_times) / time_span
        return 0.0
    
    def get_avg_latency(self) -> float:
        if len(self.processing_times) == 0:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)


def print_system_info() -> None:
    import cv2
    import platform
    
    print("=" * 60)
    print("OPTICAL MOUSE COMPUTER VISION - SYSTEM INFO")
    print("=" * 60)
    print(f"Python Version: {platform.python_version()}")
    print(f"OpenCV Version: {cv2.__version__}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print("=" * 60)
