"""
Main Module
Application entry point and orchestration
"""

import sys
import time
import logging
import signal
from typing import Optional
import numpy as np
import cv2

from .camera_manager import CameraManager
from .motion_tracker import MotionTracker
from .coordinate_transformer import CoordinateTransformer
from .cursor_controller import CursorController
from .display_manager import DisplayManager
from .utilities import (
    setup_logging, load_config, PerformanceMonitor, print_system_info
)

logger = logging.getLogger(__name__)


class OpticalMouseSystem:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = load_config(config_path)
        self.running = False
        
        self.camera_manager: Optional[CameraManager] = None
        self.motion_tracker: Optional[MotionTracker] = None
        self.coordinate_transformer: Optional[CoordinateTransformer] = None
        self.cursor_controller: Optional[CursorController] = None
        self.display_manager: Optional[DisplayManager] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logger.info("Interrupt signal received, shutting down...")
        self.running = False
    
    def initialize_system(self) -> bool:
        try:
            logger.info("Initializing Optical Mouse System...")
            
            cam_config = self.config['camera']
            self.camera_manager = CameraManager(
                source=cam_config['source'],
                width=cam_config['width'],
                height=cam_config['height'],
                fps=cam_config['fps']
            )
            
            if not self.camera_manager.initialize_camera():
                logger.error("Failed to initialize camera")
                return False
            
            cam_width, cam_height = self.camera_manager.get_frame_dimensions()
            
            track_config = self.config['tracking']
            if track_config['method'] == 'optical_flow':
                tracker_params = self.config['optical_flow']
            else:
                tracker_params = self.config['color_tracking']
            
            self.motion_tracker = MotionTracker(
                method=track_config['method'],
                **tracker_params
            )
            
            import pyautogui
            screen_width, screen_height = pyautogui.size()
            
            self.coordinate_transformer = CoordinateTransformer(
                camera_width=cam_width,
                camera_height=cam_height,
                screen_width=screen_width,
                screen_height=screen_height,
                smoothing_factor=track_config['smoothing_factor']
            )
            
            cursor_config = self.config['cursor']
            self.cursor_controller = CursorController(
                sensitivity=track_config['sensitivity'],
                boundary_margin=cursor_config['boundary_margin'],
                movement_mode=cursor_config['movement_mode']
            )
            
            display_config = self.config['display']
            self.display_manager = DisplayManager(
                window_width=display_config['window_width'],
                window_height=display_config['window_height'],
                show_camera=display_config['show_camera'],
                show_desktop=display_config['show_desktop'],
                fps_display=display_config['fps_display']
            )
            self.display_manager.create_display_windows()
            
            # Initialize recording if enabled
            if self.config.get('recording', {}).get('enabled', False):
                recording_config = self.config['recording']
                self.display_manager.initialize_recording(
                    output_file=recording_config.get('output_file', 'optical_mouse_demo_1.mp4'),
                    fps=recording_config.get('fps', 20),
                    canvas_width=cam_width,
                    canvas_height=cam_height,
                    trail_length=recording_config.get('trail_length', 100)
                )
                logger.info("Recording mode enabled")
            
            self.performance_monitor = PerformanceMonitor()
            
            logger.info("System initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            return False
    
    def main_loop(self) -> None:
        logger.info("Starting main loop...")
        self.running = True
        
        frame_count = 0
        motion_trail = []
        
        try:
            while self.running:
                self.performance_monitor.start_frame()
                
                ret, frame = self.camera_manager.read_frame()
                if not ret or frame is None:
                    logger.warning("Failed to capture frame")
                    continue
                
                delta_x, delta_y, tracking_data = self.motion_tracker.track_motion(frame)
                
                smooth_x, smooth_y = self.coordinate_transformer.apply_movement_smoothing(
                    delta_x, delta_y
                )
                
                if abs(smooth_x) > 0.5 or abs(smooth_y) > 0.5:
                    self.cursor_controller.move_cursor_relative(smooth_x, smooth_y)
                
                cursor_x, cursor_y = self.cursor_controller.get_current_cursor_position()
                
                if self.config['tracking']['method'] == 'optical_flow':
                    points = tracking_data
                    status = None
                    if isinstance(points, np.ndarray) and len(points) > 0:
                        status = np.ones(len(points))
                    camera_frame = self.display_manager.draw_tracking_overlays(
                        frame, points=points, status=status
                    )
                else:
                    centroid = tracking_data
                    if centroid:
                        motion_trail.append(centroid)
                        if len(motion_trail) > 20:
                            motion_trail.pop(0)
                    camera_frame = self.display_manager.draw_tracking_overlays(
                        frame, centroid=centroid, trails=motion_trail
                    )
                
                latency = self.performance_monitor.end_frame()
                fps = self.performance_monitor.get_fps()
                
                tracking_points = len(tracking_data) if isinstance(tracking_data, np.ndarray) else (1 if tracking_data else 0)
                camera_frame = self.display_manager.draw_performance_metrics(
                    camera_frame, fps, tracking_points, latency
                )
                
                # Check if recording is enabled
                if self.config.get('recording', {}).get('enabled', False):
                    # Create and save demo frame
                    demo_frame = self.display_manager.create_demo_frame(
                        camera_frame, cursor_x, cursor_y,
                        self.cursor_controller.screen_width,
                        self.cursor_controller.screen_height
                    )
                    self.display_manager.write_frame(demo_frame)
                    
                    # Show demo frame
                    cv2.imshow("Optical Mouse Demo - Recording", demo_frame)
                else:
                    # Original display mode
                    desktop_frame = self.display_manager.capture_desktop_region(
                        width=self.config['display']['window_width'],
                        height=self.config['display']['window_height']
                    )
                    
                    desktop_frame = self.display_manager.draw_cursor_highlight(
                        desktop_frame, cursor_x, cursor_y
                    )
                    
                    self.display_manager.update_display_windows(
                        camera_frame, desktop_frame
                    )
                
                if self.display_manager.check_exit_key():
                    logger.info("Exit key pressed")
                    break
                
                frame_count += 1
                
                if frame_count % 100 == 0:
                    logger.info(f"Frames: {frame_count}, FPS: {fps:.1f}, Latency: {latency:.1f}ms")
        
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        
        finally:
            logger.info(f"Main loop ended. Total frames: {frame_count}")
    
    def cleanup_resources(self) -> None:
        logger.info("Cleaning up resources...")
        
        if self.camera_manager:
            self.camera_manager.release_camera()
        
        if self.display_manager and self.display_manager.recording_enabled:
            self.display_manager.stop_recording()
        
        if self.display_manager:
            self.display_manager.destroy_windows()
        
        logger.info("Cleanup complete")
    
    def run(self) -> None:
        print_system_info()
        
        if not self.initialize_system():
            logger.error("System initialization failed, exiting")
            return
        
        try:
            self.main_loop()
        finally:
            self.cleanup_resources()


def main():
    setup_logging(log_level="INFO")
    
    logger.info("=" * 60)
    logger.info("OPTICAL MOUSE COMPUTER VISION PROJECT")
    logger.info("=" * 60)
    
    system = OpticalMouseSystem(config_path="config.yaml")
    system.run()
    
    logger.info("Application terminated")


if __name__ == "__main__":
    main()
