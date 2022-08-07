from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from users.managers import CustomUserManager
from companies.models import (
    Company,
    Office,
    Vehicle
)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=128,
                              unique=True)
    first_name = models.CharField(max_length=256,
                                  blank=True)
    last_name = models.CharField(max_length=256,
                                 blank=True)
    company = models.ForeignKey(Company,
                                on_delete=models.CASCADE,
                                null=True)
    # Office of employee registration
    office = models.ForeignKey(Office,
                               on_delete=models.SET_DEFAULT,
                               default=None,
                               null=True,
                               blank=True,
                               related_name='employees')
    # Vehicles of employee
    vehicles = models.ManyToManyField(Vehicle,
                                      blank=True,
                                      related_name='driver')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
