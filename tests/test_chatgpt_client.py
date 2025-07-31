"""Tests for the ChatGPT client module."""
import unittest
from unittest.mock import Mock, patch

from src.chatgpt.client import ChatGPTClient


class TestChatGPTClient(unittest.TestCase):
    """Test cases for ChatGPTClient."""
    
    @patch('src.chatgpt.client.OpenAI')
    def setUp(self, mock_openai):
        """Set up test fixtures."""
        self.mock_openai_instance = Mock()
        mock_openai.return_value = self.mock_openai_instance
        
        self.client = ChatGPTClient(api_key='test_key')
    
    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.client.model, 'gpt-4-turbo-preview')
        self.assertIsNotNone(self.client.system_prompt)
        self.assertIn('email assistant', self.client.system_prompt)
    
    def test_generate_response_without_context(self):
        """Test generating response without thread context."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Generated response'))]
        
        self.mock_openai_instance.chat.completions.create.return_value = mock_response
        
        response = self.client.generate_response('Customer message')
        
        self.assertEqual(response, 'Generated response')
        
        call_args = self.mock_openai_instance.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[1]['role'], 'user')
        self.assertIn('Customer message', messages[1]['content'])
        self.assertNotIn('Conversation History', messages[1]['content'])
    
    def test_generate_response_with_context(self):
        """Test generating response with thread context."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Generated response with context'))]
        
        self.mock_openai_instance.chat.completions.create.return_value = mock_response
        
        response = self.client.generate_response(
            'Customer message',
            thread_context='Previous conversation'
        )
        
        self.assertEqual(response, 'Generated response with context')
        
        call_args = self.mock_openai_instance.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        self.assertEqual(len(messages), 2)
        self.assertIn('Customer message', messages[1]['content'])
        self.assertIn('Conversation History', messages[1]['content'])
        self.assertIn('Previous conversation', messages[1]['content'])
    
    def test_generate_response_error_handling(self):
        """Test error handling in generate_response."""
        self.mock_openai_instance.chat.completions.create.side_effect = Exception('API Error')
        
        response = self.client.generate_response('Customer message')
        
        self.assertEqual(response, '')
    
    def test_check_zoom_mention_positive(self):
        """Test checking for Zoom mention with positive cases."""
        test_cases = [
            'Zoom meeting scheduled for tomorrow',
            'The zoom meeting is confirmed',
            'I have scheduled our Zoom call',
            'Meeting is confirmed for 3 PM',
            'See you on Zoom!',
            'ZOOM MEETING CONFIRMED'
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                self.assertTrue(self.client.check_zoom_mention(text))
    
    def test_check_zoom_mention_negative(self):
        """Test checking for Zoom mention with negative cases."""
        test_cases = [
            'Let me schedule a meeting',
            'Can we have a zoom call?',
            'I would like to set up a meeting',
            'Zoom would be great',
            'Please confirm the meeting time'
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                self.assertFalse(self.client.check_zoom_mention(text))
    
    def test_model_parameters(self):
        """Test that correct model parameters are used."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Response'))]
        
        self.mock_openai_instance.chat.completions.create.return_value = mock_response
        
        self.client.generate_response('Test message')
        
        call_args = self.mock_openai_instance.chat.completions.create.call_args
        
        self.assertEqual(call_args[1]['model'], 'gpt-4-turbo-preview')
        self.assertEqual(call_args[1]['temperature'], 0.7)
        self.assertEqual(call_args[1]['max_tokens'], 500)
    
    @patch('src.chatgpt.client.OpenAI')
    def test_custom_model(self, mock_openai):
        """Test using custom model."""
        mock_openai_instance = Mock()
        mock_openai.return_value = mock_openai_instance
        
        client = ChatGPTClient(api_key='test_key', model='gpt-3.5-turbo')
        
        self.assertEqual(client.model, 'gpt-3.5-turbo')


if __name__ == '__main__':
    unittest.main()