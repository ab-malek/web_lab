from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps
from .models import UserProfile


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                user_profile = request.user.userprofile
                if user_profile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    raise PermissionDenied
            except UserProfile.DoesNotExist:
                raise PermissionDenied
        return _wrapped_view
    return decorator
