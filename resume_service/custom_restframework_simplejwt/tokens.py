from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from custom_restframework_simplejwt.exceptions import (
    ExpiredTokenError,
    TokenBackendError,
    TokenBackendExpiredToken,
    TokenError,
)
from custom_restframework_simplejwt.models import TokenUser
from custom_restframework_simplejwt.state import api_settings
from custom_restframework_simplejwt.utils import (
    aware_utcnow,
    datetime_from_epoch,
    datetime_to_epoch,
    format_lazy,
    get_md5_hash_password,
    logger,
)

if TYPE_CHECKING:
    from custom_restframework_simplejwt.backends import TokenBackend

T = TypeVar("T", bound="Token")

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class Token:
    """
    A class which validates and wraps an existing JWT
    """

    token_type: Optional[str] = None
    lifetime: Optional[timedelta] = None

    def __init__(self, token: Optional["Token"] = None, verify: bool = True) -> None:
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """

        self.token = token
        self.current_time = aware_utcnow()

        # Set up token
        if token is not None:
            # An encoded token was provided
            token_backend = self.get_token_backend()

            # Decode token
            try:
                self.payload = token_backend.decode(token, verify=verify)
            except TokenBackendExpiredToken as e:
                raise ExpiredTokenError(_("Token is expired")) from e
            except TokenBackendError as e:
                raise TokenError(_("Token is invalid")) from e

            if verify:
                self.verify()

    def __repr__(self) -> str:
        return repr(self.payload)

    def __getitem__(self, key: str):
        return self.payload[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.payload[key] = value

    def __delitem__(self, key: str) -> None:
        del self.payload[key]

    def __contains__(self, key: str) -> Any:
        return key in self.payload

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.payload.get(key, default)

    def __str__(self) -> str:
        """
        Signs and returns a token as a base64 encoded string.
        """
        return self.get_token_backend().encode(self.payload)

    def verify(self) -> None:
        """
        Performs additional validation steps which were not performed when this
        token was decoded.  This method is part of the "public" API to indicate
        the intention that it may be overridden in subclasses.
        """
        # According to RFC 7519, the "exp" claim is OPTIONAL
        # (https://tools.ietf.org/html/rfc7519#section-4.1.4).  As a more
        # correct behavior for authorization tokens, we require an "exp"
        # claim.  We don't want any zombie tokens walking around.
        self.check_exp()

        # If the defaults are not None then we should enforce the
        # requirement of these settings.As above, the spec labels
        # these as optional.
        if (
            api_settings["JTI_CLAIM"] is not None
            and api_settings["JTI_CLAIM"] not in self.payload
        ):
            raise TokenError(_("Token has no id"))

        if api_settings["TOKEN_TYPE_CLAIM"] is not None:
            self.verify_token_type()

    def verify_token_type(self) -> None:
        """
        Ensures that the token type claim is present and has the correct value.
        """
        token_type = None
        try:
            token_type = self.payload[api_settings["TOKEN_TYPE_CLAIM"]]
        except KeyError as e:
            raise TokenError(_("Token has no type")) from e

        if self.token_type != token_type:
            raise TokenError(_("Token has wrong type"))

    def check_exp(
        self, claim: str = "exp", current_time: Optional[datetime] = None
    ) -> None:
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        if current_time is None:
            current_time = self.current_time

        try:
            claim_value = self.payload[claim]
        except KeyError as e:
            raise TokenError(format_lazy(_("Token has no '{}' claim"), claim)) from e

        claim_time = datetime_from_epoch(claim_value)
        leeway = self.get_token_backend().get_leeway()
        if claim_time <= current_time - leeway:
            raise TokenError(format_lazy(_("Token '{}' claim has expired"), claim))

    _token_backend: Optional["TokenBackend"] = None

    @property
    def token_backend(self) -> "TokenBackend":
        if self._token_backend is None:
            self._token_backend = import_string(
                "custom_restframework_simplejwt.state.token_backend"
            )
        return self._token_backend

    def get_token_backend(self) -> "TokenBackend":
        # Backward compatibility.
        return self.token_backend


class AccessToken(Token):
    token_type = "access"
    lifetime = api_settings["ACCESS_TOKEN_LIFETIME"]
