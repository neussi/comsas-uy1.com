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
    path('events/register/success/<uuid:uuid>/', views.event_registration_success, name='event_registration_success'),
    
    # Actualités
    path('news/', views.news, name='news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    
    # Galerie
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<int:pk>/', views.gallery_detail, name='gallery_detail'),
    
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

    # ============= NOUVELLES FONCTIONNALITÉS =============
    # Modèles de requêtes
    path('documents/', views.request_documents, name='request_documents'),
    path('documents/download/<int:pk>/', views.download_document, name='download_document'),
    
    # Département
    path('departement/enseignants/', views.department_professors, name='department_professors'),
    path('departement/salles/', views.department_classrooms, name='department_classrooms'),
    path('departement/delegues/', views.department_delegates, name='department_delegates'),
    
    # Blog
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<str:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<str:slug>/like/', views.like_article, name='like_article'),
    
    # Ticketing
    path('tickets/download/<uuid:uuid>/', views.download_ticket, name='download_ticket'),
    path('tickets/verify/<uuid:uuid>/', views.verify_ticket, name='ticket_verify'),
]

if settings.DEBUG:
    urlpatterns += [
        path('test-404/', views.handler404, name='test_404'),
        path('test-500/', views.handler500, name='test_500'),
    ]
