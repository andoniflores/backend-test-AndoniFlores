import time

from celery import shared_task
import requests

# Send slack message to slack cornershop channel
@shared_task
def send_reminder_task(payload):
    response = requests.post('https://hooks.slack.com/services/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',
                    data = payload)
    return response