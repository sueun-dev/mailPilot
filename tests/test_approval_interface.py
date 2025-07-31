"""Tests for the approval interface module."""
import unittest
from unittest.mock import Mock, patch

from src.approval.interface import ApprovalInterface
from rich.panel import Panel


class TestApprovalInterface(unittest.TestCase):
    """Test cases for ApprovalInterface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ui = ApprovalInterface()
    
    @patch('src.approval.interface.Console')
    def test_init(self, mock_console):
        """Test interface initialization."""
        ui = ApprovalInterface()
        mock_console.assert_called_once()
        self.assertIsNotNone(ui.console)
    
    def test_display_message_info(self):
        """Test displaying info message."""
        with patch.object(self.ui.console, 'print') as mock_console_print:
            self.ui.display_message('Test info message', 'info')
            
            mock_console_print.assert_called_once()
            call_args = str(mock_console_print.call_args[0][0])
            self.assertIn('Test info message', call_args)
    
    def test_display_message_success(self):
        """Test displaying success message."""
        with patch.object(self.ui.console, 'print') as mock_console_print:
            self.ui.display_message('Test success message', 'success')
            
            mock_console_print.assert_called_once()
            call_args = str(mock_console_print.call_args[0][0])
            self.assertIn('Test success message', call_args)
    
    def test_display_message_warning(self):
        """Test displaying warning message."""
        with patch.object(self.ui.console, 'print') as mock_console_print:
            self.ui.display_message('Test warning message', 'warning')
            
            mock_console_print.assert_called_once()
            call_args = str(mock_console_print.call_args[0][0])
            self.assertIn('Test warning message', call_args)
    
    def test_display_message_error(self):
        """Test displaying error message."""
        with patch.object(self.ui.console, 'print') as mock_console_print:
            self.ui.display_message('Test error message', 'error')
            
            mock_console_print.assert_called_once()
            call_args = str(mock_console_print.call_args[0][0])
            self.assertIn('Test error message', call_args)
    
    @patch('src.approval.interface.Confirm.ask')
    def test_display_draft_approved(self, mock_confirm):
        """Test displaying draft and approving it."""
        mock_confirm.return_value = True
        
        with patch.object(self.ui.console, 'print') as mock_console_print:
            with patch.object(self.ui.console, 'clear') as mock_clear:
                draft = {
                    'to': 'recipient@example.com',
                    'subject': 'Test Subject',
                    'body': 'Test email body',
                    'context': 'Previous conversation context'
                }
                
                result = self.ui.display_draft(draft)
                
                self.assertTrue(result)
                mock_clear.assert_called_once()
    
    @patch('src.approval.interface.Confirm.ask')
    def test_display_draft_rejected(self, mock_confirm):
        """Test displaying draft and rejecting it."""
        mock_confirm.return_value = False
        
        with patch.object(self.ui.console, 'print') as mock_console_print:
            with patch.object(self.ui.console, 'clear') as mock_clear:
                draft = {
                    'to': 'recipient@example.com',
                    'subject': 'Test Subject',
                    'body': 'Test email body'
                }
                
                result = self.ui.display_draft(draft)
                
                self.assertFalse(result)
    
    @patch('src.approval.interface.Confirm.ask')
    def test_display_draft_no_context(self, mock_confirm):
        """Test displaying draft without context."""
        mock_confirm.return_value = False
        
        with patch.object(self.ui.console, 'print') as mock_console_print:
            with patch.object(self.ui.console, 'clear') as mock_clear:
                draft = {
                    'to': 'recipient@example.com',
                    'subject': 'Test Subject',
                    'body': 'Test email body'
                }
                
                self.ui.display_draft(draft)
                
                # Check that context panel was not created
                calls_str = str(mock_console_print.call_args_list)
                self.assertNotIn('Conversation Context', calls_str)
    
    def test_display_thread_summary(self):
        """Test displaying thread summary."""
        with patch.object(self.ui.console, 'print') as mock_console_print:
            summary = {
                'thread_id': 'thread123',
                'customer_email': 'sender@example.com',
                'message_count': 3,
                'zoom_scheduled': False,
                'created_at': '2024-01-01'
            }
            
            self.ui.display_thread_summary(summary)
            
            mock_console_print.assert_called_once()
            # The actual call is a Panel object, check its attributes
            panel = mock_console_print.call_args[0][0]
            self.assertIsInstance(panel, Panel)
            panel_str = str(panel.renderable)
            self.assertIn('sender@example.com', panel_str)
            self.assertIn('3', panel_str)
    
    def test_display_thread_summary_with_zoom(self):
        """Test displaying thread summary with Zoom scheduled."""
        with patch.object(self.ui.console, 'print') as mock_console_print:
            summary = {
                'thread_id': 'thread123',
                'customer_email': 'sender@example.com',
                'message_count': 5,
                'zoom_scheduled': True,
                'created_at': '2024-01-01'
            }
            
            self.ui.display_thread_summary(summary)
            
            # The actual call is a Panel object, check its attributes
            panel = mock_console_print.call_args[0][0]
            self.assertIsInstance(panel, Panel)
            panel_str = str(panel.renderable)
            self.assertIn('✅', panel_str)
    
    @patch('builtins.input')
    def test_prompt_action(self, mock_input):
        """Test prompting for action."""
        mock_input.return_value = '1'
        
        with patch.object(self.ui.console, 'print') as mock_console_print:
            result = self.ui.prompt_action()
            
            self.assertEqual(result, '1')
            
            calls_str = str(mock_console_print.call_args_list)
            self.assertIn('Check for new emails', calls_str)
            self.assertIn('View active threads', calls_str)
            self.assertIn('Exit', calls_str)
    


if __name__ == '__main__':
    unittest.main()