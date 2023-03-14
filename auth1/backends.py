from django.contrib.auth.backends import BaseBackend
from inventory.models import ngo,donor

'''
This is a customisable backend for our application that while authenticating checks the is_ngo flag and
tries to retrieve an ngo or donor's object with the provided username and password.

It returns instance of ngo or donor whosoevers username and password matches and if neither an ngo nor a donor object is found, 
then the method returns None.
'''
class MyUserBackend(BaseBackend):
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        try:
            user = ngo.objects.get(username=username, is_ngo=True)
            if user.check_password(password):
                return user
        except ngo.DoesNotExist:
            try:
                user = donor.objects.get(username=username, is_ngo=False)
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