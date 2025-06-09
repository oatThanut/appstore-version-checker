# App Store Version Checker

Monitors an iOS app's latest version on the App Store (via scraping and fallback API).  
Sends Slack notifications when a new version is released.

## How to Use

1. Clone this repo.
2. Create `.env` from `.env.example`.
3. Build the Docker image:
   ```
   docker build -t appstore-checker .
   ```
4. Run it with a volume for version tracking:
   ```
   mkdir -p data
   docker run -d --env-file .env -v $(pwd)/data:/app appstore-checker
   ```

## Config

- `SLACK_WEBHOOK_URL`: Slack Incoming Webhook URL
- You can change `APP_ID` and `COUNTRY` in `checker.py`
