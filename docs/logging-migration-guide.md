# Logging Migration Guide

## Overview

This guide provides a comprehensive plan for migrating from `print()` statements to structured logging using the new logging framework.

## Quick Start

```python
# At the top of your module
from utils.logging_config import get_logger

# Create module logger
logger = get_logger(__name__)

# Use instead of print()
logger.info("Starting email processing")
logger.error("Failed to send email", exc_info=True)
```

## Migration Examples by Module

### 1. Gmail Client (`src/gmail/client.py`)

**Current print statements:**
```python
print(f"No token found at {self.token_file}. Will authenticate with Google.")
print("Opening browser for Google authentication...")
print(f"Creating directory: {token_dir}")
print(f"Saving authentication token to {self.token_file}")
print("Authentication successful!")
print(f'An error occurred: {error}')
```

**Migrated to logging:**
```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

class GmailClient:
    def _authenticate(self):
        """Authenticate and return Gmail service."""
        try:
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        except FileNotFoundError:
            logger.info(f"No token found at {self.token_file}. Will authenticate with Google.")
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.debug("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                logger.info("Opening browser for Google authentication...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Directory creation
            if token_dir and not os.path.exists(token_dir):
                logger.debug(f"Creating directory: {token_dir}")
                os.makedirs(token_dir, exist_ok=True)
            
            logger.info(f"Saving authentication token")  # Don't log the path in production
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            logger.info("Authentication successful!")
    
    def get_unread_messages(self, query: str = 'is:unread') -> List[Dict]:
        """Get unread messages from inbox."""
        try:
            # ... existing code ...
        except HttpError as error:
            logger.error(f"Failed to get unread messages: {error}", extra={
                "query": query,
                "error_code": error.resp.status if hasattr(error, 'resp') else None
            })
            return []
```

### 2. ChatGPT Client (`src/chatgpt/client.py`)

**Current:**
```python
print(f"Error generating response: {e}")
```

**Migrated:**
```python
from utils.logging_config import get_logger, LogPerformance

logger = get_logger(__name__)

class ChatGPTClient:
    def generate_response(self, email_content: str, thread_context: Optional[str] = None) -> Optional[str]:
        """Generate response using ChatGPT."""
        with LogPerformance(logger, "ChatGPT API call", logging.DEBUG):
            try:
                messages = self._build_messages(email_content, thread_context)
                
                logger.debug("Sending request to OpenAI", extra={
                    "model": self.model,
                    "message_count": len(messages),
                    "has_context": bool(thread_context)
                })
                
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **self.model_params
                )
                
                response = completion.choices[0].message.content
                logger.info("Successfully generated response", extra={
                    "response_length": len(response),
                    "zoom_mentioned": self._check_zoom_mention(response)
                })
                
                return response
                
            except Exception as e:
                logger.error(f"Error generating ChatGPT response: {e}", 
                           exc_info=True,
                           extra={"email_preview": email_content[:100]})
                return None
```

### 3. Thread Memory (`src/storage/thread_memory.py`)

**Current:**
```python
print(f"Error saving threads: {e}")
```

**Migrated:**
```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

class ThreadMemory:
    def _save_threads(self):
        """Save threads to storage file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.threads, f, indent=2)
            logger.debug(f"Saved {len(self.threads)} threads to storage")
        except IOError as e:
            logger.error(f"Failed to save thread data", exc_info=True, extra={
                "storage_file": self.storage_file,
                "thread_count": len(self.threads)
            })
```

### 4. Main Application (`src/main.py`)

**Current:**
```python
print("Error: OPENAI_API_KEY not found in keychain")
print("Run: python keychain_env.py set OPENAI_API_KEY 'your-key'")
print("\n\nShutting down...")
print(f"\nError: {e}")
```

**Migrated:**
```python
from utils.logging_config import get_logger, configure_logging

logger = get_logger(__name__)

def main():
    """Main entry point."""
    # Configure logging based on environment
    configure_logging()
    
    logger.info("MailPilot starting up", extra={
        "version": "0.1.0",
        "environment": os.getenv("MAILPILOT_ENV", "development")
    })
    
    try:
        # Load environment
        kc.load_all_to_env()
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            logger.critical("OPENAI_API_KEY not found in keychain")
            # Still print to console for user
            print("Error: OPENAI_API_KEY not found in keychain")
            print("Run: python scripts/keychain_env.py set OPENAI_API_KEY 'your-key'")
            return 1
        
        # Check for credentials
        if not os.path.exists(config_path):
            logger.error("Gmail credentials file not found", extra={
                "expected_path": config_path
            })
            # User-facing message
            print("Error: config/credentials.json not found")
            print("\nPlease follow the instructions in config/HOW_TO_GET_CREDENTIALS.md")
            return 1
        
        # Run application
        responder = EmailAutoResponder()
        responder.run()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        print("\n\nShutting down...")
    except Exception as e:
        logger.critical("Unhandled exception in main", exc_info=True)
        print(f"\nError: {e}")
        return 1
    
    logger.info("MailPilot shutdown complete")
    return 0
```

