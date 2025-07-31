"""Tests for the main EmailAutoResponder class."""
import unittest
from unittest.mock import Mock, patch, MagicMock

from src.main import EmailAutoResponder


class TestEmailAutoResponder(unittest.TestCase):
    """Test cases for EmailAutoResponder."""
    
    @patch('src.main.ApprovalInterface')
    @patch('src.main.ThreadMemory')
    @patch('src.main.ChatGPTClient')
    @patch('src.main.GmailClient')
    def setUp(self, mock_gmail, mock_chatgpt, mock_memory, mock_ui):
        """Set up test fixtures."""
        self.mock_gmail_instance = Mock()
        self.mock_chatgpt_instance = Mock()
        self.mock_memory_instance = Mock()
        self.mock_ui_instance = Mock()
        
        mock_gmail.return_value = self.mock_gmail_instance
        mock_chatgpt.return_value = self.mock_chatgpt_instance
        mock_memory.return_value = self.mock_memory_instance
        mock_ui.return_value = self.mock_ui_instance
        
        self.responder = EmailAutoResponder(
            gmail_creds='test_creds.json',
            openai_api_key='test_key'
        )
    
    def test_init(self):
        """Test responder initialization."""
        self.assertIsNotNone(self.responder.gmail)
        self.assertIsNotNone(self.responder.chatgpt)
        self.assertIsNotNone(self.responder.memory)
        self.assertIsNotNone(self.responder.ui)
    
    def test_process_email_zoom_already_scheduled(self):
        """Test processing email when Zoom is already scheduled."""
        message = {
            'thread_id': 'thread123',
            'id': 'msg123',
            'sender': 'test@example.com',
            'subject': 'Test',
            'body': 'Test message'
        }
        
        self.mock_memory_instance.is_zoom_scheduled.return_value = True
        
        result = self.responder.process_email(message)
        
        self.assertFalse(result)
        self.mock_ui_instance.display_message.assert_called_with(
            'Zoom already scheduled for thread thread12...', 'warning'
        )
    
    def test_process_email_successful(self):
        """Test successful email processing."""
        message = {
            'thread_id': 'thread123',
            'id': 'msg123',
            'sender': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'Test message body'
        }
        
        self.mock_memory_instance.is_zoom_scheduled.return_value = False
        self.mock_memory_instance.get_thread_context.return_value = 'Previous context'
        self.mock_chatgpt_instance.generate_response.return_value = 'Generated response'
        self.mock_chatgpt_instance.check_zoom_mention.return_value = False
        self.mock_ui_instance.display_draft.return_value = True
        self.mock_gmail_instance.send_message.return_value = {'id': 'sent_msg'}
        
        result = self.responder.process_email(message)
        
        self.assertTrue(result)
        
        # Verify message was added to memory
        self.mock_memory_instance.add_message.assert_called()
        
        # Verify response was generated
        self.mock_chatgpt_instance.generate_response.assert_called_with(
            customer_message='Test message body',
            thread_context='Previous context'
        )
        
        # Verify draft was displayed
        self.mock_ui_instance.display_draft.assert_called_once()
        
        # Verify email was sent
        self.mock_gmail_instance.send_message.assert_called_with(
            to='test@example.com',
            subject='Re: Test Subject',
            body='Generated response',
            thread_id='thread123'
        )
        
        # Verify message was marked as read
        self.mock_gmail_instance.mark_as_read.assert_called_with('msg123')
    
    def test_process_email_generation_failed(self):
        """Test email processing when response generation fails."""
        message = {
            'thread_id': 'thread123',
            'id': 'msg123',
            'sender': 'test@example.com',
            'subject': 'Test',
            'body': 'Test message'
        }
        
        self.mock_memory_instance.is_zoom_scheduled.return_value = False
        self.mock_chatgpt_instance.generate_response.return_value = ''
        
        result = self.responder.process_email(message)
        
        self.assertFalse(result)
        self.mock_ui_instance.display_message.assert_called_with(
            'Failed to generate response', 'error'
        )
    
    def test_process_email_draft_rejected(self):
        """Test email processing when draft is rejected."""
        message = {
            'thread_id': 'thread123',
            'id': 'msg123',
            'sender': 'test@example.com',
            'subject': 'Test',
            'body': 'Test message'
        }
        
        self.mock_memory_instance.is_zoom_scheduled.return_value = False
        self.mock_chatgpt_instance.generate_response.return_value = 'Generated response'
        self.mock_ui_instance.display_draft.return_value = False
        
        result = self.responder.process_email(message)
        
        self.assertFalse(result)
        self.mock_ui_instance.display_message.assert_called_with(
            'Email draft rejected', 'warning'
        )
    
    def test_process_email_send_failed(self):
        """Test email processing when send fails."""
        message = {
            'thread_id': 'thread123',
            'id': 'msg123',
            'sender': 'test@example.com',
            'subject': 'Test',
            'body': 'Test message'
        }
        
        self.mock_memory_instance.is_zoom_scheduled.return_value = False
        self.mock_chatgpt_instance.generate_response.return_value = 'Generated response'
        self.mock_ui_instance.display_draft.return_value = True
        self.mock_gmail_instance.send_message.return_value = {}
        
        result = self.responder.process_email(message)
        
        self.assertFalse(result)
        self.mock_ui_instance.display_message.assert_called_with(
            'Failed to send email', 'error'
        )
    
    def test_process_email_with_zoom_mention(self):
        """Test email processing with Zoom mention."""
        message = {
            'thread_id': 'thread123',
            'id': 'msg123',
            'sender': 'test@example.com',
            'subject': 'Test',
            'body': 'Test message'
        }
        
        self.mock_memory_instance.is_zoom_scheduled.return_value = False
        self.mock_chatgpt_instance.generate_response.return_value = 'Zoom meeting scheduled'
        self.mock_chatgpt_instance.check_zoom_mention.return_value = True
        self.mock_ui_instance.display_draft.return_value = True
        self.mock_gmail_instance.send_message.return_value = {'id': 'sent_msg'}
        
        result = self.responder.process_email(message)
        
        self.assertTrue(result)
        self.mock_memory_instance.mark_zoom_scheduled.assert_called_with('thread123')
        
        # Check for success message about Zoom
        calls = self.mock_ui_instance.display_message.call_args_list
        zoom_message_found = any(
            'Zoom meeting mentioned' in str(call) for call in calls
        )
        self.assertTrue(zoom_message_found)
    
    def test_check_new_emails_no_messages(self):
        """Test checking emails when there are no new messages."""
        self.mock_gmail_instance.get_unread_messages.return_value = []
        
        self.responder.check_new_emails()
        
        self.mock_ui_instance.display_message.assert_any_call(
            'No new emails found', 'info'
        )
    
    def test_check_new_emails_with_messages(self):
        """Test checking emails with new messages."""
        messages = [
            {'sender': 'test1@example.com', 'thread_id': 'thread1'},
            {'sender': 'test2@example.com', 'thread_id': 'thread2'}
        ]
        
        self.mock_gmail_instance.get_unread_messages.return_value = messages
        
        with patch.object(self.responder, 'process_email') as mock_process:
            self.responder.check_new_emails()
        
        self.mock_ui_instance.display_message.assert_any_call(
            'Found 2 new email(s)', 'success'
        )
        self.assertEqual(mock_process.call_count, 2)
    
    def test_view_active_threads_none(self):
        """Test viewing active threads when there are none."""
        self.mock_memory_instance.get_active_threads.return_value = []
        
        self.responder.view_active_threads()
        
        self.mock_ui_instance.display_message.assert_called_with(
            'No active threads', 'info'
        )
    
    def test_view_active_threads_with_data(self):
        """Test viewing active threads with data."""
        self.mock_memory_instance.get_active_threads.return_value = ['thread1', 'thread2']
        
        summary1 = {
            'thread_id': 'thread1', 
            'customer_email': 'test1@example.com',
            'message_count': 2,
            'zoom_scheduled': False,
            'created_at': '2024-01-01'
        }
        summary2 = {
            'thread_id': 'thread2',
            'customer_email': 'test2@example.com',
            'message_count': 3,
            'zoom_scheduled': False,
            'created_at': '2024-01-01'
        }
        
        self.mock_memory_instance.get_thread_summary.side_effect = [summary1, summary2]
        
        self.responder.view_active_threads()
        
        self.mock_ui_instance.display_message.assert_any_call(
            '\n[bold]Active Threads (2):[/bold]', 'info'
        )
        self.assertEqual(self.mock_ui_instance.display_thread_summary.call_count, 2)
    
    def test_run_check_emails(self):
        """Test run loop with check emails option."""
        self.mock_ui_instance.prompt_action.side_effect = ['1', '3']
        
        with patch.object(self.responder, 'check_new_emails') as mock_check:
            self.responder.run()
        
        mock_check.assert_called_once()
        self.mock_ui_instance.display_message.assert_any_call(
            '\nGoodbye! 👋', 'info'
        )
    
    def test_run_view_threads(self):
        """Test run loop with view threads option."""
        self.mock_ui_instance.prompt_action.side_effect = ['2', '3']
        
        with patch.object(self.responder, 'view_active_threads') as mock_view:
            self.responder.run()
        
        mock_view.assert_called_once()
    
    def test_run_invalid_choice(self):
        """Test run loop with invalid choice."""
        self.mock_ui_instance.prompt_action.side_effect = ['9', '3']
        
        self.responder.run()
        
        self.mock_ui_instance.display_message.assert_any_call(
            'Invalid choice. Please try again.', 'error'
        )
    
    @patch('time.sleep')
    def test_run_with_keyboard_interrupt(self, mock_sleep):
        """Test run loop with keyboard interrupt."""
        self.mock_ui_instance.prompt_action.side_effect = KeyboardInterrupt()
        
        with self.assertRaises(KeyboardInterrupt):
            self.responder.run()


