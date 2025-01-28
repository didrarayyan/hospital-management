from django.utils import timezone
from django.urls import resolve
from django.contrib.auth.views import LoginView
from .models import AuditLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated and not isinstance(resolve(request.path).func.view_class, LoginView):
            self.log_user_action(request)
        
        return response
    
    def log_user_action(self, request):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            AuditLog.objects.create(
                user=request.user,
                action=request.method,
                model_name=request.path.split('/')[1],
                object_id=request.resolver_match.kwargs.get('pk', 0),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

class SessionManagementMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            current_time = timezone.now().timestamp()
            
            if last_activity and (current_time - float(last_activity)) > 3600:
                request.session.flush()
            else:
                request.session['last_activity'] = current_time

        response = self.get_response(request)
        return response

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'"
        
        return response

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            user_role = request.user.role
            
            if not self.has_permission(user_role, current_url):
                response = self.handle_unauthorized_access(request)
                return response
        
        return self.get_response(request)
    
    def has_permission(self, role, url_name):
        role_permissions = {
            'ADMIN': ['all'],
            'DOCTOR': ['patient_list', 'appointment_list', 'patient_detail'],
            'NURSE': ['patient_list', 'patient_detail'],
            'STAFF': ['appointment_list', 'patient_registration']
        }
        
        allowed_urls = role_permissions.get(role, [])
        return 'all' in allowed_urls or url_name in allowed_urls
    
    def handle_unauthorized_access(self, request):
        from django.shortcuts import redirect
        from django.contrib import messages
        
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
