"""
Cursor Controller Module
Handles system cursor movement and positioning
"""

import pyautogui
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# PyAutoGUI safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.001  # Minimal pause between actions


class CursorController:
    """Controls system cursor movement"""
    
    def __init__(self, sensitivity: float = 1.0, 
                 boundary_margin: int = 50,
                 movement_mode: str = "relative"):
        """
        Initialize Cursor Controller
        
        Args:
            sensitivity: Movement sensitivity multiplier (default 1.0)
            boundary_margin: Pixels from screen edge to prevent cursor escape
            movement_mode: "relative" or "absolute" positioning
        """
        self.sensitivity = sensitivity
        self.boundary_margin = boundary_margin
        self.movement_mode = movement_mode
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        logger.info(f"Cursor Controller initialized: "
                   f"{self.screen_width}x{self.screen_height}, "
                   f"mode={movement_mode}, sensitivity={sensitivity}")
    
    def move_cursor_relative(self, delta_x: float, delta_y: float) -> None:
        """
        Move cursor by relative displacement
        
        Args:
            delta_x: X displacement in pixels
            delta_y: Y displacement in pixels
        """
        try:
            # Apply sensitivity
            move_x = delta_x * self.sensitivity
            move_y = delta_y * self.sensitivity
            
            # Get current position
            current_x, current_y = self.get_current_cursor_position()
            
            # Calculate new position
            new_x = current_x + move_x
            new_y = current_y + move_y
            
            # Apply boundaries
            new_x, new_y = self._apply_boundaries(new_x, new_y)
            
            # Move cursor
            pyautogui.moveTo(new_x, new_y, duration=0)
            
        except Exception as e:
            logger.error(f"Cursor movement error: {e}")
    
    def move_cursor_absolute(self, screen_x: int, screen_y: int) -> None:
        """
        Move cursor to absolute screen position
        
        Args:
            screen_x: Target X coordinate
            screen_y: Target Y coordinate
        """
        try:
            # Apply boundaries
            screen_x, screen_y = self._apply_boundaries(screen_x, screen_y)
            
            # Move cursor
            pyautogui.moveTo(screen_x, screen_y, duration=0)
            
        except Exception as e:
            logger.error(f"Cursor movement error: {e}")
    
    def get_current_cursor_position(self) -> Tuple[int, int]:
        """
        Get current cursor position
        
        Returns:
            Tuple of (x, y) coordinates
        """
        try:
            position = pyautogui.position()
            return position.x, position.y
        except Exception as e:
            logger.error(f"Failed to get cursor position: {e}")
            return 0, 0
    
    def _apply_boundaries(self, x: float, y: float) -> Tuple[int, int]:
        """
        Apply boundary constraints to cursor position
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of constrained (x, y)
        """
        # Clamp to screen bounds with margin
        x = max(self.boundary_margin, 
                min(self.screen_width - self.boundary_margin, x))
        y = max(self.boundary_margin, 
                min(self.screen_height - self.boundary_margin, y))
        
        return int(x), int(y)
    
    def set_sensitivity(self, sensitivity: float) -> None:
        """
        Update cursor sensitivity
        
        Args:
            sensitivity: New sensitivity value (0.1-10.0)
        """
        self.sensitivity = max(0.1, min(10.0, sensitivity))
        logger.info(f"Cursor sensitivity set to {self.sensitivity}")
    
    def set_movement_mode(self, mode: str) -> None:
        """
        Set movement mode
        
        Args:
            mode: "relative" or "absolute"
        """
        if mode in ["relative", "absolute"]:
            self.movement_mode = mode
            logger.info(f"Movement mode set to {mode}")
        else:
            logger.warning(f"Invalid movement mode: {mode}")
    
    def set_boundary_margin(self, margin: int) -> None:
        """
        Set boundary margin
        
        Args:
            margin: Pixels from screen edge (0-500)
        """
        self.boundary_margin = max(0, min(500, margin))
        logger.info(f"Boundary margin set to {self.boundary_margin}")
    
    def center_cursor(self) -> None:
        """Move cursor to screen center"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        self.move_cursor_absolute(center_x, center_y)
        logger.info("Cursor centered")
    
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """
        Get screen dimensions
        
        Returns:
            Tuple of (width, height)
        """
        return self.screen_width, self.screen_height
    
    def is_cursor_at_edge(self, threshold: int = 10) -> bool:
        """
        Check if cursor is near screen edge
        
        Args:
            threshold: Distance from edge in pixels
            
        Returns:
            True if cursor is near edge
        """
        x, y = self.get_current_cursor_position()
        
        return (x <= threshold or 
                x >= self.screen_width - threshold or
                y <= threshold or
                y >= self.screen_height - threshold)
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"CursorController(sensitivity={self.sensitivity}, "
                f"mode={self.movement_mode}, "
                f"screen={self.screen_width}x{self.screen_height})")
