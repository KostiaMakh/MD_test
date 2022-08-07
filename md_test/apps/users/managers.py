from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email field can not be empty')
        else:
            user = self.model(email=self.normalize_email(email),
                              **extra_fields)
            user.set_password(password)
            user.save()
            return user

    def create_admin(self, email, password):
        return self._create_user(email,
                                 password,
                                 is_admin=True)

    def create_employee(self, email, password):
        return self._create_user(email,
                                 password,
                                 is_admin=False)

    def create_superuser(self, email, password):
        return self._create_user(email,
                                 password,
                                 is_staff=True,
                                 is_superuser=True)
