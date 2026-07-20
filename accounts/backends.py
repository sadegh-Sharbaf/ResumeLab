from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import User


class IdentifierBackend(ModelBackend):
    """Authenticate with username, email, or phone."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = (username or kwargs.get("identifier") or "").strip()
        if not identifier or not password:
            return None
        try:
            user = User.objects.get(
                Q(username__iexact=identifier)
                | Q(email__iexact=identifier)
                | Q(phone=identifier)
            )
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
