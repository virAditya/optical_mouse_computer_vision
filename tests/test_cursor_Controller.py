"""
Unit tests for Cursor Controller module
"""

import unittest
from unittest.mock import Mock, patch

from optical_mouse.cursor_controller import CursorController


class TestCursorController(unittest.TestCase):
    """Test cases for CursorController class"""
    
    @patch('pyautogui.size')
    def setUp(self, mock_size):
        """Set up test fixtures"""
        mock_size.return_value = (1920, 1080)
        self.controller = CursorController(
            sensitivity=1.0,
            boundary_margin=50,
            movement_mode="relative"
        )
    
    def test_initialization(self):
        """Test controller initialization"""
        self.assertEqual(self.controller.sensitivity, 1.0)
        self.assertEqual(self.controller.boundary_margin, 50)
        self.assertEqual(self.controller.movement_mode, "relative")
        self.assertEqual(self.controller.screen_width, 1920)
        self.assertEqual(self.controller.screen_height, 1080)
    
    @patch('pyautogui.position')
    @patch('pyautogui.moveTo')
    def test_move_cursor_relative(self, mock_moveto, mock_position):
        """Test relative cursor movement"""
        mock_position.return_value = Mock(x=500, y=500)
        
        self.controller.move_cursor_relative(10, 5)
        
        mock_moveto.assert_called_once()
        call_args = mock_moveto.call_args[0]
        self.assertEqual(call_args[0], 510)
        self.assertEqual(call_args[1], 505)
    
    @patch('pyautogui.position')
    @patch('pyautogui.moveTo')
    def test_move_cursor_relative_with_sensitivity(self, mock_moveto, mock_position):
        """Test relative cursor movement with custom sensitivity"""
        mock_position.return_value = Mock(x=500, y=500)
        self.controller.set_sensitivity(2.0)
        
        self.controller.move_cursor_relative(10, 5)
        
        call_args = mock_moveto.call_args[0]
        self.assertEqual(call_args[0], 520)  # 500 + 10*2
        self.assertEqual(call_args[1], 510)  # 500 + 5*2
    
    @patch('pyautogui.moveTo')
    def test_move_cursor_absolute(self, mock_moveto):
        """Test absolute cursor movement"""
        self.controller.move_cursor_absolute(100, 200)
        
        mock_moveto.assert_called_once_with(100, 200, duration=0)
    
    @patch('pyautogui.position')
    def test_get_current_cursor_position(self, mock_position):
        """Test getting cursor position"""
        mock_position.return_value = Mock(x=123, y=456)
        
        x, y = self.controller.get_current_cursor_position()
        
        self.assertEqual(x, 123)
        self.assertEqual(y, 456)
    
    def test_apply_boundaries_within_bounds(self):
        """Test boundary application for valid coordinates"""
        x, y = self.controller._apply_boundaries(500, 500)
        
        self.assertEqual(x, 500)
        self.assertEqual(y, 500)
    
    def test_apply_boundaries_below_minimum(self):
        """Test boundary application for coordinates below minimum"""
        x, y = self.controller._apply_boundaries(10, 10)
        
        self.assertEqual(x, 50)  # Clamped to boundary_margin
        self.assertEqual(y, 50)
    
    def test_apply_boundaries_above_maximum(self):
        """Test boundary application for coordinates above maximum"""
        x, y = self.controller._apply_boundaries(2000, 2000)
        
        self.assertEqual(x, 1870)  # 1920 - 50
        self.assertEqual(y, 1030)  # 1080 - 50
    
    def test_set_sensitivity(self):
        """Test sensitivity setting"""
        self.controller.set_sensitivity(2.5)
        self.assertEqual(self.controller.sensitivity, 2.5)
        
        # Test clamping to maximum
        self.controller.set_sensitivity(20.0)
        self.assertEqual(self.controller.sensitivity, 10.0)
        
        # Test clamping to minimum
        self.controller.set_sensitivity(0.05)
        self.assertEqual(self.controller.sensitivity, 0.1)
    
    def test_set_movement_mode_valid(self):
        """Test setting valid movement modes"""
        self.controller.set_movement_mode("absolute")
        self.assertEqual(self.controller.movement_mode, "absolute")
        
        self.controller.set_movement_mode("relative")
        self.assertEqual(self.controller.movement_mode, "relative")
    
    def test_set_movement_mode_invalid(self):
        """Test setting invalid movement mode"""
        original_mode = self.controller.movement_mode
        self.controller.set_movement_mode("invalid")
        # Mode should remain unchanged
        self.assertEqual(self.controller.movement_mode, original_mode)
    
    def test_set_boundary_margin(self):
        """Test boundary margin setting"""
        self.controller.set_boundary_margin(100)
        self.assertEqual(self.controller.boundary_margin, 100)
        
        # Test clamping
        self.controller.set_boundary_margin(1000)
        self.assertEqual(self.controller.boundary_margin, 500)
        
        self.controller.set_boundary_margin(-10)
        self.assertEqual(self.controller.boundary_margin, 0)
    
    @patch('pyautogui.moveTo')
    def test_center_cursor(self, mock_moveto):
        """Test cursor centering"""
        self.controller.center_cursor()
        
        mock_moveto.assert_called_once()
        call_args = mock_moveto.call_args[0]
        self.assertEqual(call_args[0], 960)  # 1920 / 2
        self.assertEqual(call_args[1], 540)  # 1080 / 2
    
    def test_get_screen_dimensions(self):
        """Test getting screen dimensions"""
        width, height = self.controller.get_screen_dimensions()
        
        self.assertEqual(width, 1920)
        self.assertEqual(height, 1080)
    
    @patch('pyautogui.position')
    def test_is_cursor_at_edge_true(self, mock_position):
        """Test cursor at edge detection - at edge"""
        mock_position.return_value = Mock(x=5, y=500)
        
        result = self.controller.is_cursor_at_edge(threshold=10)
        
        self.assertTrue(result)
    
    @patch('pyautogui.position')
    def test_is_cursor_at_edge_false(self, mock_position):
        """Test cursor at edge detection - not at edge"""
        mock_position.return_value = Mock(x=500, y=500)
        
        result = self.controller.is_cursor_at_edge(threshold=10)
        
        self.assertFalse(result)
    
    def test_repr(self):
        """Test string representation"""
        repr_str = repr(self.controller)
        
        self.assertIn("CursorController", repr_str)
        self.assertIn("sensitivity=1.0", repr_str)
        self.assertIn("mode=relative", repr_str)


if __name__ == '__main__':
    unittest.main()
