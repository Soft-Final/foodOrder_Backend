from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.crypto import get_random_string
from user_authentication.mail.mail import send_password_async

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if password is None:
            password = get_random_string(8)
            send_password_async(password=password, targets=[email])
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Ensure admins are marked as ADMIN type
        extra_fields.setdefault('user_type', 'ADMIN')
        user = self.create_user(email=email, password=password, **extra_fields)
        return user

# Define user type choices
USER_TYPE_CHOICES = [
    ('ADMIN', 'Admin'),
    ('KITCHEN', 'Kitchen'),
    ('CUSTOMER', 'Customer'),
]

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=512)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    # Added user type field to differentiate types of users
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='CUSTOMER')
    # Removed manager field

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    # Removed 'first_name' and 'last_name' fields from REQUIRED_FIELDS
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email