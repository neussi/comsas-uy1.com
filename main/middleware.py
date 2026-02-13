# ============= main/middleware.py =============

from django.shortcuts import render
from django.conf import settings

class CustomErrorMiddleware:
    """
    Middleware pour forcer l'affichage des pages d'erreur personnalisées en développement
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Intercepter les erreurs 404 en mode DEBUG
        if settings.DEBUG and response.status_code == 404:
            return render(request, '404.html', status=404)
        
        return response

    def process_exception(self, request, exception):
        """Intercepter les erreurs 500 en mode DEBUG"""
        if False and settings.DEBUG:
            return render(request, '500.html', status=500)
        return None
