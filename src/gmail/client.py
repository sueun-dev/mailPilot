"""Gmail API client for email operations."""
import base64
import os
import json
from email.mime.text import MIMEText
from typing import List, Dict, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.logging_config import get_logger

# Import app configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.app_config import (
    GMAIL_SCOPES, CREDENTIALS_FILE, TOKEN_FILE, OAUTH_PORT
)

# Module logger
logger = get_logger(__name__)


class GmailClient:
    """Gmail API client for email operations."""
    
    def __init__(self, credentials_file: str = CREDENTIALS_FILE, token_file: str = TOKEN_FILE):
        """Initialize Gmail client."""
        self.credentials_file = credentials_file
        self.token_file = token_file
        
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
            )
        
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate and return Gmail service."""
        # Try to load existing token
        try:
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        except:
            creds = None
        
        # Check if credentials need refresh or new authentication
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, GMAIL_SCOPES)
                creds = flow.run_local_server(port=OAUTH_PORT)
            
            # Save the token
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def get_unread_messages(self, query: str = None, max_results: Optional[int] = None) -> List[Dict]:
        """Get unread messages from inbox."""
        try:
            # Gmail API 요청 파라미터 설정
            if query is None:
                query = GMAIL_QUERY
            params = {
                'userId': 'me',
                'q': query
            }
            
            # max_results가 지정되면 추가
            if max_results:
                params['maxResults'] = max_results
            
            results = self.service.users().messages().list(**params).execute()
            
            messages = results.get('messages', [])
            return [self._get_message_details(msg['id']) for msg in messages]
            
        except HttpError as error:
            logger.error(f'Failed to get unread messages: {error}', exc_info=True)
            return []
    
    def _get_message_details(self, msg_id: str) -> Dict:
        """Get full message details."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id
            ).execute()
            
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            thread_id = message.get('threadId', '')
            
            body = self._extract_body(message['payload'])
            
            return {
                'id': msg_id,
                'thread_id': thread_id,
                'subject': subject,
                'sender': sender,
                'body': body,
                'snippet': message.get('snippet', '')
            }
            
        except HttpError as error:
            logger.error(f'Failed to get message details: {error}', exc_info=True, extra={'msg_id': msg_id})
            return {}
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def send_message(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> Dict:
        """Send an email message."""
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        
        if thread_id:
            raw_message['threadId'] = thread_id
        
        try:
            sent_message = self.service.users().messages().send(
                userId='me',
                body=raw_message
            ).execute()
            return sent_message
        except HttpError as error:
            logger.error(f'Failed to send message: {error}', exc_info=True, extra={'to': to, 'thread_id': thread_id})
            return {}
    
    def mark_as_read(self, msg_id: str) -> bool:
        """Mark a message as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            logger.error(f'Failed to mark message as read: {error}', exc_info=True, extra={'msg_id': msg_id})
            return False
    
    def get_thread_messages(self, thread_id: str) -> List[Dict]:
        """Get all messages in a thread."""
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = []
            for msg in thread.get('messages', []):
                messages.append(self._get_message_details(msg['id']))
            
            return messages
        except HttpError as error:
            logger.error(f'Failed to get thread messages: {error}', exc_info=True, extra={'thread_id': thread_id})
            return []