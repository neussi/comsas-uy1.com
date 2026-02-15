# admin_dashboard/urls.py
from django.urls import path, include
from . import views
from . import auth_views
from . import certificate_views
from . import badge_views
from . import archive_views

urlpatterns = [

    # ... (existing paths) ...

    # Certificate Management
    path('events/<int:pk>/certificates/', certificate_views.event_certificates_manage, name='admin_event_certificates'),
    path('events/<int:pk>/certificates/generate-all/', certificate_views.generate_all_certificates, name='admin_generate_all_certificates'),
    path('events/<int:pk>/certificates/download-zip/', certificate_views.download_certificates_zip, name='admin_download_certificates_zip'),
    path('registrations/<int:registration_id>/regenerate-certificate/', certificate_views.regenerate_certificate, name='admin_regenerate_certificate'),
    
    # Badge Management
    path('events/<int:pk>/badges/', badge_views.event_badges_manage, name='admin_event_badges'),
    path('events/<int:pk>/badges/generate-all/', badge_views.generate_all_badges, name='admin_generate_all_badges'),
    path('events/<int:pk>/badges/download-zip/', badge_views.download_badges_zip, name='admin_download_badges_zip'),
    path('registrations/<int:registration_id>/regenerate-badge/', badge_views.regenerate_badge, name='admin_regenerate_badge'),

    # ============= DASHBOARD =============
    # Dashboard home (nécessite une connexion)
    path('', views.dashboard_home, name='admin_dashboard_home'),
    # ============= AUTHENTIFICATION =============
    # Pages d'authentification
    path('auth/login/', auth_views.admin_login_view, name='admin_login'),
    path('auth/logout/', auth_views.admin_logout_view, name='admin_logout'),
    path('auth/register/', auth_views.admin_register_view, name='admin_register'),
    path('auth/password-reset/', auth_views.admin_password_reset_view, name='admin_password_reset'),

    
    # ============= GESTION DES MEMBRES =============
    path('members/', views.members_list, name='admin_members_list'),
    path('members/create/', views.MemberCreateView.as_view(), name='admin_member_create'),
    path('members/<int:pk>/', views.member_detail, name='admin_member_detail'),
    path('members/<int:pk>/edit/', views.MemberUpdateView.as_view(), name='admin_member_edit'),
    path('members/<int:pk>/delete/', views.MemberDeleteView.as_view(), name='admin_member_delete'),
    path('members/<int:pk>/approve/', views.member_approve, name='admin_member_approve'),
    path('members/<int:pk>/reject/', views.member_reject, name='admin_member_reject'),
    path('members/<int:pk>/download-card/', views.member_download_card, name='admin_member_download_card'),
    
    # ============= GESTION DES PROJETS =============
    path('projects/', views.projects_list, name='admin_projects_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='admin_project_create'),
    path('projects/<int:pk>/', views.project_detail, name='admin_project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='admin_project_edit'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='admin_project_delete'),
    
    # ============= GESTION DES ÉVÉNEMENTS =============
    path('events/', views.events_list, name='admin_events_list'),
    path('events/create/', views.EventCreateView.as_view(), name='admin_event_create'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='admin_event_edit'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='admin_event_delete'),
    path('events/<int:pk>/reservations/', views.event_registrations, name='admin_event_registrations'),
    path('registrations/<int:pk>/delete/', views.delete_registration, name='admin_delete_registration'),
    path('events/<int:pk>/registrations/export/', views.event_registrations_export_excel, name='admin_export_registrations'),
    path('registrations/<int:pk>/confirm/', views.confirm_registration, name='admin_confirm_registration'),
    
    # ============= GESTION DES ACTUALITÉS =============
    path('news/', views.news_list, name='admin_news_list'),
    path('news/create/', views.NewsCreateView.as_view(), name='admin_news_create'),
    path('news/<int:pk>/edit/', views.NewsUpdateView.as_view(), name='admin_news_edit'),
    path('news/<int:pk>/delete/', views.NewsDeleteView.as_view(), name='admin_news_delete'),
    
    # ============= GESTION DE LA GALERIE =============
    path('gallery/', views.gallery_list, name='admin_gallery_list'),
    path('gallery/create/', views.GalleryCreateView.as_view(), name='admin_gallery_create'),
    path('gallery/<int:pk>/edit/', views.GalleryUpdateView.as_view(), name='admin_gallery_edit'),
    path('gallery/<int:pk>/delete/', views.GalleryDeleteView.as_view(), name='admin_gallery_delete'),
    
    # ============= GESTION DES MESSAGES =============
    path('messages/', views.messages_list, name='admin_messages_list'),
    path('messages/<int:pk>/', views.message_detail, name='admin_message_detail'),
    path('messages/<int:pk>/reply/', views.mark_message_replied, name='admin_mark_message_replied'),
    path('messages/<int:pk>/delete/', views.message_delete, name='admin_message_delete'),
    
    # ============= GESTION DU PARRAINAGE =============
    path('sponsorship/', views.sponsorship_home, name='admin_sponsorship_home'),
    path('sponsorship/session/create/', views.SponsorshipSessionCreateView.as_view(), name='admin_session_create'),
    path('sponsorship/session/<int:pk>/edit/', views.SponsorshipSessionUpdateView.as_view(), name='admin_session_edit'),
    path('sponsorship/session/<int:pk>/delete/', views.SponsorshipSessionDeleteView.as_view(), name='admin_session_delete'),
    path('sponsorship/mentors/', views.sponsorship_mentors, name='admin_sponsorship_mentors'),
    path('sponsorship/mentees/', views.sponsorship_mentees, name='admin_sponsorship_mentees'),
    path('sponsorship/matches/', views.sponsorship_matches, name='admin_sponsorship_matches'),
    path('sponsorship/matches/export/csv/', views.sponsorship_matches_export_csv, name='admin_sponsorship_export_csv'),
    path('sponsorship/matches/export/excel/', views.sponsorship_matches_export_excel, name='admin_sponsorship_export_excel'),
    path('sponsorship/auto-match/', views.sponsorship_auto_match, name='admin_sponsorship_auto_match'),
    
    # ============= PARAMÈTRES DU SITE =============
    path('settings/', views.site_settings, name='admin_site_settings'),

    # ============= GESTION DES CONCOURS =============
    path('contests/', views.contests_home, name='admin_contests_home'),
    path('contests/create/', views.ContestCreateView.as_view(), name='admin_contest_create'),
    path('contests/<int:pk>/', views.contest_detail, name='admin_contest_detail'),
    path('contests/<int:pk>/edit/', views.ContestUpdateView.as_view(), name='admin_contest_edit'),
    path('contests/<int:pk>/delete/', views.ContestDeleteView.as_view(), name='admin_contest_delete'),
    
    # Candidats
    path('contests/<int:contest_pk>/candidates/add/', views.CandidateCreateView.as_view(), name='admin_candidate_create'),
    path('candidates/<int:pk>/edit/', views.CandidateUpdateView.as_view(), name='admin_candidate_edit'),
    path('candidates/<int:pk>/delete/', views.CandidateDeleteView.as_view(), name='admin_candidate_delete'),

    # ============= GESTION DES REQUÊTES =============
    path('requests/', views.requests_list, name='admin_requests_list'),
    path('requests/create/', views.RequestDocumentCreateView.as_view(), name='admin_request_create'),
    path('requests/<int:pk>/edit/', views.RequestDocumentUpdateView.as_view(), name='admin_request_edit'),
    path('requests/<int:pk>/delete/', views.RequestDocumentDeleteView.as_view(), name='admin_request_delete'),

    # ============= GESTION DU DÉPARTEMENT =============
    # Enseignants
    path('department/professors/', views.professors_list, name='admin_professors_list'),
    path('department/professors/create/', views.ProfessorCreateView.as_view(), name='admin_professor_create'),
    path('department/professors/<int:pk>/edit/', views.ProfessorUpdateView.as_view(), name='admin_professor_edit'),
    path('department/professors/<int:pk>/delete/', views.ProfessorDeleteView.as_view(), name='admin_professor_delete'),
    
    # Salles
    path('department/classrooms/', views.classrooms_list, name='admin_classrooms_list'),
    path('department/classrooms/create/', views.ClassroomCreateView.as_view(), name='admin_classroom_create'),
    path('department/classrooms/<int:pk>/edit/', views.ClassroomUpdateView.as_view(), name='admin_classroom_edit'),
    path('department/classrooms/<int:pk>/delete/', views.ClassroomDeleteView.as_view(), name='admin_classroom_delete'),
    
    # Délégués
    path('department/delegates/', views.delegates_list, name='admin_delegates_list'),
    path('department/delegates/create/', views.DelegateCreateView.as_view(), name='admin_delegate_create'),
    path('department/delegates/<int:pk>/edit/', views.DelegateUpdateView.as_view(), name='admin_delegate_edit'),
    path('department/delegates/<int:pk>/delete/', views.DelegateDeleteView.as_view(), name='admin_delegate_delete'),

    # ============= GESTION DU BLOG =============
    path('blog/', views.blog_list, name='admin_blog_list'),
    path('blog/create/', views.BlogArticleCreateView.as_view(), name='admin_blog_create'),
    path('blog/<int:pk>/edit/', views.BlogArticleUpdateView.as_view(), name='admin_blog_edit'),
    path('blog/<int:pk>/delete/', views.BlogArticleDeleteView.as_view(), name='admin_blog_delete'),
    
    # ============= GESTION DES ARCHIVES =============
    path('archives/', archive_views.archive_list, name='admin_archive_list'),
    path('archives/add/', archive_views.archive_create, name='admin_archive_create'),
    path('archives/<int:pk>/edit/', archive_views.archive_edit, name='admin_archive_edit'),
    path('archives/<int:pk>/delete/', archive_views.archive_delete, name='admin_archive_delete'),
]