"""Thread memory storage for maintaining conversation context."""
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from utils.logging_config import get_logger

# Import app configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.app_config import THREAD_MEMORY_FILE, THREAD_EXPIRATION_DAYS

logger = get_logger(__name__)


class ThreadMemory:
    """Manages conversation thread storage and retrieval."""
    
    def __init__(self, storage_file: str = THREAD_MEMORY_FILE):
        """Initialize thread memory storage."""
        self.storage_file = storage_file
        
        # Ensure data directory exists
        data_dir = os.path.dirname(self.storage_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        
        self.threads = self._load_threads()
    
    def _load_threads(self) -> Dict:
        """Load threads from storage file."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_threads(self):
        """Save threads to storage file."""
        with open(self.storage_file, 'w') as f:
            json.dump(self.threads, f, indent=2)
    
    def add_message(self, thread_id: str, message: Dict):
        """Add a message to a thread."""
        if thread_id not in self.threads:
            self.threads[thread_id] = {
                'created_at': datetime.now().isoformat(),
                'messages': [],
                'customer_email': message.get('sender', ''),
                'zoom_scheduled': False,
                'is_marketing_thread': False,  # 마케팅 이메일로 시작된 스레드인지
                'last_sender': None  # 마지막 발신자 추적
            }
        
        self.threads[thread_id]['messages'].append({
            'timestamp': datetime.now().isoformat(),
            'sender': message.get('sender', ''),
            'subject': message.get('subject', ''),
            'body': message.get('body', ''),
            'message_id': message.get('id', ''),
            'is_draft': message.get('is_draft', False)
        })
        
        # 마지막 발신자 업데이트
        self.threads[thread_id]['last_sender'] = message.get('sender', '')
        
        self._save_threads()
    
    def get_thread_context(self, thread_id: str) -> Optional[str]:
        """Get formatted thread context for GPT."""
        if thread_id not in self.threads:
            return None
        
        thread = self.threads[thread_id]
        context_parts = []
        
        for msg in thread['messages']:
            if not msg.get('is_draft'):
                sender_type = "Customer" if msg['sender'] != 'You' else "You"
                # 타임스탬프를 더 간단한 형식으로 변환
                timestamp = datetime.fromisoformat(msg['timestamp'])
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
                
                # 제목과 본문을 포함
                context_text = f"{sender_type} ({formatted_time}):\n"
                if msg.get('subject'):
                    context_text += f"Subject: {msg['subject']}\n"
                context_text += f"{msg['body']}\n"
                
                context_parts.append(context_text)
        
        return "\n---\n".join(context_parts)
    
    def mark_zoom_scheduled(self, thread_id: str):
        """Mark that a Zoom meeting has been scheduled for this thread."""
        if thread_id in self.threads:
            self.threads[thread_id]['zoom_scheduled'] = True
            self._save_threads()
    
    def is_zoom_scheduled(self, thread_id: str) -> bool:
        """Check if Zoom meeting is already scheduled for this thread."""
        return self.threads.get(thread_id, {}).get('zoom_scheduled', False)
    
    def get_active_threads(self) -> List[str]:
        """Get list of thread IDs without scheduled Zoom meetings and not expired."""
        return [
            thread_id 
            for thread_id, thread in self.threads.items() 
            if not thread.get('zoom_scheduled', False) 
            and not thread.get('is_expired', False)
        ]
    
    def mark_as_marketing_thread(self, thread_id: str):
        """Mark a thread as started by marketing email."""
        if thread_id in self.threads:
            self.threads[thread_id]['is_marketing_thread'] = True
            self._save_threads()
    
    def is_marketing_thread(self, thread_id: str) -> bool:
        """Check if thread was started by marketing email."""
        return self.threads.get(thread_id, {}).get('is_marketing_thread', False)
    
    def get_last_sender(self, thread_id: str) -> Optional[str]:
        """Get the last sender in a thread."""
        return self.threads.get(thread_id, {}).get('last_sender')
    
    def get_thread_summary(self, thread_id: str) -> Optional[Dict]:
        """Get a summary of a thread."""
        if thread_id not in self.threads:
            return None
        
        thread = self.threads[thread_id]
        return {
            'thread_id': thread_id,
            'customer_email': thread['customer_email'],
            'created_at': thread['created_at'],
            'message_count': len(thread['messages']),
            'zoom_scheduled': thread['zoom_scheduled'],
            'is_marketing_thread': thread.get('is_marketing_thread', False),
            'last_sender': thread.get('last_sender')
        }
    
    def is_thread_expired(self, thread_id: str) -> bool:
        """Check if a thread is expired (older than THREAD_EXPIRATION_DAYS)."""
        if thread_id not in self.threads:
            return False
        
        thread = self.threads[thread_id]
        # 이미 Zoom이 예약된 스레드는 만료시키지 않음
        if thread.get('zoom_scheduled', False):
            return False
        
        # 마지막 메시지 시간 확인
        if thread['messages']:
            last_message_time = thread['messages'][-1]['timestamp']
            last_message_date = datetime.fromisoformat(last_message_time)
            expiration_date = datetime.now() - timedelta(days=THREAD_EXPIRATION_DAYS)
            
            return last_message_date < expiration_date
        
        # 메시지가 없으면 생성 시간으로 확인
        created_date = datetime.fromisoformat(thread['created_at'])
        expiration_date = datetime.now() - timedelta(days=THREAD_EXPIRATION_DAYS)
        return created_date < expiration_date
    
    def mark_thread_as_expired(self, thread_id: str):
        """Mark a thread as expired."""
        if thread_id in self.threads:
            self.threads[thread_id]['is_expired'] = True
            self.threads[thread_id]['expired_at'] = datetime.now().isoformat()
            self._save_threads()
            logger.info(f"Thread {thread_id[:8]} marked as expired")
    
    def cleanup_expired_threads(self) -> int:
        """Clean up expired threads and return count."""
        expired_count = 0
        threads_to_check = list(self.threads.keys())
        
        for thread_id in threads_to_check:
            if self.is_thread_expired(thread_id):
                self.mark_thread_as_expired(thread_id)
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Marked {expired_count} threads as expired")
            
        return expired_count