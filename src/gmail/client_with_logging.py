"""Gmail API client for email operations with comprehensive logging.

This is an example of the gmail/client.py module fully migrated to use
the new logging system instead of print statements.
"""
import base64
import os
from email.mime.text import MIMEText
from typing import List, Dict, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.logging_config import get_logger, LogPerformance

# Module logger
logger = get_logger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']


class GmailClient:
    """Gmail API client for email operations."""
    
    def __init__(self, credentials_file: str = 'config/credentials.json', token_file: str = 'data/token.json'):
        """Initialize Gmail client."""
        logger.info("Initializing Gmail client", extra={
            "credentials_file": credentials_file,
            "token_file": token_file
        })
        
        self.credentials_file = credentials_file
        self.token_file = token_file
        
        if not os.path.exists(self.credentials_file):
            logger.error("Credentials file not found", extra={
                "path": self.credentials_file
            })
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
                "Please add credentials.json to the config/ folder.\n"
                "See config/HOW_TO_GET_CREDENTIALS.md for instructions."
            )
        
        self.service = self._authenticate()
        logger.info("Gmail client initialized successfully")
    
    def _authenticate(self):
        """Authenticate and return Gmail service."""
        logger.debug("Starting Gmail authentication")
        creds = None
        
        # Try to load existing token
        try:
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            logger.debug("Loaded existing token")
        except FileNotFoundError:
            logger.info(f"No token found. Will authenticate with Google.")
        except Exception as e:
            logger.warning(f"Error loading token: {e}", exc_info=True)
        
        # Check if credentials are valid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                try:
                    creds.refresh(Request())
                    logger.info("Credentials refreshed successfully")
                except Exception as e:
                    logger.error("Failed to refresh credentials", exc_info=True)
                    creds = None
            
            if not creds:
                logger.info("Starting OAuth2 flow for new authentication")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                logger.info("OAuth2 authentication completed")
            
            # Ensure data directory exists before saving token
            token_dir = os.path.dirname(self.token_file)
            if token_dir and not os.path.exists(token_dir):
                logger.debug(f"Creating token directory: {token_dir}")
                os.makedirs(token_dir, exist_ok=True)
            
            # Save the token for next run
            logger.info("Saving authentication token")
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                logger.info("Authentication token saved successfully")
            except IOError as e:
                logger.error("Failed to save authentication token", exc_info=True)
        
        # Build and return the service
        logger.debug("Building Gmail service")
        service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail service built successfully")
        return service
    
    def get_unread_messages(self, query: str = 'is:unread') -> List[Dict]:
        """Get unread messages from inbox."""
        logger.info("Fetching unread messages", extra={"query": query})
        
        with LogPerformance(logger, "Gmail API list messages"):
            try:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query
                ).execute()
                
                messages = results.get('messages', [])
                logger.info(f"Found {len(messages)} unread messages")
                
                # Get details for each message
                detailed_messages = []
                for msg in messages:
                    details = self._get_message_details(msg['id'])
                    if details:
                        detailed_messages.append(details)
                
                logger.info(f"Successfully retrieved {len(detailed_messages)} message details")
                return detailed_messages
                
            except HttpError as error:
                logger.error("Failed to fetch unread messages", exc_info=True, extra={
                    "query": query,
                    "error_code": error.resp.status if hasattr(error, 'resp') else None,
                    "error_reason": error.error_details if hasattr(error, 'error_details') else None
                })
                return []
            except Exception as e:
                logger.error("Unexpected error fetching messages", exc_info=True)
                return []
    
    def _get_message_details(self, msg_id: str) -> Dict:
        """Get full message details."""
        logger.debug(f"Fetching details for message: {msg_id}")
        
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
            
            result = {
                'id': msg_id,
                'thread_id': thread_id,
                'subject': subject,
                'sender': sender,
                'body': body,
                'snippet': message.get('snippet', '')
            }
            
            logger.debug("Successfully retrieved message details", extra={
                "msg_id": msg_id,
                "thread_id": thread_id,
                "subject_length": len(subject),
                "body_length": len(body)
            })
            
            return result
            
        except HttpError as error:
            logger.error(f"Failed to get message details for {msg_id}", exc_info=True, extra={
                "msg_id": msg_id,
                "error_code": error.resp.status if hasattr(error, 'resp') else None
            })
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting message details", exc_info=True, extra={
                "msg_id": msg_id
            })
            return {}
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        logger.debug("Extracting email body from payload")
        body = ''
        
        try:
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
            elif payload['body'].get('data'):
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            
            logger.debug(f"Extracted body of length {len(body)}")
            return body
            
        except Exception as e:
            logger.error("Failed to extract email body", exc_info=True)
            return ''
    
    def send_message(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> Dict:
        """Send an email message."""
        logger.info("Sending email", extra={
            "to": to,  # This will be sanitized by the logging filter
            "subject_length": len(subject),
            "body_length": len(body),
            "thread_id": thread_id or "new_thread"
        })
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        
        if thread_id:
            raw_message['threadId'] = thread_id
        
        with LogPerformance(logger, "Gmail API send message"):
            try:
                sent_message = self.service.users().messages().send(
                    userId='me',
                    body=raw_message
                ).execute()
                
                logger.info("Email sent successfully", extra={
                    "message_id": sent_message.get('id'),
                    "thread_id": sent_message.get('threadId')
                })
                return sent_message
                
            except HttpError as error:
                logger.error("Failed to send email", exc_info=True, extra={
                    "to": to,  # Will be sanitized
                    "thread_id": thread_id,
                    "error_code": error.resp.status if hasattr(error, 'resp') else None
                })
                return {}
            except Exception as e:
                logger.error("Unexpected error sending email", exc_info=True)
                return {}
    
    def mark_as_read(self, msg_id: str) -> bool:
        """Mark a message as read."""
        logger.debug(f"Marking message as read: {msg_id}")
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logger.info(f"Message marked as read: {msg_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Failed to mark message as read", exc_info=True, extra={
                "msg_id": msg_id,
                "error_code": error.resp.status if hasattr(error, 'resp') else None
            })
            return False
        except Exception as e:
            logger.error(f"Unexpected error marking message as read", exc_info=True, extra={
                "msg_id": msg_id
            })
            return False
    
    def get_thread_messages(self, thread_id: str) -> List[Dict]:
        """Get all messages in a thread."""
        logger.info(f"Fetching thread messages", extra={"thread_id": thread_id})
        
        with LogPerformance(logger, f"Gmail API get thread {thread_id}"):
            try:
                thread = self.service.users().threads().get(
                    userId='me',
                    id=thread_id
                ).execute()
                
                messages = []
                message_count = len(thread.get('messages', []))
                logger.debug(f"Thread contains {message_count} messages")
                
                for msg in thread.get('messages', []):
                    details = self._get_message_details(msg['id'])
                    if details:
                        messages.append(details)
                
                logger.info(f"Successfully retrieved {len(messages)} messages from thread", extra={
                    "thread_id": thread_id,
                    "message_count": len(messages)
                })
                return messages
                
            except HttpError as error:
                logger.error(f"Failed to get thread messages", exc_info=True, extra={
                    "thread_id": thread_id,
                    "error_code": error.resp.status if hasattr(error, 'resp') else None
                })
                return []
            except Exception as e:
                logger.error(f"Unexpected error getting thread messages", exc_info=True, extra={
                    "thread_id": thread_id
                })
                return []