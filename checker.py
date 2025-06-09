import requests
from bs4 import BeautifulSoup
import time
import random
import os

APP_ID = '1286637638'
COUNTRY = 'th'
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
LAST_VERSION_FILE = '.last_version'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/119.0.0.0 Safari/537.36'
    )
}


def load_last_version():
    if os.path.exists(LAST_VERSION_FILE):
        with open(LAST_VERSION_FILE, 'r') as f:
            return f.read().strip()
    return None


def save_last_version(version):
    with open(LAST_VERSION_FILE, 'w') as f:
        f.write(version)


def get_version_from_webpage(app_id, country='us'):
    url = f"https://apps.apple.com/{country}/app/id{app_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            version_tag = soup.find('p', class_='l-column small-6 medium-12 whats-new__latest__version')
            if version_tag:
                version = version_tag.text.strip().replace("Version ", "")
                print(f"[INFO] Version from web: {version}")
                return version
            else:
                print("[WARN] Version tag not found on page.")
        else:
            print(f"[WARN] HTTP {response.status_code} - Failed to fetch App Store page.")
    except Exception as e:
        print(f"[ERROR] Web scraping failed: {e}")
    return None


def get_version_from_itunes_lookup(app_id):
    url = f"https://itunes.apple.com/lookup?id={app_id}&country={COUNTRY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results")
            if results and "version" in results[0]:
                version = results[0]["version"]
                print(f"[INFO] Version from iTunes Lookup: {version}")
                return version
        else:
            print(f"[WARN] HTTP {response.status_code} from iTunes API.")
    except Exception as e:
        print(f"[ERROR] iTunes lookup failed: {e}")
    return None


def send_slack_notification(version):
    if not SLACK_WEBHOOK_URL:
        print("[WARN] Slack webhook URL not set.")
        return
    message = {
        "text": f"🚀 New App Store version detected: *{version}* for App ID `{APP_ID}`"
    }
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=message)
        if resp.status_code == 200:
            print("[INFO] Slack notification sent.")
        else:
            print(f"[ERROR] Slack notification failed: HTTP {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Slack request failed: {e}")


LAST_VERSION = load_last_version()
print(f"[INIT] Loaded last version: {LAST_VERSION or '(none)'}")

while True:
    latest_version = get_version_from_webpage(APP_ID, COUNTRY)
    if not latest_version:
        print("[INFO] Trying fallback: iTunes Lookup API...")
        latest_version = get_version_from_itunes_lookup(APP_ID)

    if latest_version:
        if latest_version != LAST_VERSION:
            print(f"[INFO] New version detected: {latest_version}")
            send_slack_notification(latest_version)
            save_last_version(latest_version)
            LAST_VERSION = latest_version
        else:
            print(f"[INFO] No change. Current version is still {latest_version}")
    else:
        print("[ERROR] Could not retrieve version from any source.")

    delay = random.randint(50, 70)
    print(f"[DEBUG] Sleeping for {delay} seconds...")
    time.sleep(delay)
