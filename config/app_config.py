"""Central configuration for MailPilot application.

All user-configurable settings should be managed here.
"""

# ===== EMAIL CONFIGURATION =====

# Marketing email templates
EMAIL_TEMPLATES = {
    "youtube_shorts": {
        "subject": "Hi {name} - Transform Your Content Creation with AI 🚀",
        "body": """Hi {name},

I hope this email finds you well! I wanted to reach out because I've been working on something that I think could really help content creators like yourself.

Have you ever wished you could create engaging YouTube Shorts faster and more efficiently? I've developed YouTube Shorts Auto Generator - an AI-powered tool that helps you:

✨ Generate viral-worthy short videos in minutes
🎯 Optimize content for maximum engagement
🎨 Create eye-catching thumbnails automatically
📊 Analyze trends to stay ahead of the curve
⏰ Save hours of editing time

The best part? It's designed to maintain your unique style while boosting your productivity 10x.

I'd love to show you how it works and discuss how it could fit into your content creation workflow. Would you be interested in a quick 15-minute Zoom demo? I'm confident it could transform the way you create content.

Looking forward to hearing your thoughts!

Warm regards,

Sueun Cho
sueun.dev@gmail.com"""
    }
}

# Default campaign to use
DEFAULT_CAMPAIGN = "youtube_shorts"

# Email signature for all emails
EMAIL_SIGNATURE = """Sueun Cho
sueun.dev@gmail.com"""

# ===== GMAIL API CONFIGURATION =====

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Gmail query for fetching emails
GMAIL_QUERY = "is:unread"

# OAuth settings
OAUTH_PORT = 0  # 0 = dynamic port assignment

# ===== FILE PATHS =====

# Credentials and config
CREDENTIALS_FILE = "config/credentials.json"
TOKEN_FILE = "data/token.json"
CUSTOMER_LIST_FILE = "config/customer_emails.txt"

# Data storage
THREAD_MEMORY_FILE = "data/thread_memory.json"
MARKETING_SENT_FILE = "data/marketing_sent.json"
LAST_PROCESSED_FILE = "data/last_processed.json"

# Log files
LOG_DIR = "logs"
MAIN_LOG_FILE = "logs/mailpilot.log"
ERROR_LOG_FILE = "logs/mailpilot_errors.log"
SECURITY_LOG_FILE = "logs/mailpilot_security.log"

# ===== LOGGING CONFIGURATION =====

# Log levels by environment
ENV_LOG_LEVELS = {
    'development': 'DEBUG',
    'test': 'INFO',
    'production': 'WARNING'
}

# Log file settings
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
SECURITY_LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 5
SECURITY_LOG_BACKUP_COUNT = 10

# Third-party logger settings
THIRD_PARTY_LOG_LEVELS = {
    'urllib3': 'WARNING',
    'google': 'WARNING',
    'googleapiclient': 'ERROR',
    'google_auth_httplib2': 'ERROR',
    'oauthlib': 'ERROR',
    'httpx': 'WARNING',
    'openai': 'WARNING',
    'httpcore': 'ERROR'
}

# ===== CHATGPT CONFIGURATION =====

# OpenAI model settings
CHATGPT_MODEL = "gpt-4-turbo-preview"
CHATGPT_TEMPERATURE = 0.7
CHATGPT_MAX_TOKENS = 500

# System prompt for sales responses
CHATGPT_SYSTEM_PROMPT = """You are a professional sales representative for YouTube Shorts Auto Generator. 
Keep responses concise, friendly, and focused on scheduling a Zoom demo. 
Always maintain a helpful and enthusiastic tone.
Address the customer by name when possible.
If they express interest, provide a specific time suggestion for the Zoom meeting."""

# Keywords to detect Zoom meeting confirmation
ZOOM_CONFIRMATION_KEYWORDS = [
    "zoom meeting scheduled",
    "calendar invite sent",
    "meeting confirmed",
    "see you on zoom",
    "zoom link:",
    "meeting id:",
    "join zoom meeting"
]

# ===== OPERATIONAL SETTINGS =====

# Processing limits
FIRST_RUN_MESSAGE_LIMIT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Response timing
MIN_RESPONSE_DELAY = 30  # seconds - minimum delay before sending response
MAX_RESPONSE_DELAY = 120  # seconds - maximum delay before sending response

# Thread management
THREAD_EXPIRATION_DAYS = 30  # days - threads older than this are considered expired

# UI settings
MENU_SLEEP_DELAY = 0.5  # seconds
CONSOLE_PADDING = (1, 2)

# Console color codes
CONSOLE_COLORS = {
    'DEBUG': '\033[36m',    # Cyan
    'INFO': '\033[32m',     # Green
    'WARNING': '\033[33m',  # Yellow
    'ERROR': '\033[31m',    # Red
    'CRITICAL': '\033[35m', # Magenta
    'RESET': '\033[0m'
}

# ===== LOCALE SETTINGS =====

# Preferred locale settings
PREFERRED_LOCALES = ['en_US.UTF-8', 'C.UTF-8']

# ===== SECURITY PATTERNS =====

# Patterns for sensitive data redaction in logs
SENSITIVE_PATTERNS = [
    (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\\s]+)', 'API_KEY'),
    (r'password["\']?\s*[:=]\s*["\']?([^"\'\\s]+)', 'PASSWORD'),
    (r'token["\']?\s*[:=]\s*["\']?([^"\'\\s]+)', 'TOKEN'),
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}', 'EMAIL'),
    (r'secret["\']?\s*[:=]\s*["\']?([^"\'\\s]+)', 'SECRET'),
]