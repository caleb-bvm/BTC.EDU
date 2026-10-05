from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AccountBackend(ModelBackend):
    """Scope credentials to one account type, including when emails match."""

    def authenticate(self, request, username=None, password=None, account_type=None, **kwargs):
        user_model = get_user_model()
        email = username or kwargs.get(user_model.USERNAME_FIELD)
        if email is None or password is None:
            return None
        if account_type is None:
            # The administration uses Django's own authentication form.
            account_type = user_model.Type.ADMIN if request and request.path.startswith("/admin/") else user_model.Type.STUDENT
        try:
            user = user_model.objects.get(email__iexact=email.strip(), account_type=account_type)
        except user_model.DoesNotExist:
            user_model().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
