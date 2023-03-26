from django.contrib.auth.backends import BaseBackend
from inventory.models import ngo, donor


class MyUserBackend(BaseBackend):
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        """
        Authenticates a user by checking their username and password against the
        database.

        :param request:
            HTTP request object (optional)
        :param username:
            username of the user to authenticate
        :param password:
            password of the user to authenticate

        :return:
            the authenticated user object, or None if authentication fails
        """
        try:
            user = ngo.objects.get(username=username, is_ngo=True)
            if user.check_password(password):
                return user
        except ngo.DoesNotExist:
            try:
                user = donor.objects.get(username=username, is_ngo=False)
                if user.check_password(password):
                    return user
            except donor.DoesNotExist:
                return None

    def get_user(self, user_id):
        """
        Retrieves a user object from the database by ID.

        :param user_id:
            ID of the user to retrieve

        :return:
            user instance if found, or None if not found
        """
        try:
            return ngo.objects.get(pk=user_id)
        except ngo.DoesNotExist:
            try:
                return donor.objects.get(pk=user_id)
            except donor.DoesNotExist:
                return None
