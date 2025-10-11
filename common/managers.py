# common/managers.py
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, email, username, password=None, **extra_fields):
        if not user_id:
            raise ValueError(_('아이디는 필수입니다.'))
        if not email:
            raise ValueError(_('이메일은 필수입니다.'))
        if not username:
            raise ValueError(_('사용자 이름은 필수입니다.'))

        email = self.normalize_email(email)
        user = self.model(
            user_id=user_id,
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)

        return self.create_user(user_id, email, username, password, **extra_fields)