import pdb
from rest_framework.permissions import BasePermission
from django.conf import settings
import os

SAFE_METHODS = ['GET']
MY_CUSTOM_SETTING = os.environ.get('a', 'default_value')


class WhitelistPermission(BasePermission):
    message = "You must be a manager to create a raffle"

    def has_permission(self, request, view):
        # skip permisson if request is GET
        if request.method in SAFE_METHODS:
            return True
        else:
            # Access to the raffle manager endpoints is only allowed from ips listed in the `MANAGER_IPS`
            domain = request.META['REMOTE_ADDR']
            whitelisted = os.environ.get('MANAGER_IPS').split(',')
            if domain in whitelisted:
                return True
            return False
