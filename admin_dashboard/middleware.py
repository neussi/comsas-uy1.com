# admin_dashboard/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AdminAuthMiddleware:
    """
    Middleware pour rediriger les utilisateurs non authentifiés 
    vers la page de connexion admin
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs qui ne nécessitent pas d'authentification
        self.public_urls = [
            '/dashboard/auth/login/',
            '/dashboard/auth/register/',
            '/dashboard/auth/password-reset/',
            '/dashboard/auth/logout/',
        ]
    
    def __call__(self, request):
        # Vérifier si on est sur une URL admin
        if request.path.startswith('/dashboard/') and request.path != '/dashboard/':
            
            # Vérifier si l'URL est publique
            is_public = any(request.path.startswith(url) for url in self.public_urls)
            
            if not is_public:
                # Vérifier l'authentification
                if not request.user.is_authenticated:
                    messages.warning(request, 'Vous devez vous connecter pour accéder au dashboard admin.')
                    return redirect(f"{reverse('admin_login')}?next={request.path}")
                
                # Vérifier les permissions
                if not (request.user.is_staff or request.user.is_superuser):
                    messages.error(request, 'Vous n\'avez pas les permissions nécessaires.')
                    return redirect('dashboard')
        
        response = self.get_response(request)
        return response
