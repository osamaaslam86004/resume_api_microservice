import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

logger = logging.getLogger(__name__)


def delete_blacklisted_tokens():
    """Delete blacklisted JWT tokens older than 24 hours

    Command: zappa tail dev --filter="api_auth"
    """

    logger.info(f"My scheduled task ran at {timezone.now()}")

    tokens_exists = BlacklistedToken.objects.exists()

    if tokens_exists:
        tokens = BlacklistedToken.objects.all()

        cutoff_time = timezone.now() - timedelta(days=1)

        tokens_to_delete = tokens.filter(blacklisted_at__lt=cutoff_time)

        if tokens_to_delete.exists():
            deleted_count, _ = tokens_to_delete.delete()

            logger.info(f"Deleted {deleted_count} blacklisted tokens")

        else:
            logger.info("No tokens to delete")
    else:
        logger.info("Table is Empty")
