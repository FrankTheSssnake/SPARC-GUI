from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import json
import os

class FCMNotifier:
    def __init__(self, service_account_path, project_id, settings_path="settings.json"):
        self.service_account_path = service_account_path
        self.project_id = project_id
        self.settings_path = settings_path
        self._access_token = None
        self._creds = None
        self._refresh_token()

    def _refresh_token(self):
        self._creds = service_account.Credentials.from_service_account_file(
            self.service_account_path,
            scopes=['https://www.googleapis.com/auth/firebase.messaging']
        )
        request = google.auth.transport.requests.Request()
        self._creds.refresh(request)
        self._access_token = self._creds.token

    def send_topic_notification(self, title, body, data=None):
        # Load userID from settings.json
        if not os.path.exists(self.settings_path):
            raise FileNotFoundError(f"Settings file not found: {self.settings_path}")
        with open(self.settings_path, 'r') as f:
            settings = json.load(f)
        topic = settings.get('userID')
        if not topic:
            raise ValueError("userID (topic) not found in settings.json")
        if not self._access_token or self._creds.expired:
            self._refresh_token()
        message = {
            "message": {
                "topic": topic,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }
        if data:
            message["message"]["data"] = data
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        url = f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send"
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(message)
        )
        return response.status_code, response.text

# Example usage (remove or comment out in production):
# notifier = FCMNotifier('service-account.json', 'sparc-8b7af')
# status, resp = notifier.send_topic_notification(
#     title="Hello",
#     body="This is a topic push notification"
# )
# print(status, resp)

