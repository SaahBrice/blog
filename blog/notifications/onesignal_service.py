from onesignal_sdk.client import Client
from django.conf import settings

class OneSignalService:
    def __init__(self):
        self.client = Client(
            app_id=settings.ONESIGNAL_APP_ID,
            rest_api_key=settings.ONESIGNAL_REST_API_KEY
        )

    def send_notification(self, player_ids, message, data=None):
        notification_body = {
            'contents': {'en': message},
            'include_player_ids': player_ids,
        }
        if data:
            notification_body['data'] = data
        
        response = self.client.send_notification(notification_body)
        return response