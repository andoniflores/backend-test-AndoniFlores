import time

from celery import shared_task
import requests

# Send slack message to slack cornershop channel
@shared_task
def send_reminder_task(payload):
    response = requests.post('https://hooks.slack.com/services/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',
                    data = payload)
    return response