### 5. Approval Interface (`src/approval/interface.py`)

**Note:** The approval interface uses Rich console for UI output. These should remain as console.print() calls since they're user interface elements, not logs.

```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

class ApprovalInterface:
    def __init__(self):
        self.console = Console()
        logger.debug("Initialized approval interface")
    
    def display_draft(self, draft: Dict, context: Optional[str] = None) -> bool:
        """Display email draft for approval."""
        logger.info("Displaying draft for approval", extra={
            "to": draft.get('to', ''),
            "thread_id": draft.get('thread_id', 'new'),
            "has_context": bool(context)
        })
        
        # Keep console.print for UI elements
        self.console.print("\n[bold blue]📧 Email Draft Review[/bold blue]\n")
        # ... rest of UI code stays the same
        
        approved = Confirm.ask("Send this email?", default=True)
        logger.info(f"Draft approval: {'approved' if approved else 'rejected'}")
        return approved
```

## Logging Best Practices

### 1. Log Levels

- **DEBUG**: Detailed information for diagnosing problems
  ```python
  logger.debug("Processing email", extra={"msg_id": msg_id, "size": len(body)})
  ```

- **INFO**: General informational messages
  ```python
  logger.info("Email sent successfully", extra={"recipient": to, "thread_id": thread_id})
  ```

- **WARNING**: Warning messages for potential issues
  ```python
  logger.warning("Rate limit approaching", extra={"current": 95, "limit": 100})
  ```

- **ERROR**: Error messages that don't stop execution
  ```python
  logger.error("Failed to send email", exc_info=True, extra={"recipient": to})
  ```

- **CRITICAL**: Fatal errors that stop execution
  ```python
  logger.critical("Unable to connect to Gmail API", exc_info=True)
  ```

### 2. Structured Logging

Always use the `extra` parameter for additional context:

```python
logger.info("Processing email thread", extra={
    "thread_id": thread_id,
    "message_count": len(messages),
    "sender": sender_email,
    "subject": subject[:50]  # Truncate for privacy
})
```

### 3. Performance Logging

Use the LogPerformance context manager:

```python
with LogPerformance(logger, "Email processing"):
    # Long running operation
    process_emails()
```

### 4. Security Considerations

- Never log sensitive data directly
- Use the built-in sanitization filters
- Be careful with email addresses and personal info

```python
# Bad
logger.info(f"User {email} logged in with password {password}")

# Good
logger.info("User authentication successful", extra={"user_id": user_id})
```

### 5. Exception Logging

Always use `exc_info=True` for exceptions:

```python
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True, extra={
        "operation": "risky_operation",
        "context": relevant_context
    })
```

## Environment Configuration

### Development
```bash
export MAILPILOT_ENV=development
# Colored console output, DEBUG level
```

### Test
```bash
export MAILPILOT_ENV=test
# Structured JSON to console, INFO level
```

### Production
```bash
export MAILPILOT_ENV=production
export MAILPILOT_LOG_DIR=/var/log/mailpilot
# File output only, WARNING level
```

## Testing Logging

```python
import unittest
from unittest.mock import patch
import logging

class TestWithLogging(unittest.TestCase):
    def test_error_handling(self):
        with self.assertLogs('src.gmail.client', level='ERROR') as cm:
            # Test code that should log an error
            client.some_method_that_fails()
        
        self.assertIn('ERROR:src.gmail.client:Failed', cm.output[0])
```

## Monitoring and Analysis

The structured JSON logs can be easily parsed for monitoring:

```bash
# Count errors by module
jq '. | select(.level == "ERROR") | .module' logs/mailpilot.log | sort | uniq -c

# Find slow operations
jq '. | select(.message | contains("completed in")) | select(.duration > 1.0)' logs/mailpilot.log

# Track authentication events
jq '. | select(.message | contains("Authentication"))' logs/mailpilot_security.log
```

## Migration Checklist

- [ ] Add `from utils.logging_config import get_logger` to each module
- [ ] Create module logger: `logger = get_logger(__name__)`
- [ ] Replace print statements with appropriate log levels
- [ ] Add structured context with `extra` parameter
- [ ] Test with different environments
- [ ] Update documentation
- [ ] Configure monitoring/alerting based on logs
- [ ] Train team on new logging practices