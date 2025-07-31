"""Main orchestrator for the email auto-response system."""
import sys
import os
import time
import json
import locale
import io
import random
from typing import Set
from datetime import datetime, timedelta

# No longer needed - using environment variables instead of keychain

# Import app configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.app_config import (
    LAST_PROCESSED_FILE, GMAIL_QUERY, MENU_SLEEP_DELAY,
    PREFERRED_LOCALES, FIRST_RUN_MESSAGE_LIMIT, CUSTOMER_LIST_FILE,
    MIN_RESPONSE_DELAY, MAX_RESPONSE_DELAY, THREAD_EXPIRATION_DAYS,
    MAX_RETRIES, RETRY_DELAY
)

from gmail.client import GmailClient
from chatgpt.client import ChatGPTClient
from storage.thread_memory import ThreadMemory
from approval.interface import ApprovalInterface
from marketing.outbound import OutboundMarketing
from utils.logging_config import get_logger

# Set Python default encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set locale to UTF-8
try:
    locale.setlocale(locale.LC_ALL, PREFERRED_LOCALES[0])
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, PREFERRED_LOCALES[1] if len(PREFERRED_LOCALES) > 1 else 'C.UTF-8')
    except locale.Error:
        pass  # Use system default

# Module logger
logger = get_logger(__name__)


