"""
Default Configuration Constants
Provides fallback values for all system parameters
"""

# Camera Configuration
DEFAULT_CAMERA_SOURCE = 0  # 0 for default webcam
DEFAULT_CAMERA_WIDTH = 640
DEFAULT_CAMERA_HEIGHT = 480
DEFAULT_CAMERA_FPS = 30

# Tracking Configuration
DEFAULT_TRACKING_METHOD = "optical_flow"  # Options: "optical_flow" or "color_tracking"
DEFAULT_SENSITIVITY = 1.0
DEFAULT_SMOOTHING_FACTOR = 0.3

# Optical Flow Parameters
DEFAULT_MAX_CORNERS = 100  # Maximum number of corners to track
DEFAULT_QUALITY_LEVEL = 0.3  # Quality level for corner detection (0.0-1.0)
DEFAULT_MIN_DISTANCE = 7  # Minimum distance between corners
DEFAULT_BLOCK_SIZE = 7  # Size of averaging block for corner detection

# Color Tracking Parameters (HSV Color Space)
# Default: Green color range
DEFAULT_LOWER_HSV = [35, 50, 50]  # Lower HSV threshold
DEFAULT_UPPER_HSV = [85, 255, 255]  # Upper HSV threshold

# Display Configuration
DEFAULT_SHOW_CAMERA = True  # Show camera feed window
DEFAULT_SHOW_DESKTOP = True  # Show desktop capture window
DEFAULT_WINDOW_WIDTH = 800  # Display window width
DEFAULT_WINDOW_HEIGHT = 600  # Display window height
DEFAULT_FPS_DISPLAY = True  # Show FPS counter

# Cursor Configuration
DEFAULT_MOVEMENT_MODE = "relative"  # Options: "relative" or "absolute"
DEFAULT_BOUNDARY_MARGIN = 50  # Pixels from screen edge to prevent escape

# Performance Configuration
DEFAULT_PERFORMANCE_WINDOW = 30  # Number of frames for FPS averaging
DEFAULT_MOVEMENT_THRESHOLD = 0.5  # Minimum movement to register (pixels)

# Logging Configuration
DEFAULT_LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
DEFAULT_LOG_FILE = None  # None for console only, or path to log file

# Color Presets for Color Tracking
COLOR_PRESETS = {
    'green': {
        'lower_hsv': [35, 50, 50],
        'upper_hsv': [85, 255, 255]
    },
    'blue': {
        'lower_hsv': [100, 50, 50],
        'upper_hsv': [130, 255, 255]
    },
    'red': {
        'lower_hsv': [0, 50, 50],
        'upper_hsv': [10, 255, 255]
    },
    'yellow': {
        'lower_hsv': [20, 50, 50],
        'upper_hsv': [35, 255, 255]
    },
    'purple': {
        'lower_hsv': [130, 50, 50],
        'upper_hsv': [160, 255, 255]
    }
}

# Camera Source Examples
CAMERA_SOURCE_EXAMPLES = {
    'webcam_0': 0,
    'webcam_1': 1,
    'ip_camera_example': "http://192.168.1.5:8080/video",
    'rtsp_example': "rtsp://192.168.1.5:8554/stream",
    'video_file': "path/to/video.mp4"
}

# Sensitivity Presets
SENSITIVITY_PRESETS = {
    'very_slow': 0.3,
    'slow': 0.7,
    'normal': 1.0,
    'fast': 1.5,
    'very_fast': 2.5,
    'extreme': 5.0
}

# Smoothing Presets
SMOOTHING_PRESETS = {
    'none': 0.0,
    'light': 0.2,
    'medium': 0.3,
    'heavy': 0.5,
    'very_heavy': 0.7
}
