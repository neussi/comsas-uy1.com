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
    
    # Anciens Présidents
    path('presidents/', views.president_list, name='president_list'),
    path('presidents/<int:president_id>/', views.president_detail, name='president_detail'),

    # Membres
    path('members/', views.members, name='members'),
    path('membre/<int:pk>/', views.public_member_profile, name='member_profile'),
    path('register/', views.member_registration, name='member_registration'),
    path('register/success/', views.member_registration_success, name='member_registration_success'),
    
    # Projets
    path('projects/', views.projects, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    
    # Événements & Activités
    path('events/', views.events, name='events'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/register/success/<uuid:uuid>/', views.event_registration_success, name='event_registration_success'),
    path('evenements/activite/<slug:slug>/', views.activity_detail, name='activity_detail'),
    path('evenements/activite/<int:slug>/', views.activity_detail, name='activity_detail_pk'),
    path('evenements/activites/<slug:slug>/', views.activity_detail, name='activity_detail_alt1'),
    path('events/activity/<slug:slug>/', views.activity_detail, name='activity_detail_alt2'),
    path('events/activite/<slug:slug>/', views.activity_detail, name='activity_detail_alt3'),
    path('evenements/activite/candidature/<uuid:uuid>/', views.activity_application_status, name='activity_application_status'),
    path('events/activity/candidature/<uuid:uuid>/', views.activity_application_status, name='activity_application_status_alt'),
    path('evenements/activite/status/<uuid:uuid>/', views.activity_application_status, name='activity_application_status_status_fr'),
    path('events/activite/status/<uuid:uuid>/', views.activity_application_status, name='activity_application_status_status_en'),
    path('events/activity/status/<uuid:uuid>/', views.activity_application_status, name='activity_application_status_status_en2'),
    path('evenements/activite/candidature/<uuid:uuid>/annuler/', views.activity_payment_cancel, name='activity_payment_cancel'),
    path('api/evenements/activite/payment-status/<str:transaction_id>/', views.api_activity_payment_status, name='api_activity_payment_status'),
    
    # Actualités
    path('news/', views.news, name='news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    
    # Galerie
    path('gallery/', views.gallery, name='gallery'),
    path('galerie/', views.gallery, name='galerie'),
    path('gallery/<int:pk>/', views.gallery_detail, name='gallery_detail'),
    
    # Dons
    path('donations/', views.donations, name='donations'),
    path('donations/initiate/', views.initiate_donation, name='initiate_donation'),
    path('donations/status/<str:external_id>/', views.check_donation_status, name='check_donation_status'),
    
    # Contact
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    
    # WhatsApp redirect
    path('whatsapp/', views.whatsapp_redirect, name='whatsapp_redirect'),

    # Parrainage
    path('parrainage/', views.sponsorship_home, name='sponsorship_home'),
    path('parrainage/devenir-parrain/', views.register_mentor, name='register_mentor'),
    path('parrainage/trouver-parrain/', views.register_mentee, name='register_mentee'),
    path('parrainage/paiement/<uuid:uuid>/', views.sponsorship_payment, name='sponsorship_payment'),
    path('parrainage/paiement/<uuid:uuid>/annuler/', views.sponsorship_payment_cancel, name='sponsorship_payment_cancel'),
    path('parrainage/succes/', views.sponsorship_success, name='sponsorship_success'),
    path('parrainage/succes/<uuid:uuid>/', views.sponsorship_success, name='sponsorship_success_participant'),
    path('parrainage/mon-binome/<uuid:uuid>/', views.sponsorship_my_match, name='sponsorship_my_match'),
    path('parrainage/pass/<uuid:uuid>/telecharger/', views.sponsorship_download_pass, name='sponsorship_download_pass'),
    path('api/parrainage/paiement/status/<uuid:uuid>/', views.sponsorship_payment_status, name='sponsorship_payment_status'),
    path('parrainage/nos-parrains/', views.list_mentors, name='list_mentors'),
    path('parrainage/binomes/', views.list_matches, name='list_matches'),
    # Aliases URL pour le parrainage
    path('sponsorship/', views.sponsorship_home, name='sponsorship_home_alias'),
    path('sponsorship/mentors/', views.list_mentors, name='list_mentors_alias'),
    path('sponsorship/matches/', views.list_matches, name='list_matches_alias'),
    path('sponsorship/register/mentor/', views.register_mentor, name='register_mentor_alias'),
    path('sponsorship/register/mentee/', views.register_mentee, name='register_mentee_alias'),
    path('sponsorship/payment/<uuid:uuid>/', views.sponsorship_payment, name='sponsorship_payment_alias'),
    path('sponsorship/success/<uuid:uuid>/', views.sponsorship_success, name='sponsorship_success_alias'),
    path('sponsorship/my-match/<uuid:uuid>/', views.sponsorship_my_match, name='sponsorship_my_match_alias'),
    path('cofesti/parrainage/devenir-parrain/', views.register_mentor, name='cofesti_register_mentor'),
    path('cofesti/parrainage/trouver-parrain/', views.register_mentee, name='cofesti_register_mentee'),
    path('cofesti/parrainage/paiement/<uuid:uuid>/', views.sponsorship_payment, name='cofesti_sponsorship_payment'),
    path('cofesti/parrainage/mon-binome/<uuid:uuid>/', views.sponsorship_my_match, name='cofesti_sponsorship_my_match'),
    path('cofesti/parrainage/pass/<uuid:uuid>/telecharger/', views.sponsorship_download_pass, name='cofesti_sponsorship_download_pass'),
    
    # ============= SYSTÈME DE VOTE (CONCOURS) =============
    path('concours/', views.contest_list, name='contest_list'),
    path('concours/<slug:slug>/', views.contest_detail, name='contest_detail'),
    path('concours/<slug:contest_slug>/postuler/', views.contest_candidate_register, name='contest_candidate_register'),
    path('concours/<slug:contest_slug>/vote/<int:candidate_id>/', views.vote_candidate, name='vote_candidate'),

    # ============= NOUVELLES FONCTIONNALITÉS =============
    # Modèles de requêtes & Recherche API
    path('documents/', views.request_documents, name='request_documents'),
    path('documents/download/<int:pk>/', views.download_document, name='download_document'),
    path('api/documents/search/', views.api_document_search, name='api_document_search'),
    path('api/chatbot/message/', views.api_chatbot_message, name='api_chatbot_message'),
    
    # Archives (PV, Documents)
    path('archives/', views.archives_list, name='archives'),
    path('archives/<slug:slug>/', views.archive_detail, name='archive_detail'),
    path('archives/<slug:slug>/like/', views.archive_like, name='archive_like'),
    path('archives/<slug:slug>/download/', views.archive_download, name='archive_download'),
    
    # Département
    path('departement/enseignants/', views.department_professors, name='department_professors'),
    path('departement/salles/', views.department_classrooms, name='department_classrooms'),
    path('departement/delegues/', views.department_delegates, name='department_delegates'),
    path('departement/delegues/<slug:slug>/', views.delegate_detail, name='delegate_detail'),
    
    # Blog
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<str:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<str:slug>/like/', views.like_article, name='like_article'),
    
    # Ticketing
    path('tickets/download/<uuid:uuid>/', views.download_ticket, name='download_ticket'),
    path('tickets/verify/', views.verify_ticket, name='ticket_verify_index'),
    path('tickets/verify/<uuid:uuid>/', views.verify_ticket, name='ticket_verify'),
    path('verify/<uuid:uuid>/', views.verify_ticket, name='verify_ticket'),
    path('verify/', views.verify_ticket, name='verify_ticket_index'),

    # ============= J.U.IN 2026 =============
    path('juin/', views.juin_page, name='juin'),
    path('juin/activites/', views.juin_activities_all, name='juin_activities'),
    path('juin/competitions/', views.juin_competitions_status, name='juin_competitions'),
    path('juin/compete/<slug:competition_slug>/', views.juin_competition_register, name='juin_compete'),
    
    path('juin/commissions/', views.juin_commissions_list, name='juin_commissions'),
    path('juin/postuler/', views.juin_apply_commission, name='juin_apply'),
    path('juin/postuler/succes/', views.juin_apply_success, name='juin_apply_success'),
    path('juin/commission/<slug:slug>/', views.juin_commission_detail, name='juin_commission_detail'),
    path('juin/soutenir/', views.juin_donate, name='juin_donate'),
    
    # Concours / Candidats
    path('juin/concours/postuler/', views.juin_miss_mister_register, name='juin_candidate_register'),
    path('juin/concours/candidats/', views.juin_candidates_status, name='juin_candidates'),

    # Membres
    path('membres/', views.members_list, name='members_list'),
    
    path('contact/', views.contact, name='contact'),
    path('juin/guide/', views.juin_guide, name='juin_guide'),
    path('juin/sponsors/', views.juin_sponsors_list, name='juin_sponsors'),
    path('juin/devenir-partenaire/', views.juin_sponsor_request, name='juin_become_partner'),
    
    # Propenta Pay Webhooks & Async checks
    path('webhook', views.propenta_webhook, name='propenta_webhook_raw'),
    path('webhook/', views.propenta_webhook, name='propenta_webhook'),
    path('api/propenta/webhook/', views.propenta_webhook, name='propenta_webhook_api'),
    path('api/payments/webhook/freemopay/', views.propenta_webhook, name='juin_freemopay_webhook'),
    path('api/payments/status/<str:external_id>/', views.juin_payment_status_check, name='juin_payment_status'),
    path('api/vote/initiate/', views.contest_vote_initiate, name='contest_vote_initiate'),
    path('api/vote/status/<str:transaction_id>/', views.vote_status_check, name='vote_status_check'),
    path('api/juin/vote/initiate/', views.juin_vote_initiate, name='juin_vote_initiate'),
    path('api/juin/vote/status/<str:transaction_id>/', views.juin_vote_status_check, name='juin_vote_status_check'),
    path('juin/concours/vote/merci/<str:transaction_id>/', views.juin_vote_complete, name='juin_vote_complete'),
    path('concours/vote/merci/<str:transaction_id>/', views.vote_complete, name='vote_complete'),

    # ============= NOUVELLES FONCTIONNALITÉS 2026 =============
    # Projets
    path('projets/soumettre/', views.project_submit, name='project_submit'),
    path('projets/succes/', views.project_submit_success, name='project_submit_success'),
    
    # Commissions du Club
    path('directions/', views.club_commissions_list, name='club_commissions_list'),
    path('directions/postuler/', views.club_commission_apply, name='club_commission_apply'),
    path('directions/succes/', views.club_commission_apply_success, name='club_commission_apply_success'),
    path('directions/<slug:slug>/', views.club_commission_detail, name='club_commission_detail'),
    path('commissions/', views.club_commissions_list, name='commissions_list'),
    path('commissions/postuler/', views.club_commission_apply, name='commission_apply'),
    path('commissions/succes/', views.club_commission_apply_success, name='commission_apply_success'),
    path('commissions/<slug:slug>/', views.club_commission_detail, name='commission_detail'),
    
    # Ressources & Alumni
    path('ressources/', views.resources_list, name='resources_list'),
    path('ressources/ajouter/', views.resource_upload, name='resource_upload'),
    path('alumni/opportunites/', views.job_board, name='job_board'),
    path('alumni/opportunites/ajouter/', views.job_offer_create, name='job_offer_create'),
    
    # Miss & Mister J.U.IN 2026
    path('juin/miss-mister/', views.juin_miss_mister_contest, name='juin_miss_mister'),
    path('juin/miss-mister/candidat/<int:pk>/', views.juin_candidate_detail, name='juin_candidate_detail'),
    path('juin/miss-mister/resultats/', views.juin_contest_results, name='juin_contest_results'),
    
    # Portfolios
    path('portfolio/<slug:slug>/', views.member_portfolio, name='member_portfolio'),

    # ============= COFESTI (FESTI-NOËL COMSAS) =============
    path('cofesti/', views.cofesti_home, name='cofesti_home'),
    path('cofesti/<int:year>/', views.cofesti_home, name='cofesti_home_year'),
    path('cofesti/miss-master/', views.cofesti_miss_master, name='cofesti_miss_master'),
    path('cofesti/miss-master/postuler/', views.cofesti_candidate_apply, name='cofesti_candidate_apply'),
    path('cofesti/<int:year>/miss-master/', views.cofesti_miss_master, name='cofesti_miss_master_year'),
    path('cofesti/<int:year>/miss-master/postuler/', views.cofesti_candidate_apply, name='cofesti_candidate_apply_year'),
    path('cofesti/sports/', views.cofesti_sports, name='cofesti_sports'),
    path('cofesti/sport/', views.cofesti_sports, name='cofesti_sport_alias'),
    path('cofesti/<int:year>/sports/', views.cofesti_sports, name='cofesti_sports_year'),
    path('cofesti/<int:year>/sport/', views.cofesti_sports, name='cofesti_sports_year_alias'),
    path('cofesti/pique-niques/', views.cofesti_picnics, name='cofesti_picnics'),
    path('cofesti/piqueniques/', views.cofesti_picnics, name='cofesti_picnics_alias1'),
    path('cofesti/picnics/', views.cofesti_picnics, name='cofesti_picnics_alias2'),
    path('cofesti/<int:year>/pique-niques/', views.cofesti_picnics, name='cofesti_picnics_year'),
    path('cofesti/<int:year>/piqueniques/', views.cofesti_picnics, name='cofesti_picnics_year_alias1'),
    path('cofesti/<int:year>/picnics/', views.cofesti_picnics, name='cofesti_picnics_year_alias2'),
    path('cofesti/parrainage/', views.cofesti_sponsorship, name='cofesti_sponsorship'),
    path('cofesti/soiree-parrainage/', views.cofesti_sponsorship, name='cofesti_sponsorship_alias0'),
    path('cofesti/parrainage-gala/', views.cofesti_sponsorship, name='cofesti_sponsorship_alias1'),
    path('cofesti/gala/', views.cofesti_sponsorship, name='cofesti_sponsorship_alias2'),
    path('cofesti/<int:year>/parrainage/', views.cofesti_sponsorship, name='cofesti_sponsorship_year'),
    path('cofesti/<int:year>/soiree-parrainage/', views.cofesti_sponsorship, name='cofesti_sponsorship_year_alias0'),
    path('cofesti/<int:year>/parrainage-gala/', views.cofesti_sponsorship, name='cofesti_sponsorship_year_alias1'),
    path('cofesti/<int:year>/gala/', views.cofesti_sponsorship, name='cofesti_sponsorship_year_alias2'),
    path('cofesti/comite/', views.cofesti_committee, name='cofesti_committee'),
    path('cofesti/committee/', views.cofesti_committee, name='cofesti_committee_alias'),
    path('cofesti/<int:year>/comite/', views.cofesti_committee, name='cofesti_committee_year'),
    path('cofesti/<int:year>/committee/', views.cofesti_committee, name='cofesti_committee_year_alias'),

    # Actions & API COFESTI
    path('api/cofesti/vote/initiate/', views.cofesti_vote_initiate, name='cofesti_vote_initiate'),
    path('api/cofesti/vote/status/<str:transaction_id>/', views.cofesti_vote_status_check, name='cofesti_vote_status_check'),
    path('cofesti/vote/merci/<str:transaction_id>/', views.cofesti_vote_complete, name='cofesti_vote_complete'),
    path('cofesti/equipe/inscrire/', views.cofesti_team_register, name='cofesti_team_register'),
    path('cofesti/pique-nique/reserver/', views.cofesti_picnic_book, name='cofesti_picnic_book'),
    path('cofesti/parrainage/inscrire/', views.cofesti_sponsorship_register, name='cofesti_sponsorship_register'),
]

if settings.DEBUG:
    urlpatterns += [
        path('test-404/', views.handler404, name='test_404'),
        path('test-500/', views.handler500, name='test_500'),
    ]
