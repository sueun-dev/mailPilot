"""Outbound marketing email functionality."""
import re
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from utils.logging_config import get_logger

# Module logger
logger = get_logger(__name__)

# Import app configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.app_config import EMAIL_TEMPLATES, DEFAULT_CAMPAIGN, MARKETING_SENT_FILE


class OutboundMarketing:
    """Handles outbound marketing email campaigns."""
    
    def __init__(self, sent_file: str = MARKETING_SENT_FILE):
        """Initialize outbound marketing."""
        self.sent_file = sent_file
        self.sent_records = self._load_sent_records()
        
    def _load_sent_records(self) -> Dict:
        """Load records of sent marketing emails."""
        with open(self.sent_file, 'r') as f:
            return json.load(f)
    
    def _save_sent_records(self):
        """Save sent records to file."""
        os.makedirs(os.path.dirname(self.sent_file), exist_ok=True)
        with open(self.sent_file, 'w') as f:
            json.dump(self.sent_records, f, indent=2)
    
    def parse_customer_list(self, file_path: str) -> List[Tuple[str, str]]:
        """Parse customer list to extract names and emails."""
        customers = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse "Name <email@example.com>" format
                        match = re.match(r'^(.+?)\s*<(.+?)>$', line)
                        if match:
                            name = match.group(1).strip()
                            email = match.group(2).strip()
                            customers.append((name, email))
                        else:
                            logger.warning(f"Could not parse name from: {line}")
                            customers.append(("Customer", line))
                            
        except Exception as e:
            logger.error(f"Failed to parse customer list: {e}")
            
        return customers
    
    def has_been_sent(self, email: str, campaign: str = "youtube_shorts") -> bool:
        """Check if marketing email has already been sent to this email."""
        return email in self.sent_records.get(campaign, {})
    
    def mark_as_sent(self, email: str, campaign: str = "youtube_shorts"):
        """Mark email as sent for this campaign."""
        if campaign not in self.sent_records:
            self.sent_records[campaign] = {}
            
        self.sent_records[campaign][email] = {
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        
        self._save_sent_records()
    
    def get_unsent_customers(self, customers: List[Tuple[str, str]], campaign: str = "youtube_shorts") -> List[Tuple[str, str]]:
        """Get list of customers who haven't received this campaign yet."""
        unsent = []
        for name, email in customers:
            if not self.has_been_sent(email, campaign):
                unsent.append((name, email))
        return unsent
    
    def generate_marketing_email(self, name: str, campaign: str = None) -> Dict[str, str]:
        """Generate personalized marketing email content."""
        # Use default campaign if not specified
        if campaign is None:
            campaign = DEFAULT_CAMPAIGN
            
        template = EMAIL_TEMPLATES.get(campaign)
        if not template:
            raise ValueError(f"Template not found for campaign: {campaign}")
            
        subject = template['subject'].format(name=name)
        body = template['body'].format(name=name)
        
        return {
            "subject": subject,
            "body": body
        }