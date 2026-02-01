
""" URLs principales du projet aaelbm2_website """
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    
    # Dashboard administrateur personnalisé
    path('dashboard/', include('admin_dashboard.urls')),
    
    # Interface d'administration Django par défaut (nécessaire pour certains namespaces)
    path('admin/', admin.site.urls),
    
    # CKEditor pour l'upload de fichiers
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # URLs d'internationalisation (IMPORTANT : inclut set_language)
    path('i18n/', include('django.conf.urls.i18n')),
]

# ========================= HANDLERS D'ERREURS =========================
handler404 = 'main.views.handler404'
handler500 = 'main.views.handler500'


# URLs avec support multilingue
urlpatterns += i18n_patterns(
    # Site principal (page d'accueil, etc.)
    path('', include('main.urls')),
    
    # Préfixe de langue par défaut
    prefix_default_language=False
)

# Configuration pour le développement
if settings.DEBUG:
    # Servir les fichiers média en développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Configuration de l'admin Django
admin.site.site_header = "COMS.A.S Administration Technique"
admin.site.site_title = "COMS.A.S Admin"
admin.site.index_title = "Administration Technique Django"
