# ============= main/middleware.py (NOUVEAU FICHIER À CRÉER) =============

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
            context = {
                'error_code': '404',
                'error_title': 'Page non trouvée',
                'error_message': 'Désolé, la page que vous recherchez n\'existe pas ou a été déplacée.',
            }
            return render(request, 'errors/404.html', context, status=404)
        
        return response

    def process_exception(self, request, exception):
        """Intercepter les erreurs 500 en mode DEBUG"""
        if False and settings.DEBUG:
            context = {
                'error_code': '500',
                'error_title': 'Erreur serveur',
                'error_message': 'Une erreur interne s\'est produite. Notre équipe technique a été notifiée et travaille à résoudre le problème.',
            }
            return render(request, 'errors/500.html', context, status=500)
        return None
