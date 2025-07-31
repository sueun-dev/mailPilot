# Detailed Setup Guide

## Prerequisites

- Python 3.12+
- macOS (for Keychain support) or Linux/Windows with environment variables
- Google account with Gmail access
- OpenAI API account

## Step 1: Clone and Install

```bash
git clone <your-repo-url>
cd mailPilot

# Install dependencies
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

## Step 2: Google Cloud Setup

### Create a Project

1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Click "Create Project"
3. Name it (e.g., "Mail Pilot")

### Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Enable"

### Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop app" as application type
4. Name it (e.g., "Mail Pilot Desktop")
5. Download the JSON file
6. Save it as `config/credentials.json`

### Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (or "Internal" for Google Workspace)
3. Fill in required fields:
   - App name: Mail Pilot
   - User support email: your email
   - Developer contact: your email
4. Add scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`

## Step 3: OpenAI Setup

### Get API Key

1. Visit [OpenAI Platform](https://platform.openai.com)
2. Go to API keys section
3. Create new secret key

### Store API Key (macOS)

```bash
python scripts/keychain_env.py set OPENAI_API_KEY 'sk-...'
```

### Store API Key (Other platforms)

Create `.env` file:
```bash
OPENAI_API_KEY=sk-...
```

## Step 4: First Run

```bash
python run.py
```

On first run:
1. Browser will open for Gmail authorization
2. Grant requested permissions
3. Token will be saved to `data/token.json`

## Troubleshooting

### "credentials.json not found"
- Ensure file is in `config/` directory
- Check file permissions

### OAuth errors
- Verify Gmail API is enabled
- Check OAuth consent screen configuration
- For test users, add your email to test users list

### "OPENAI_API_KEY not found"
- Run keychain setup command again
- Verify key is correct

### Permission errors
- Ensure `data/` directory is writable
- Check file ownership