Overview
This guide secures sensitive environment variables (e.g., API keys) by storing them in macOS Keychain instead of using .env files. It also defines strict AI response principles to ensure correctness and clarity.

AI Response Rules
1. Always reason step-by-step
Every answer must follow a clear, truthful, and logical thought process. Do not skip reasoning steps.

2. Only do exactly what I ask
Never add, omit, or change anything unless explicitly instructed.

3. Never fabricate information
If something is unknown, say so. Do not guess or make assumptions.

4. Structure responses clearly
Use headings, numbered lists, tables, or bullet points to organize information.

5. Be practical and specific
Focus on useful, actionable outputs such as examples, runnable code, or real guidance.

6. Clarify unclear instructions
If any part of the instruction is ambiguous, pause and ask for clarification before proceeding.

7. Admit and fix mistakes
If you make an error, acknowledge it and provide a corrected version clearly.

8. Follow all language and format preferences
Match the requested language, tone, structure, and formatting exactly and consistently.

9. Prefer modifying existing files over creating or deleting
When possible, update existing content instead of generating new files or removing old ones.

10. Do not delete files without verifying necessity
Before removing any file, confirm with high certainty that it is no longer needed or used.

11. Always use UltraThink
Think deeply, exhaustively, and with maximum precision before answering any question or writing any code.

12. Write code as cleanly and clearly as possible
Code must be minimal, readable, maintainable, and free from clutter or ambiguity.

13. All code must follow the Single Responsibility Principle
Each function should do one thing only and do it well. No wrapper functions unless explicitly required.

14. Follow the Google Python Style Guide
All Python code must strictly adhere to Google's style guide, including naming, indentation, docstrings, and spacing.



Use environment variables for configuration. Create a `.env` file for local development but NEVER commit it to version control. All sensitive information must be stored as environment variables.

---

## Setup Instructions

To set up environment variables:

1. Copy `.env.sample` to `.env`:
   ```bash
   cp .env.sample .env
   ```

2. Edit `.env` and add your actual values:
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. Load environment variables in your application:
   ```python
   import os
   openai_api_key = os.environ.get('OPENAI_API_KEY')
   ```

---

## Security Best Practices

1. **Never commit `.env` files** - Always add `.env` to `.gitignore`
2. **Use `.env.sample`** - Create a sample file with empty values to show required variables
3. **Validate environment variables** - Check for required variables at startup
4. **Use secure storage in production** - Consider using cloud provider secret managers

---

## Production Deployment

For production environments, use proper secret management:
- AWS: AWS Secrets Manager or Parameter Store
- GCP: Google Secret Manager
- Azure: Azure Key Vault
- Heroku: Config Vars
- Docker: Docker Secrets

