import time

from celery import shared_task
import requests
from keys import WEBHOOK_URL

# Send slack message to slack cornershop channel
@shared_task
def send_reminder_task(payload):
    response = requests.post(WEBHOOK_URL,
                    data = payload)
    return response