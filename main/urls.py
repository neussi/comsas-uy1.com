# main/urls.py
from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    
    # À propos
    path('about/', views.about, name='about'),
    path('mandate/', views.mandate, name='mandate'),
    path('profile/', views.member_profile, name='profile'),
    
    # Membres
    path('members/', views.members, name='members'),
    path('membre/<int:pk>/', views.public_member_profile, name='member_profile'),
    path('register/', views.member_registration, name='member_registration'),
    path('register/success/', views.member_registration_success, name='member_registration_success'),
    
    # Projets
    path('projects/', views.projects, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    
    # Événements
    path('events/', views.events, name='events'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/register/success/', views.event_registration_success, name='event_registration_success'),
    
    # Actualités
    path('news/', views.news, name='news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    
    # Galerie
    path('gallery/', views.gallery, name='gallery'),
    
    # Dons
    path('donations/', views.donations, name='donations'),
    
    # Contact
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    
    # WhatsApp redirect
    path('whatsapp/', views.whatsapp_redirect, name='whatsapp_redirect'),

    # Parrainage
    path('parrainage/', views.sponsorship_home, name='sponsorship_home'),
    path('parrainage/devenir-parrain/', views.register_mentor, name='register_mentor'),
    path('parrainage/trouver-parrain/', views.register_mentee, name='register_mentee'),
    path('parrainage/succes/', views.sponsorship_success, name='sponsorship_success'),
    path('parrainage/nos-parrains/', views.list_mentors, name='list_mentors'),
    path('parrainage/binomes/', views.list_matches, name='list_matches'),
    
    # ============= SYSTÈME DE VOTE (CONCOURS) =============
    path('concours/', views.contest_list, name='contest_list'),
    path('concours/<slug:slug>/', views.contest_detail, name='contest_detail'),
    path('concours/<slug:contest_slug>/vote/<int:candidate_id>/', views.vote_candidate, name='vote_candidate'),

]

if settings.DEBUG:
    urlpatterns += [
        path('test-404/', views.handler404, name='test_404'),
        path('test-500/', views.handler500, name='test_500'),
    ]