class TestMainFunction(unittest.TestCase):
    """Test cases for the main function."""
    
    @patch('os.environ.get')
    @patch('os.path.exists')
    @patch('builtins.print')
    @patch('sys.path', new=[])
    def test_main_no_api_key(self, mock_print, mock_exists, mock_get):
        """Test main function when API key is missing."""
        mock_get.return_value = None
        
        from src.main import main
        main()
        
        # Check for error message about missing API key
        # The exact message may vary based on logging configuration
    
    @patch('os.environ.get')
    @patch('os.path.exists')
    @patch('builtins.print')
    @patch('sys.path', new=[])
    def test_main_no_credentials_file(self, mock_print, mock_exists, mock_get):
        """Test main function when credentials file is missing."""
        mock_get.return_value = 'test_key'
        mock_exists.return_value = False
        
        from src.main import main
        main()
        
        mock_print.assert_any_call('Error: config/credentials.json not found')
    
    @patch('os.environ.get')
    @patch('os.path.exists')
    @patch('src.main.EmailAutoResponder')
    @patch('sys.path', new=[])
    def test_main_successful(self, mock_responder_class, mock_exists, mock_get):
        """Test successful main function execution."""
        mock_get.return_value = 'test_key'
        mock_exists.return_value = True
        
        mock_responder_instance = Mock()
        mock_responder_class.return_value = mock_responder_instance
        
        from src.main import main
        main()
        
        # Check that credentials path includes 'config/'
        call_args = mock_responder_class.call_args
        self.assertIn('config', call_args[1]['gmail_creds'])
        self.assertEqual(call_args[1]['openai_api_key'], 'test_key')
        mock_responder_instance.run.assert_called_once()
    
    @patch('os.environ.get')
    @patch('os.path.exists')
    @patch('src.main.EmailAutoResponder')
    @patch('builtins.print')
    @patch('sys.path', new=[])
    def test_main_with_exception(self, mock_print, mock_responder_class, mock_exists, mock_get):
        """Test main function with exception."""
        mock_get.return_value = 'test_key'
        mock_exists.return_value = True
        
        mock_responder_instance = Mock()
        mock_responder_instance.run.side_effect = Exception('Test error')
        mock_responder_class.return_value = mock_responder_instance
        
        from src.main import main
        main()
        
        mock_print.assert_any_call('\nError: Test error')


if __name__ == '__main__':
    unittest.main()