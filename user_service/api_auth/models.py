from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.contrib.auth import authenticate


class CustomUserManager(BaseUserManager):
    # def create_user(self, email, username, password=None):
    def create_user(self, **kwargs):
        email = kwargs["email"]

        password = kwargs["password"]

        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=kwargs["username"],
            is_active=kwargs.get("is_active", None),
            is_staff=kwargs.get("is_staff", None),
            # locality = kwargs['locality'],
            # # start_date = validated_data['start_date'],
            # # end_date  = validated_data['end_date'],
            # facebook = kwargs['facebook']
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_user(self, email, username, password):

        user = authenticate(email=email, password=password)
        if user:
            return user
        else:
            return None

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # locality = models.CharField(max_length=255, help_text="e.g. city such as Boston", null=True)
    # facebook = models.URLField(blank=True)
    # start_date = models.DateField(null=True)
    # end_date = models.DateField(null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
