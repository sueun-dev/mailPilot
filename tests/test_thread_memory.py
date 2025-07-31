"""Tests for the thread memory module."""
import unittest
from datetime import datetime
from unittest.mock import patch, mock_open, Mock

from src.storage.thread_memory import ThreadMemory


class TestThreadMemory(unittest.TestCase):
    """Test cases for ThreadMemory."""
    
    @patch('os.path.exists')
    def setUp(self, mock_exists):
        """Set up test fixtures."""
        mock_exists.return_value = False
        self.memory = ThreadMemory('data/test_memory.json')
    
    def test_init(self):
        """Test memory initialization."""
        self.assertIsInstance(self.memory.threads, dict)
        self.assertEqual(len(self.memory.threads), 0)
        self.assertEqual(self.memory.storage_file, 'data/test_memory.json')
    
    @patch('builtins.open', new_callable=mock_open)
    def test_add_message(self, mock_file):
        """Test adding a message to thread memory."""
        message = {
            'id': 'msg1',
            'sender': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        
        self.memory.add_message('thread1', message)
        
        self.assertIn('thread1', self.memory.threads)
        self.assertEqual(len(self.memory.threads['thread1']['messages']), 1)
        self.assertEqual(self.memory.threads['thread1']['messages'][0]['sender'], 'test@example.com')
        self.assertEqual(self.memory.threads['thread1']['messages'][0]['body'], 'Test body')
        self.assertFalse(self.memory.threads['thread1']['zoom_scheduled'])
        mock_file.assert_called()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_add_multiple_messages(self, mock_file):
        """Test adding multiple messages to same thread."""
        message1 = {'id': 'msg1', 'body': 'First message'}
        message2 = {'id': 'msg2', 'body': 'Second message'}
        
        self.memory.add_message('thread1', message1)
        self.memory.add_message('thread1', message2)
        
        self.assertEqual(len(self.memory.threads['thread1']['messages']), 2)
        self.assertEqual(self.memory.threads['thread1']['messages'][0]['body'], 'First message')
        self.assertEqual(self.memory.threads['thread1']['messages'][1]['body'], 'Second message')
    
    @patch('builtins.open', new_callable=mock_open)
    def test_get_thread_context(self, mock_file):
        """Test getting thread context."""
        message1 = {
            'sender': 'customer@example.com',
            'body': 'I need help with my order'
        }
        message2 = {
            'sender': 'You',
            'body': 'I can help you with that'
        }
        
        self.memory.add_message('thread1', message1)
        self.memory.add_message('thread1', message2)
        
        context = self.memory.get_thread_context('thread1')
        
        self.assertIn('Customer', context)
        self.assertIn('I need help with my order', context)
        self.assertIn('You', context)
        self.assertIn('I can help you with that', context)
    
    def test_get_thread_context_nonexistent(self):
        """Test getting context for nonexistent thread."""
        context = self.memory.get_thread_context('nonexistent')
        self.assertIsNone(context)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_is_zoom_scheduled(self, mock_file):
        """Test checking if Zoom is scheduled."""
        self.memory.add_message('thread1', {'body': 'Test'})
        self.memory.add_message('thread2', {'body': 'Test'})
        
        self.memory.mark_zoom_scheduled('thread1')
        
        self.assertTrue(self.memory.is_zoom_scheduled('thread1'))
        self.assertFalse(self.memory.is_zoom_scheduled('thread2'))
        self.assertFalse(self.memory.is_zoom_scheduled('nonexistent'))
    
    @patch('builtins.open', new_callable=mock_open)
    def test_mark_zoom_scheduled(self, mock_file):
        """Test marking Zoom as scheduled."""
        self.memory.add_message('thread1', {'body': 'Test'})
        
        self.memory.mark_zoom_scheduled('thread1')
        
        self.assertTrue(self.memory.threads['thread1']['zoom_scheduled'])
    
    @patch('builtins.open', new_callable=mock_open)
    def test_get_active_threads(self, mock_file):
        """Test getting active threads."""
        self.memory.add_message('thread1', {'body': 'Test'})
        self.memory.add_message('thread2', {'body': 'Test'})
        self.memory.add_message('thread3', {'body': 'Test'})
        
        self.memory.mark_zoom_scheduled('thread2')
        
        active_threads = self.memory.get_active_threads()
        
        self.assertEqual(len(active_threads), 2)
        self.assertIn('thread1', active_threads)
        self.assertIn('thread3', active_threads)
        self.assertNotIn('thread2', active_threads)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_get_thread_summary(self, mock_file):
        """Test getting thread summary."""
        message1 = {
            'sender': 'customer@example.com',
            'subject': 'Order Issue',
            'body': 'I have a problem with my order'
        }
        message2 = {
            'sender': 'You',
            'subject': 'Re: Order Issue',
            'body': 'I can help you with that'
        }
        
        self.memory.add_message('thread1', message1)
        self.memory.add_message('thread1', message2)
        
        summary = self.memory.get_thread_summary('thread1')
        
        self.assertEqual(summary['thread_id'], 'thread1')
        self.assertEqual(summary['customer_email'], 'customer@example.com')
        self.assertEqual(summary['message_count'], 2)
        self.assertFalse(summary['zoom_scheduled'])
        self.assertIn('created_at', summary)
    
    def test_get_thread_summary_nonexistent(self):
        """Test getting summary for nonexistent thread."""
        summary = self.memory.get_thread_summary('nonexistent')
        self.assertIsNone(summary)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_thread_timestamps(self, mock_file):
        """Test that timestamps are properly set."""
        with patch('src.storage.thread_memory.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_now_instance = Mock()
            mock_now_instance.isoformat.return_value = '2024-01-01T12:00:00'
            mock_datetime.now.return_value = mock_now_instance
            
            self.memory.add_message('thread1', {'body': 'Test'})
            
            self.assertIn('created_at', self.memory.threads['thread1'])
            self.assertEqual(len(self.memory.threads['thread1']['messages']), 1)
    
    def test_empty_thread_context(self):
        """Test getting context for thread with no messages."""
        self.memory.threads['thread1'] = {
            'messages': [],
            'zoom_scheduled': False,
            'created_at': datetime.now().isoformat()
        }
        
        context = self.memory.get_thread_context('thread1')
        self.assertEqual(context, '')


if __name__ == '__main__':
    unittest.main()