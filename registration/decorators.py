from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator

def two_factor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.two_factor_enabled:
            return view_func(request, *args, **kwargs)
        messages.warning(request, 'Two-factor authentication is required for this action.')
        return redirect('two_factor_setup')
    return wrapper

def audit_log(action_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            if request.user.is_authenticated:
                request.user.auditlog_set.create(
                    action=action_name,
                    model_name=view_func.__module__,
                    object_id=kwargs.get('pk', 0),
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            return response
        return wrapper
    return decorator

def api_key_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return JsonResponse({'error': 'Invalid API key'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def session_timeout(timeout_minutes=60):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                last_activity = request.session.get('last_activity')
                if last_activity:
                    elapsed = (timezone.now() - timezone.datetime.fromtimestamp(float(last_activity))).total_seconds() / 60
                    if elapsed > timeout_minutes:
                        request.session.flush()
                        messages.warning(request, 'Your session has expired. Please login again.')
                        return redirect('login')
                request.session['last_activity'] = timezone.now().timestamp()
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_https(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure():
            messages.warning(request, 'This action requires a secure connection.')
            return redirect('https://' + request.get_host() + request.get_full_path())
        return view_func(request, *args, **kwargs)
    return wrapper

def permission_required(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have the required permission.')
            return redirect('dashboard')
        return wrapper
    return decorator

def validate_api_key(api_key):
    # Implement your API key validation logic here
    valid_keys = ['your-secure-api-key']  # Store these securely in environment variables
    return api_key in valid_keys
