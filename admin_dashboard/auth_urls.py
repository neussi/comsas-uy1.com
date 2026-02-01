# admin_dashboard/auth_urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import auth_views

urlpatterns = [
    # Authentification personnalisée
    path('login/', auth_views.admin_login_view, name='admin_login'),
    path('logout/', auth_views.admin_logout_view, name='admin_logout'),
    path('register/', auth_views.admin_register_view, name='admin_register'),
    
    # Réinitialisation de mot de passe
    path('password-reset/', auth_views.admin_password_reset_view, name='admin_password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='admin_dashboard/auth/password_reset_done.html'
    ), name='admin_password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='admin_dashboard/auth/password_reset_confirm.html'
    ), name='admin_password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='admin_dashboard/auth/password_reset_complete.html'
    ), name='admin_password_reset_complete'),
]