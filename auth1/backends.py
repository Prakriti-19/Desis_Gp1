from django.contrib.auth.backends import BaseBackend
from inventory.models import ngo,donor
class MyUserBackend(BaseBackend):
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        try:
            user = ngo.objects.get(username=username, is_ngo=True,is_donor=False)
            if user.check_password(password):
                return user
        except ngo.DoesNotExist:
            try:
                user = donor.objects.get(username=username, is_donor=True,is_ngo=False)
                if user.check_password(password) :
                    return user
            except donor.DoesNotExist:
                return None
    
    def get_user(self, user_id):
        try:
            return ngo.objects.get(pk=user_id)
        except ngo.DoesNotExist:
            try:
                return donor.objects.get(pk=user_id)
            except donor.DoesNotExist:
                return None