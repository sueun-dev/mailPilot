# How to Get Gmail API Credentials

Follow these steps to create and download your `credentials.json` file from Google Cloud Console.

## Step-by-Step Guide

### 1. Create or Select a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project dropdown at the top
3. Click "New Project" or select an existing project
4. Name it something like "Mail Pilot" and click "Create"

### 2. Enable Gmail API

1. In your project, navigate to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on "Gmail API" in the results
4. Click the **Enable** button

### 3. Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (or Internal if using Google Workspace)
3. Click **Create**
4. Fill in the required fields:
   - **App name**: Mail Pilot
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
5. Click **Save and Continue**
6. On the Scopes page, click **Add or Remove Scopes**
7. Add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
8. Click **Update** and then **Save and Continue**
9. Add test users (your email) if in testing mode
10. Click **Save and Continue**

### 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. For Application type, select **Desktop app**
4. Name it "Mail Pilot Desktop" (or any name you prefer)
5. Click **Create**

### 5. Download the Credentials

1. In the credentials list, find your newly created OAuth 2.0 Client ID
2. Click the download button (⬇️) on the right
3. Save the downloaded file as `credentials.json` in this config folder

## Important Notes

- Keep your `credentials.json` file secure and never commit it to version control
- The file should be placed at: `mailPilot/config/credentials.json`
- If you're in development/testing mode, you'll need to add test users in the OAuth consent screen
- The app will remain in "Testing" mode unless you submit it for verification (not needed for personal use)

## Troubleshooting

### "Access blocked" error
- Make sure you've added your email as a test user in the OAuth consent screen

### "Redirect URI mismatch" error
- The Desktop app type should automatically handle redirect URIs
- If issues persist, ensure you selected "Desktop app" as the application type

### Rate limits
- Gmail API has quotas. For personal use, you're unlikely to hit them
- Check your quotas at: APIs & Services → Quotas