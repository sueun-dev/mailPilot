# Architecture Overview

## Components

### 1. Gmail Client (`src/gmail/`)
- Handles all Gmail API interactions
- OAuth2 authentication
- Message retrieval and sending
- Thread management

### 2. ChatGPT Client (`src/chatgpt/`)
- OpenAI API integration
- Response generation with context
- Zoom mention detection

### 3. Storage (`src/storage/`)
- Thread memory persistence
- Conversation context tracking
- Zoom scheduling status

### 4. Approval Interface (`src/approval/`)
- Rich terminal UI
- Draft review and approval
- Thread status display

### 5. Main Orchestrator (`src/main.py`)
- Coordinates all components
- Email processing workflow
- Application lifecycle

## Data Flow

1. **Email Reception**
   - Gmail client polls for unread messages
   - Messages are filtered and parsed

2. **Response Generation**
   - Thread context is retrieved from storage
   - ChatGPT generates contextual response
   - Response includes Zoom meeting suggestions

3. **Approval Process**
   - Draft is displayed in terminal UI
   - User reviews and approves/rejects
   - Approved emails are sent

4. **State Management**
   - Thread history is maintained
   - Zoom scheduling status is tracked
   - Prevents duplicate responses