import logging
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from rest_framework_simplejwt.exceptions import TokenError

logger = logging.getLogger(__name__)

from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=OutstandingToken)
def blacklist_old_tokens(sender, instance, **kwargs):
    """
    Signal handler to blacklist old refresh and access tokens when a new OutstandingToken is added.
    """

    if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] == False:
        return

    try:
        # Decode the new refresh token
        new_refresh_token = RefreshToken(instance.token)
        user_id = new_refresh_token.payload["user_id"]

        # Get the user's outstanding tokens excluding the newly added one
        outstanding_tokens = OutstandingToken.objects.filter(user_id=user_id).exclude(
            id=instance.id
        )

        for outstanding_token in outstanding_tokens:
            try:
                old_refresh_token = RefreshToken(outstanding_token.token)
                old_refresh_token.blacklist()
                logger.debug(
                    f"Blacklisted old refresh token: {outstanding_token.token}"
                )
            except TokenError as e:
                logger.error(f"Failed to blacklist token: {e}")

        # Also blacklist the associated access tokens
        for outstanding_token in outstanding_tokens:
            access_token = outstanding_token.token.access_token
            try:
                BlacklistedToken.objects.get_or_create(token=access_token)
                logger.debug(f"Blacklisted old access token: {access_token}")
            except TokenError as e:
                logger.error(f"Failed to blacklist access token: {e}")

    except Exception as e:
        logger.error(f"Error in blacklisting old tokens: {str(e)}")


# @receiver(pre_save, sender=BlacklistedToken)
# def blacklist_access_token(sender, instance, **kwargs):
#     try:
#         # Get the refresh token from the BlacklistedToken instance
#         refresh_token = RefreshToken(str(instance.token))

#         # Check if the token type is a refresh token
#         if refresh_token.token_type == "refresh":
#             # Get the user associated with the refresh token

#             user = User.objects.get(id=refresh_token.get("user_id"))

#             # Get the access token associated with the refresh token
#             access_token = RefreshToken.for_user(user).access_token

#             # Add the access token to the BlacklistedToken table
#             BlacklistedToken.objects.create(token=access_token)
#     except Exception as e:
#         # Handle any exceptions that may occur
#         print(f"Error blacklisting access token: {e}")
