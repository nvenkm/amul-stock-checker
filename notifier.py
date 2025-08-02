# notifier.py
import os
import requests
import logging

def send_ntfy_notification(logger, ntfy_url, message,ntfy_topic, title="Amul Stock Alert", priority="high"):
        """Send notification via ntfy.sh"""
        try:
            headers = {
                "Title": title,  # still fine for most clients
                "Content-Type": "text/plain; charset=utf-8",
                "X-Priority": priority,  # ntfy.sh expects X-Priority
                "X-Tags": "shopping,amul,stock"
            }

            response = requests.post(
                ntfy_url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"📱 Notification sent successfully to {ntfy_topic}")
            else:
                logger.error(f"❌ Failed to send notification: HTTP {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error sending notification: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error sending notification: {e}")
