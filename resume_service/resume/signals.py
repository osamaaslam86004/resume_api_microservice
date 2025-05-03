import json
import logging

import requests
from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from requests.adapters import HTTPAdapter, Retry

from resume.models import PersonalInfo

logger = logging.getLogger(__name__)


class TemporaryStorage:
    storage = {}


@receiver(post_save, sender=PersonalInfo)
def create_profile(sender, instance, **kwargs):

    if instance:
        data = {
            "id": instance.id,
            "user_id": instance.user_id,
            "event": "cv_created",
            "status": "CREATED",
            "exception": str("None"),
        }

        data = json.dumps(data)
        logger.error(f"data in signal: {data}")

        if settings.DEBUG:
            webhook_url = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"
        else:
            webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"

        headers = {"Content-Type": "application/json"}

        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[504, 500, 502, 503]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))

        try:
            response = requests.post(
                webhook_url, headers=headers, data=data, verify=False
            )
            response.raise_for_status()  # Raise an exception for any HTTP error status
            logger.info(
                f"Webhook sent successfully: {response.json()} and status code: {response.status_code}"
            )

        except requests.exceptions.RequestException as e:
            print("Failed to send webhook:", e)
            logger.error(f"Failed to send webhook: {e}")


@receiver(pre_delete, sender=PersonalInfo)
def store_cv_attributes(sender, instance, **kwargs):
    TemporaryStorage.storage[instance.id] = {
        "cv_id": instance.id,
        "user_id": instance.user_id,
    }


@receiver(post_delete, sender=PersonalInfo)
def send_webhook_on_cv_delete(sender, instance, **kwargs):
    attributes = TemporaryStorage.storage.pop(instance.id, None)

    if settings.DEBUG:
        webhook_url = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"
    else:
        webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"

    data = {
        "event": "cv_deleted",
        "id": attributes["cv_id"],
        "user_id": attributes["user_id"],
    }
    logger.error(f"Data to send webhook: {data}")

    data = json.dumps(data)
    headers = {"Content-Type": "application/json"}

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[504, 500, 502, 503])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = requests.post(webhook_url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        logger.info(
            f"Webhook sent successfully: {response.json()} and status code: {response.status_code}"
        )
    except requests.RequestException as e:
        print(f"Failed to send webhook: {e}")
        logger.error(f"Failed to send webhook: {e}")