class EmailAutoResponder:
    """Main orchestrator for the email auto-response system."""
    
    def __init__(self, gmail_creds: str, openai_api_key: str):
        """Initialize the auto-responder."""
        self.gmail = GmailClient(credentials_file=gmail_creds)
        self.chatgpt = ChatGPTClient(api_key=openai_api_key)
        self.memory = ThreadMemory()
        self.ui = ApprovalInterface()
        self.marketing = OutboundMarketing()
        
        # 고객 이메일 목록 로드
        self.customer_emails = self._load_customer_emails()
        
        # 마지막 처리 상태 로드
        self.last_processed = self._load_last_processed()
        
    def _load_customer_emails(self) -> Set[str]:
        """고객 이메일 목록을 파일에서 로드합니다."""
        customer_file = CUSTOMER_LIST_FILE
        emails = set()
        
        if os.path.exists(customer_file):
            try:
                with open(customer_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            emails.add(line.lower())
                logger.info(f"Loaded {len(emails)} customer email addresses")
            except Exception as e:
                logger.error(f"Failed to load customer emails: {e}")
        else:
            logger.warning(f"Customer email file not found: {customer_file}")
            
        return emails
    
    def _load_last_processed(self) -> dict:
        """마지막 처리 상태를 로드합니다."""
        state_file = LAST_PROCESSED_FILE
        default_state = {
            "last_message_id": None,
            "last_history_id": None,
            "last_check_time": None,
            "first_run": True
        }
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                logger.info(f"Loaded last processed state: {state}")
                return state
            except Exception as e:
                logger.error(f"Failed to load last processed state: {e}")
                
        return default_state
    
    def _save_last_processed(self):
        """현재 처리 상태를 저장합니다."""
        state_file = LAST_PROCESSED_FILE
        try:
            with open(state_file, 'w') as f:
                json.dump(self.last_processed, f, indent=2)
            logger.debug("Saved last processed state")
        except Exception as e:
            logger.error(f"Failed to save last processed state: {e}")
    
    def _is_customer_email(self, email: str) -> bool:
        """이메일이 고객 목록에 있는지 확인합니다."""
        # 이메일에서 주소 부분만 추출 (예: "John Doe <john@example.com>" -> "john@example.com")
        import re
        email_match = re.search(r'<(.+?)>', email)
        if email_match:
            email_address = email_match.group(1).lower()
        else:
            email_address = email.lower()
            
        return email_address in self.customer_emails
    
    def process_email(self, message: dict) -> bool:
        """Process a single email message."""
        thread_id = message['thread_id']
        
        # Check if thread is expired
        if self.memory.is_thread_expired(thread_id):
            self.ui.display_message(
                f"Thread {thread_id[:8]} is expired (>30 days old), skipping...", 
                "warning"
            )
            self.memory.mark_thread_as_expired(thread_id)
            return False
        
        # Check if Zoom is already scheduled
        if self.memory.is_zoom_scheduled(thread_id):
            self.ui.display_message(
                f"Zoom already scheduled for thread {thread_id[:8]}...", 
                "warning"
            )
            return False
        
        # 마케팅 스레드가 아닌 경우에만 처리 (새로운 대화만 처리)
        # 마케팅 스레드의 경우, 내가 먼저 보낸 것이므로 고객 답장을 처리해야 함
        last_sender = self.memory.get_last_sender(thread_id)
        is_marketing_thread = self.memory.is_marketing_thread(thread_id)
        
        # 디버그 로그
        logger.debug(f"Thread {thread_id[:8]}: last_sender={last_sender}, is_marketing={is_marketing_thread}, current_sender={message['sender']}")
        
        # 이미 내가 마지막으로 보낸 경우 스킵 (마케팅 스레드든 아니든)
        if last_sender == 'You':
            self.ui.display_message(
                f"Waiting for customer response in thread {thread_id[:8]}...", 
                "info"
            )
            return False
        
        # Store the incoming message
        self.memory.add_message(thread_id, message)
        
        # Get thread context
        context = self.memory.get_thread_context(thread_id)
        
        # Generate response
        self.ui.display_message("Generating response...", "info")
        response_body = self.chatgpt.generate_response(
            customer_message=message['body'],
            thread_context=context
        )
        
        if not response_body:
            self.ui.display_message("Failed to generate response", "error")
            return False
        
        # Prepare draft for approval
        draft = {
            'to': message['sender'],
            'subject': f"Re: {message['subject']}",
            'body': response_body,
            'thread_id': thread_id,
            'context': context
        }
        
        # Get approval
        approved = self.ui.display_draft(draft)
        
        if approved:
            # Add realistic response delay
            delay = random.randint(MIN_RESPONSE_DELAY, MAX_RESPONSE_DELAY)
            self.ui.display_message(f"Waiting {delay} seconds before sending (more human-like)...", "info")
            time.sleep(delay)
            
            # Send the email with retry logic
            result = None
            for attempt in range(MAX_RETRIES):
                try:
                    result = self.gmail.send_message(
                        to=draft['to'],
                        subject=draft['subject'],
                        body=draft['body'],
                        thread_id=thread_id
                    )
                    if result:
                        break
                except Exception as e:
                    logger.error(f"Send attempt {attempt + 1} failed: {e}")
                    if attempt < MAX_RETRIES - 1:
                        self.ui.display_message(f"Send failed, retrying in {RETRY_DELAY} seconds...", "warning")
                        time.sleep(RETRY_DELAY)
            
            if result:
                # Store the sent message
                self.memory.add_message(thread_id, {
                    'sender': 'You',
                    'subject': draft['subject'],
                    'body': draft['body'],
                    'id': result.get('id', ''),
                    'is_draft': False
                })
                
                # Mark original as read
                self.gmail.mark_as_read(message['id'])
                
                # Check if Zoom was mentioned
                if self.chatgpt.check_zoom_mention(response_body):
                    self.memory.mark_zoom_scheduled(thread_id)
                    self.ui.display_message(
                        "Zoom meeting mentioned - thread marked as complete", 
                        "success"
                    )
                
                self.ui.display_message("Email sent successfully!", "success")
                return True
            else:
                self.ui.display_message("Failed to send email", "error")
                return False
        else:
            self.ui.display_message("Email draft rejected", "warning")
            return False
    
    def check_new_emails(self):
        """Check for new unread emails."""
        self.ui.display_message("Checking for new emails...", "info")
        
        # 먼저 만료된 스레드 정리
        expired_count = self.memory.cleanup_expired_threads()
        if expired_count > 0:
            self.ui.display_message(f"Cleaned up {expired_count} expired threads", "info")
        
        # 고객 이메일이 없으면 경고
        if not self.customer_emails:
            self.ui.display_message(
                "\n⚠️  No customer emails configured!\n"
                f"Please add customer email addresses to: {CUSTOMER_LIST_FILE}\n"
                "Example:\n"
                "  customer1@example.com\n"
                "  customer2@company.com",
                "warning"
            )
            return
        
        # Gmail 쿼리 구성
        query = GMAIL_QUERY
        
        # 처음 실행이 아니면 마지막 메시지 이후만 가져오기
        if not self.last_processed['first_run'] and self.last_processed['last_check_time']:
            # after: 쿼리 사용
            query += f" after:{self.last_processed['last_check_time']}"
        
        # 첫 실행 시에는 10개만 가져오기
        max_results = 10 if self.last_processed['first_run'] else None
        messages = self.gmail.get_unread_messages(query=query, max_results=max_results)
        
        if not messages:
            self.ui.display_message("No new emails found", "info")
            return
        
        # 고객 이메일만 필터링하고 스레드별로 최신 메시지만 보관
        customer_messages = []
        skipped_count = 0
        seen_threads = set()  # 이미 본 스레드 추적
        
        for message in messages:
            sender = message.get('sender', '')
            thread_id = message.get('thread_id', '')
            
            if self._is_customer_email(sender):
                # 같은 스레드의 메시지가 이미 있으면 스킵
                if thread_id not in seen_threads:
                    customer_messages.append(message)
                    seen_threads.add(thread_id)
                else:
                    logger.debug(f"Skipping duplicate message in thread {thread_id[:8]}...")
            else:
                skipped_count += 1
        
        if not customer_messages:
            self.ui.display_message(
                f"Found {len(messages)} email(s), but none from customers (skipped {skipped_count} non-customer emails)",
                "info"
            )
            return
        
        # 메시지 표시
        if self.last_processed['first_run']:
            self.ui.display_message(
                f"First run: Processing {len(customer_messages)} customer email(s) (limited to 10 total emails from Gmail)",
                "info"
            )
        else:
            self.ui.display_message(
                f"Found {len(customer_messages)} new customer email(s)",
                "success"
            )
        
        messages_to_process = customer_messages
        
        # 메시지 처리
        processed_count = 0
        for message in messages_to_process:
            self.ui.display_message(f"\n--- Processing email from {message['sender']} ---", "info")
            
            if self.process_email(message):
                processed_count += 1
                # 마지막 처리 메시지 업데이트
                self.last_processed['last_message_id'] = message['id']
        
        # 상태 업데이트 및 저장
        if processed_count > 0:
            self.last_processed['first_run'] = False
            self.last_processed['last_check_time'] = int(time.time())
            self._save_last_processed()
            
        self.ui.display_message(
            f"\nProcessed {processed_count} customer email(s)",
            "success"
        )
    
    def view_active_threads(self):
        """View all active threads."""
        active_threads = self.memory.get_active_threads()
        
        if not active_threads:
            self.ui.display_message("No active threads", "info")
            return
        
        self.ui.display_message(f"\n[bold]Active Threads ({len(active_threads)}):[/bold]", "info")
        
        for thread_id in active_threads:
            summary = self.memory.get_thread_summary(thread_id)
            if summary:
                self.ui.display_thread_summary(summary)
    
    def send_marketing_emails(self):
        """Send marketing emails to all customers who haven't received them yet."""
        logger.info("\n🚀 Starting Marketing Campaign...")
        
        # Parse customer list with names
        customers = self.marketing.parse_customer_list(CUSTOMER_LIST_FILE)
        
        if not customers:
            logger.warning("No customers found in customer_emails.txt")
            return
        
        # Get unsent customers
        unsent = self.marketing.get_unsent_customers(customers)
        
        if not unsent:
            logger.info("All customers have already received the marketing email!")
            return
        
        logger.info(f"Found {len(unsent)} customers to send marketing emails to")
        
        # Send to each customer
        sent_count = 0
        for name, email in unsent:
            logger.info(f"\n--- Preparing email for {name} ({email}) ---")
            
            # Generate personalized email
            email_content = self.marketing.generate_marketing_email(name)
            
            # Prepare draft for approval
            draft = {
                'to': f"{name} <{email}>",
                'subject': email_content['subject'],
                'body': email_content['body'],
                'thread_id': None,
                'context': None
            }
            
            # Get approval
            approved = self.ui.display_draft(draft)
            
            if approved:
                # Send the email
                result = self.gmail.send_message(
                    to=draft['to'],
                    subject=draft['subject'],
                    body=draft['body']
                )
                
                if result:
                    self.marketing.mark_as_sent(email)
                    sent_count += 1
                    logger.info(f"Marketing email sent to {name}!")
                    
                    # Store in thread memory for tracking responses
                    if 'id' in result:
                        thread_id = result.get('threadId', '')
                        self.memory.add_message(thread_id, {
                            'sender': 'You',
                            'subject': draft['subject'],
                            'body': draft['body'],
                            'id': result['id'],
                            'is_draft': False
                        })
                        # 마케팅 스레드로 표시
                        self.memory.mark_as_marketing_thread(thread_id)
                else:
                    logger.error(f"Failed to send email to {name}")
            else:
                logger.warning(f"Email to {name} was rejected")
        
        logger.info(f"\n✅ Marketing campaign complete! Sent {sent_count} emails.")
    
    def run(self):
        """Run the main application loop."""
        logger.info("\n🤖 Email Marketing & Auto-Responder System\n")
        
        while True:
            choice = self.ui.prompt_action()
            
            if choice == "1":
                self.send_marketing_emails()
            elif choice == "2":
                self.check_new_emails()
            elif choice == "3":
                self.view_active_threads()
            elif choice == "4":
                logger.info("\nGoodbye! 👋")
                break
            
            time.sleep(MENU_SLEEP_DELAY)


def main():
    # Get API key from environment variables
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        logger.critical("OPENAI_API_KEY not found in environment variables")
        return
    
    # Check for Gmail credentials
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'credentials.json')
    if not os.path.exists(config_path):
        logger.error("Gmail credentials file not found", extra={"expected_path": config_path})
        return
    
    # Start the auto-responder
    responder = EmailAutoResponder(
        gmail_creds=config_path,
        openai_api_key=openai_api_key
    )
    
    try:
        responder.run()
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
