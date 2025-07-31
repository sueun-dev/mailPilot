"""Tests for the Gmail client module."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import base64
import os

from src.gmail.client import GmailClient
from googleapiclient.errors import HttpError


class TestGmailClient(unittest.TestCase):
    """Test cases for GmailClient."""
    
    @patch('src.gmail.client.build')
    @patch('src.gmail.client.Credentials')
    @patch('os.path.exists')
    def setUp(self, mock_exists, mock_creds, mock_build):
        """Set up test fixtures."""
        mock_exists.return_value = True  # Credentials file exists
        self.mock_service = Mock()
        mock_build.return_value = self.mock_service
        
        mock_creds_instance = Mock()
        mock_creds_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_creds_instance
        
        self.client = GmailClient()
    
    def test_get_unread_messages(self):
        """Test getting unread messages."""
        mock_messages = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'}
            ]
        }
        
        self.mock_service.users().messages().list().execute.return_value = mock_messages
        
        mock_msg_details = {
            'id': 'msg1',
            'threadId': 'thread1',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'test@example.com'}
                ],
                'body': {'data': base64.urlsafe_b64encode(b'Test body').decode()}
            },
            'snippet': 'Test snippet'
        }
        
        self.mock_service.users().messages().get().execute.return_value = mock_msg_details
        
        messages = self.client.get_unread_messages()
        
        self.assertEqual(len(messages), 2)
        self.mock_service.users().messages().list.assert_called_with(
            userId='me', q='is:unread'
        )
    
    def test_extract_body_simple(self):
        """Test extracting body from simple payload."""
        payload = {
            'body': {
                'data': base64.urlsafe_b64encode(b'Simple body text').decode()
            }
        }
        
        body = self.client._extract_body(payload)
        self.assertEqual(body, 'Simple body text')
    
    def test_extract_body_multipart(self):
        """Test extracting body from multipart payload."""
        payload = {
            'parts': [
                {
                    'mimeType': 'text/html',
                    'body': {'data': base64.urlsafe_b64encode(b'HTML body').decode()}
                },
                {
                    'mimeType': 'text/plain',
                    'body': {'data': base64.urlsafe_b64encode(b'Plain text body').decode()}
                }
            ]
        }
        
        body = self.client._extract_body(payload)
        self.assertEqual(body, 'Plain text body')
    
    def test_send_message(self):
        """Test sending a message."""
        self.mock_service.users().messages().send().execute.return_value = {
            'id': 'sent_msg_id'
        }
        
        result = self.client.send_message(
            to='recipient@example.com',
            subject='Test Subject',
            body='Test body'
        )
        
        self.assertEqual(result['id'], 'sent_msg_id')
        self.mock_service.users().messages().send.assert_called()
    
    def test_send_message_with_thread_id(self):
        """Test sending a message with thread ID."""
        self.mock_service.users().messages().send().execute.return_value = {
            'id': 'sent_msg_id'
        }
        
        result = self.client.send_message(
            to='recipient@example.com',
            subject='Test Subject',
            body='Test body',
            thread_id='thread123'
        )
        
        self.assertEqual(result['id'], 'sent_msg_id')
        
        call_args = self.mock_service.users().messages().send.call_args
        self.assertEqual(call_args[1]['body']['threadId'], 'thread123')
    
    def test_mark_as_read(self):
        """Test marking a message as read."""
        self.mock_service.users().messages().modify().execute.return_value = {}
        
        result = self.client.mark_as_read('msg_id')
        
        self.assertTrue(result)
        self.mock_service.users().messages().modify.assert_called_with(
            userId='me',
            id='msg_id',
            body={'removeLabelIds': ['UNREAD']}
        )
    
    def test_get_thread_messages(self):
        """Test getting all messages in a thread."""
        mock_thread = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'}
            ]
        }
        
        self.mock_service.users().threads().get().execute.return_value = mock_thread
        
        mock_msg_details = {
            'id': 'msg1',
            'threadId': 'thread1',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'test@example.com'}
                ],
                'body': {'data': base64.urlsafe_b64encode(b'Test body').decode()}
            },
            'snippet': 'Test snippet'
        }
        
        self.mock_service.users().messages().get().execute.return_value = mock_msg_details
        
        messages = self.client.get_thread_messages('thread1')
        
        self.assertEqual(len(messages), 2)
        self.mock_service.users().threads().get.assert_called_with(
            userId='me', id='thread1'
        )
    
    def test_credentials_file_not_found(self):
        """Test error when credentials file is not found."""
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(FileNotFoundError) as context:
                GmailClient()
            
            self.assertIn("Credentials file not found", str(context.exception))
            self.assertIn("config/", str(context.exception))
    
    @patch('src.gmail.client.build')
    @patch('src.gmail.client.InstalledAppFlow')
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_authentication_new_user(self, mock_exists, mock_open, mock_flow, mock_build):
        """Test authentication for new user."""
        mock_exists.return_value = True  # Credentials file exists
        mock_creds = Mock()
        mock_creds.to_json.return_value = '{"token": "test"}'
        
        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        
        with patch('src.gmail.client.Credentials.from_authorized_user_file',
                   side_effect=FileNotFoundError):
            client = GmailClient()
        
        mock_flow.from_client_secrets_file.assert_called_once()
        mock_flow_instance.run_local_server.assert_called_once_with(port=0)
    
    def test_get_unread_messages_with_http_error(self):
        """Test get_unread_messages with HttpError."""
        error_resp = Mock()
        error_resp.status = 403
        error_resp.reason = 'Forbidden'
        http_error = HttpError(error_resp, b'Error content')
        
        # Reset the mock first
        self.mock_service.reset_mock()
        self.mock_service.users().messages().list().execute.side_effect = http_error
        
        messages = self.client.get_unread_messages()
        
        self.assertEqual(messages, [])
    
    def test_get_message_details_with_http_error(self):
        """Test _get_message_details with HttpError."""
        error_resp = Mock()
        error_resp.status = 404
        error_resp.reason = 'Not Found'
        http_error = HttpError(error_resp, b'Message not found')
        
        self.mock_service.users().messages().get().execute.side_effect = http_error
        
        # We need to test this through get_unread_messages
        mock_messages = {'messages': [{'id': 'msg1'}]}
        self.mock_service.users().messages().list().execute.return_value = mock_messages
        
        messages = self.client.get_unread_messages()
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], {})
    
    def test_send_message_with_http_error(self):
        """Test send_message with HttpError."""
        error_resp = Mock()
        error_resp.status = 500
        error_resp.reason = 'Internal Server Error'
        http_error = HttpError(error_resp, b'Server error')
        
        self.mock_service.reset_mock()
        self.mock_service.users().messages().send().execute.side_effect = http_error
        
        result = self.client.send_message('test@example.com', 'Subject', 'Body')
        
        self.assertEqual(result, {})
    
    def test_mark_as_read_with_http_error(self):
        """Test mark_as_read with HttpError."""
        error_resp = Mock()
        error_resp.status = 403
        error_resp.reason = 'Forbidden'
        http_error = HttpError(error_resp, b'Permission denied')
        
        self.mock_service.reset_mock()
        self.mock_service.users().messages().modify().execute.side_effect = http_error
        
        result = self.client.mark_as_read('msg123')
        
        self.assertFalse(result)
    
    def test_get_thread_messages_with_http_error(self):
        """Test get_thread_messages with HttpError."""
        error_resp = Mock()
        error_resp.status = 404
        error_resp.reason = 'Not Found'
        http_error = HttpError(error_resp, b'Thread not found')
        
        self.mock_service.reset_mock()
        self.mock_service.users().threads().get().execute.side_effect = http_error
        
        messages = self.client.get_thread_messages('thread123')
        
        self.assertEqual(messages, [])
    
    @patch('src.gmail.client.build')
    @patch('builtins.open', create=True)
    @patch('src.gmail.client.Credentials')
    @patch('src.gmail.client.Request')
    @patch('os.path.exists')
    def test_authentication_with_token_refresh(self, mock_exists, mock_request, mock_creds, mock_open, mock_build):
        """Test authentication with expired token that needs refresh."""
        mock_exists.return_value = True
        
        # Mock expired credentials that can be refreshed
        mock_creds_instance = Mock()
        mock_creds_instance.valid = False
        mock_creds_instance.expired = True
        mock_creds_instance.refresh_token = 'refresh_token'
        mock_creds_instance.to_json.return_value = '{"token": "refreshed"}'
        mock_creds.from_authorized_user_file.return_value = mock_creds_instance
        
        client = GmailClient()
        
        mock_creds_instance.refresh.assert_called_once()
    
    @patch('src.gmail.client.build')
    @patch('src.gmail.client.InstalledAppFlow')
    @patch('builtins.open', create=True)
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_authentication_creates_token_directory(self, mock_exists, mock_makedirs, mock_open, mock_flow, mock_build):
        """Test that authentication creates token directory if it doesn't exist."""
        def exists_side_effect(path):
            if path.endswith('credentials.json'):
                return True
            return False  # Token directory doesn't exist
        
        mock_exists.side_effect = exists_side_effect
        
        mock_creds = Mock()
        mock_creds.to_json.return_value = '{"token": "test"}'
        
        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        
        with patch('src.gmail.client.Credentials.from_authorized_user_file',
                   side_effect=FileNotFoundError):
            client = GmailClient()
        
        mock_makedirs.assert_called_once_with('data', exist_ok=True)


if __name__ == '__main__':
    unittest.main()