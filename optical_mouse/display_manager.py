"""
Display Manager Module
Handles window creation, visualization, and screen capture
"""

import cv2
import numpy as np
import mss
import logging
from typing import Optional, Tuple, List
import time

logger = logging.getLogger(__name__)


class DisplayManager:
    """Manages display windows and visualization"""
    
    def __init__(self, window_width: int = 800, window_height: int = 600,
                 show_camera: bool = True, show_desktop: bool = True,
                 fps_display: bool = True):
        self.window_width = window_width
        self.window_height = window_height
        self.show_camera = show_camera
        self.show_desktop = show_desktop
        self.fps_display = fps_display
        
        self.window_camera_name = "Camera Feed - Optical Mouse"
        self.window_desktop_name = "Desktop View - Optical Mouse"
        
        self.sct = mss.mss()
        
        self.frame_times = []
        self.current_fps = 0
        
        # Recording attributes
        self.video_writer = None
        self.tracking_canvas = None
        self.cursor_trail = []
        self.recording_enabled = False
        
        logger.info("Display Manager initialized")
    
    def create_display_windows(self) -> None:
        if self.show_camera:
            cv2.namedWindow(self.window_camera_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_camera_name, self.window_width, self.window_height)
            cv2.moveWindow(self.window_camera_name, 50, 50)
        
        if self.show_desktop:
            cv2.namedWindow(self.window_desktop_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_desktop_name, self.window_width, self.window_height)
            cv2.moveWindow(self.window_desktop_name, self.window_width + 100, 50)
        
        logger.info("Display windows created")
    
    def draw_tracking_overlays(self, frame: np.ndarray, 
                               points: Optional[np.ndarray] = None,
                               status: Optional[np.ndarray] = None,
                               centroid: Optional[Tuple[int, int]] = None,
                               trails: Optional[List] = None) -> np.ndarray:
        display_frame = frame.copy()
        
        if points is not None and len(points) > 0:
            if status is not None:
                for i, (point, stat) in enumerate(zip(points, status)):
                    if stat == 1:
                        # Safely extract x, y coordinates
                        xy = point.flatten()
                        x, y = int(xy[0]), int(xy[1])
                        cv2.circle(display_frame, (x, y), 5, (0, 255, 0), -1)
                    else:
                        # Safely extract x, y coordinates
                        xy = point.flatten()
                        x, y = int(xy[0]), int(xy[1])
                        cv2.circle(display_frame, (x, y), 5, (0, 0, 255), -1)
            else:
                for point in points:
                    # Safely extract x, y coordinates
                    xy = point.flatten()
                    x, y = int(xy[0]), int(xy[1])
                    cv2.circle(display_frame, (x, y), 5, (0, 255, 0), -1)
        
        if centroid is not None:
            cx, cy = centroid
            cv2.circle(display_frame, (cx, cy), 10, (255, 0, 255), -1)
            cv2.circle(display_frame, (cx, cy), 20, (255, 0, 255), 2)
            cv2.line(display_frame, (cx - 15, cy), (cx + 15, cy), (255, 0, 255), 2)
            cv2.line(display_frame, (cx, cy - 15), (cx, cy + 15), (255, 0, 255), 2)
        
        if trails is not None and len(trails) > 1:
            points_array = np.array(trails, dtype=np.int32)
            cv2.polylines(display_frame, [points_array], False, (0, 255, 255), 2)
        
        return display_frame
    
    def capture_desktop_region(self, x: int = 0, y: int = 0,
                               width: Optional[int] = None,
                               height: Optional[int] = None) -> np.ndarray:
        try:
            monitor = {
                "top": y,
                "left": x,
                "width": width or self.sct.monitors[1]["width"],
                "height": height or self.sct.monitors[1]["height"]
            }
            
            sct_img = self.sct.grab(monitor)
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            return frame
            
        except Exception as e:
            logger.error(f"Screen capture error: {e}")
            return np.zeros((height or 480, width or 640, 3), dtype=np.uint8)
    
    def draw_cursor_highlight(self, desktop_frame: np.ndarray,
                             cursor_x: int, cursor_y: int,
                             region_x: int = 0, region_y: int = 0) -> np.ndarray:
        display_frame = desktop_frame.copy()
        
        frame_x = cursor_x - region_x
        frame_y = cursor_y - region_y
        
        h, w = display_frame.shape[:2]
        if 0 <= frame_x < w and 0 <= frame_y < h:
            cv2.line(display_frame, (frame_x - 20, frame_y), 
                    (frame_x + 20, frame_y), (0, 0, 255), 2)
            cv2.line(display_frame, (frame_x, frame_y - 20), 
                    (frame_x, frame_y + 20), (0, 0, 255), 2)
            
            cv2.circle(display_frame, (frame_x, frame_y), 15, (0, 0, 255), 2)
            cv2.circle(display_frame, (frame_x, frame_y), 25, (0, 255, 255), 1)
        
        return display_frame
    
    def draw_performance_metrics(self, frame: np.ndarray,
                                fps: float,
                                tracking_points: int = 0,
                                latency: float = 0.0) -> np.ndarray:
        if not self.fps_display:
            return frame
        
        display_frame = frame.copy()
        
        info_lines = [
            f"FPS: {fps:.1f}",
            f"Points: {tracking_points}",
            f"Latency: {latency:.1f}ms"
        ]
        
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (10, 10), (250, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, display_frame, 0.4, 0, display_frame)
        
        y_offset = 35
        for line in info_lines:
            cv2.putText(display_frame, line, (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset += 25
        
        return display_frame
    
    def update_display_windows(self, camera_frame: Optional[np.ndarray] = None,
                              desktop_frame: Optional[np.ndarray] = None) -> None:
        if self.show_camera and camera_frame is not None:
            cv2.imshow(self.window_camera_name, camera_frame)
        
        if self.show_desktop and desktop_frame is not None:
            cv2.imshow(self.window_desktop_name, desktop_frame)
    
    def calculate_fps(self, current_time: float) -> float:
        self.frame_times.append(current_time)
        
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        
        if len(self.frame_times) > 1:
            time_diff = self.frame_times[-1] - self.frame_times[0]
            if time_diff > 0:
                self.current_fps = len(self.frame_times) / time_diff
        
        return self.current_fps
    
    def check_exit_key(self, delay: int = 1) -> bool:
        key = cv2.waitKey(delay) & 0xFF
        return key == 27 or key == ord('q')
    
    def initialize_recording(self, output_file: str, fps: int = 20, 
                            canvas_width: int = 640, canvas_height: int = 480,
                            trail_length: int = 100) -> bool:
        """
        Initialize video recording
        
        Args:
            output_file: Path to save video
            fps: Recording frames per second
            canvas_width: Width of tracking canvas
            canvas_height: Height of tracking canvas
            trail_length: Number of trail points to keep
        """
        try:
            # Combined frame will be side-by-side (camera + canvas)
            frame_width = canvas_width * 2
            frame_height = canvas_height
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                output_file, fourcc, fps, (frame_width, frame_height)
            )
            
            # Create black canvas for tracking visualization
            self.tracking_canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
            self.cursor_trail = []
            self.recording_enabled = True
            self.trail_length = trail_length
            
            logger.info(f"Recording initialized: {output_file} ({frame_width}x{frame_height} @ {fps}fps)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize recording: {e}")
            return False
    
    def draw_cursor_on_canvas(self, cursor_x: int, cursor_y: int, 
                              screen_width: int = 1920, screen_height: int = 1080) -> np.ndarray:
        """
        Draw cursor position and trail on black canvas
        
        Args:
            cursor_x: Cursor X position on screen
            cursor_y: Cursor Y position on screen
            screen_width: Screen width for scaling
            screen_height: Screen height for scaling
        """
        if self.tracking_canvas is None:
            return np.zeros((480, 640, 3), dtype=np.uint8)
        
        canvas_height, canvas_width = self.tracking_canvas.shape[:2]
        
        # Scale cursor position to canvas size
        scaled_x = int((cursor_x / screen_width) * canvas_width)
        scaled_y = int((cursor_y / screen_height) * canvas_height)
        
        # Add to trail
        self.cursor_trail.append((scaled_x, scaled_y))
        
        # Keep trail length limited
        if len(self.cursor_trail) > self.trail_length:
            self.cursor_trail.pop(0)
        
        # Fade the canvas slightly (trail effect)
        self.tracking_canvas = cv2.addWeighted(self.tracking_canvas, 0.95, 
                                               self.tracking_canvas, 0, 0)
        
        # Draw trail
        if len(self.cursor_trail) > 1:
            for i in range(1, len(self.cursor_trail)):
                pt1 = self.cursor_trail[i-1]
                pt2 = self.cursor_trail[i]
                
                # Color gradient (blue to cyan to yellow)
                color_intensity = int(255 * (i / len(self.cursor_trail)))
                color = (255 - color_intensity, color_intensity, 255)
                
                thickness = max(1, int(3 * (i / len(self.cursor_trail))))
                cv2.line(self.tracking_canvas, pt1, pt2, color, thickness)
        
        # Draw current cursor position (bright)
        if 0 <= scaled_x < canvas_width and 0 <= scaled_y < canvas_height:
            cv2.circle(self.tracking_canvas, (scaled_x, scaled_y), 10, (0, 255, 255), -1)
            cv2.circle(self.tracking_canvas, (scaled_x, scaled_y), 15, (255, 255, 255), 2)
            
            # Draw crosshair
            cv2.line(self.tracking_canvas, (scaled_x - 20, scaled_y), 
                    (scaled_x + 20, scaled_y), (255, 255, 255), 2)
            cv2.line(self.tracking_canvas, (scaled_x, scaled_y - 20), 
                    (scaled_x, scaled_y + 20), (255, 255, 255), 2)
        
        return self.tracking_canvas.copy()
    
    def create_demo_frame(self, camera_frame: np.ndarray, 
                         cursor_x: int, cursor_y: int,
                         screen_width: int = 1920, screen_height: int = 1080) -> np.ndarray:
        """
        Create side-by-side demo frame (camera + tracking canvas)
        
        Args:
            camera_frame: Camera feed with tracking overlays
            cursor_x: Current cursor X position
            cursor_y: Current cursor Y position
            screen_width: Screen width
            screen_height: Screen height
        """
        if self.tracking_canvas is None:
            return camera_frame
        
        canvas_height, canvas_width = self.tracking_canvas.shape[:2]
        
        # Resize camera frame to match canvas height
        camera_resized = cv2.resize(camera_frame, (canvas_width, canvas_height))
        
        # Draw cursor on black canvas
        tracking_canvas = self.draw_cursor_on_canvas(cursor_x, cursor_y, 
                                                      screen_width, screen_height)
        
        # Add text labels with background
        # Camera side
        cv2.rectangle(camera_resized, (5, 5), (635, 45), (0, 0, 0), -1)
        cv2.putText(camera_resized, "Camera Feed + Tracking Points", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Canvas side
        cv2.rectangle(tracking_canvas, (5, 5), (635, 45), (50, 50, 50), -1)
        cv2.putText(tracking_canvas, "Cursor Movement Visualization", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Add "RECORDING" indicator
        cv2.circle(camera_resized, (canvas_width - 30, 25), 8, (0, 0, 255), -1)
        cv2.putText(camera_resized, "REC", 
                    (canvas_width - 60, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Combine side-by-side
        combined_frame = np.hstack([camera_resized, tracking_canvas])
        
        return combined_frame
    
    def write_frame(self, frame: np.ndarray) -> None:
        """Write frame to video file"""
        if self.video_writer is not None and self.recording_enabled:
            self.video_writer.write(frame)
    
    def stop_recording(self) -> None:
        """Stop video recording and release resources"""
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.recording_enabled = False
            logger.info("Recording stopped and saved")
    
    def destroy_windows(self) -> None:
        cv2.destroyAllWindows()
        logger.info("Display windows destroyed")
    
    def __del__(self):
        if hasattr(self, 'sct'):
            self.sct.close()
        if hasattr(self, 'video_writer') and self.video_writer is not None:
            self.video_writer.release()
