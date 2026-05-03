from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import json
import uuid
import logging
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .models import (
    Member, Project, Event, EventRegistration, 
    News, Gallery, GalleryAlbum, Contact, SiteSettings,
    SponsorshipSession, Mentor, Mentee, Match,
    Contest, Candidate, Vote, Archive, ArchiveComment,
    JUINEdition, JUINCommission, JUINCommissionApplication, JUINCompetition,
    JUINActivity, JUINDonation, JUINSponsor, JUINTeam,
    ClubCommission, ClubCommissionApplication, ProjectSubmission
)
from .forms import (
    MemberRegistrationForm, EventRegistrationForm, 
    ContactForm, JUINCommissionApplicationForm, 
    JUINDonationForm, JUINSponsorRequestForm
)
from .freemopay_service import FreemopayService

from .utils import generate_ticket
from django.db.models import Q

def home(request):
    """Page d'accueil"""
    # Récupérer les paramètres du site
    site_settings = SiteSettings.objects.first()
    
    # Événements en vedette (prochains)
    featured_events = Event.objects.filter(
        is_featured=True,
        is_active=True,
        date_event__gte=timezone.now()
    )[:3]
    
    # Projets en vedette
    featured_projects = Project.objects.filter(is_featured=True)[:3]
    
    # Actualités récentes
    recent_news = News.objects.filter(is_published=True)[:4]
    
    # Galerie en vedette
    featured_gallery = Gallery.objects.filter(is_featured=True)[:6]
    
    # Membres du bureau
    bureau_members = Member.objects.filter(
        is_active=True
    )
    
    # Statistiques pour la home
    total_members = Member.objects.filter(is_active=True).count()
    completed_projects = Project.objects.filter(status='completed').count()
    
    # Concours actifs pour la home
    active_contests = Contest.objects.filter(is_active=True).order_by('-start_date')[:3]
    
    # Edition JUIN actuelle
    juin_edition = JUINEdition.objects.filter(is_active=True).first()
    
    context = {
        'site_settings': site_settings,
        'featured_events': featured_events,
        'featured_projects': featured_projects,
        'recent_news': recent_news,
        'featured_gallery': featured_gallery,
        'bureau_members': bureau_members,
        'total_members': total_members,
        'completed_projects': completed_projects,
        'juin_edition': juin_edition,
        'active_contests': active_contests,
    }

    
    return render(request, 'main/home.html', context)

def about(request):
    """Page à propos"""
    site_settings = SiteSettings.objects.first()
    
    # Statistiques
    total_members = Member.objects.filter(is_active=True).count()
    completed_projects = Project.objects.filter(status='completed').count()
    ongoing_projects = Project.objects.filter(status='ongoing').count()
    
    context = {
        'site_settings': site_settings,
        'total_members': total_members,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,
    }
    
    return render(request, 'main/about.html', context)

def mandate(request):
    """Page du Plan d'Action 2025-2026"""
    site_settings = SiteSettings.objects.first()
    
    # Récupérer les membres du bureau
    bureau_members = Member.objects.filter(
        member_type='bureau',
        is_active=True
    ).order_by('poste_bureau')
    
    context = {
        'site_settings': site_settings,
        'page_title': "Plan d'Action 2025-2026",
        'bureau_members': bureau_members,
    }
    return render(request, 'main/mandate.html', context)

@login_required
def member_profile(request):
    """Page de profil du membre connecté"""
    try:
        member = request.user.member
    except Member.DoesNotExist:
        messages.warning(request, "Vous n'avez pas encore de profil membre. Veuillez compléter votre inscription.")
        return redirect('register')
        
    return render(request, 'main/profile.html', {'member': member})

def public_member_profile(request, pk):
    """Profil public d'un membre (scanned via QR Code)"""
    member = get_object_or_404(Member, pk=pk)
    
    if not member.is_active:
        # Optionnel: afficher une page "Membre inactif" ou rediriger
        messages.error(request, "Ce profil n'est pas actif.")
        return redirect('home')
        
    return render(request, 'main/member_profile.html', {'member': member})


def members(request):
    """Page des membres"""
    # Membres du bureau
    from django.db.models import Case, When, Value, IntegerField
    
    bureau_order = Case(
        When(poste_bureau__iexact='Président', then=Value(1)),
        When(poste_bureau__iexact='Vice-Président 1', then=Value(2)),
        When(poste_bureau__iexact='Vice-Président 2', then=Value(3)),
        When(poste_bureau__iexact='Secrétaire Général', then=Value(4)),
        When(poste_bureau__iexact='Secrétaire', then=Value(5)),
        When(poste_bureau__iexact='Secrétaire Adjoint', then=Value(6)),
        When(poste_bureau__iexact='Trésorier', then=Value(7)),
        When(poste_bureau__iexact='Censeur', then=Value(8)),
        When(poste_bureau__iexact='Censeur Adjoint', then=Value(9)),
        When(poste_bureau__iexact='Commissaire aux Comptes 1', then=Value(10)),
        When(poste_bureau__iexact='Commissaire aux Comptes 2', then=Value(11)),
        When(poste_bureau__iexact='Conseiller Technique', then=Value(12)),
        default=Value(20),
        output_field=IntegerField(),
    )
    
    bureau_members = Member.objects.filter(
        member_type='bureau',
        is_active=True
    ).order_by(bureau_order, 'nom_prenom')    
    # Membres fondateurs
    founder_members = Member.objects.filter(
        member_type='founder',
        is_active=True
    )
    
    # Conseillers
    conseil_members = Member.objects.filter(
        member_type='conseil',
        is_active=True
    )
    general_members = Member.objects.filter(
        is_active=True
    )
    # Membres influents (avec bio)
    influential_members = Member.objects.filter(
        is_active=True,
        bio__isnull=False
    ).exclude(bio='')[:8]
    
    context = {
        'bureau_members': bureau_members,
        'founder_members': founder_members,
        'conseil_members': conseil_members,
        'influential_members': influential_members,
        'general_members': general_members,

    }
    
    return render(request, 'main/members.html', context)



def member_registration(request):
    """Inscription d'un nouveau membre"""
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST, request.FILES)  # Ajouter request.FILES
        if form.is_valid():
            member = form.save(commit=False)
            member.is_active = False  # En attente de validation par l'administration
            member.save()
            
            messages.success(
                request, 
                _('Votre demande d\'adhésion a été envoyée avec succès! '
                  'Vous recevrez une confirmation par email une fois votre compte validé.')
            )
            
            # Envoyer un email de notification à l'administration
            try:
                # Email pour l'administration
                admin_subject = 'Nouvelle demande d\'adhésion - COMS.A.S'
                # Email HTML pour admin
                from django.core.mail import EmailMultiAlternatives
                
                html_content = render_to_string('emails/membership_request_notification.html', {
                    'nom_prenom': member.nom_prenom,
                    'matricule': member.matricule,
                    'email': member.email,
                    'telephone': member.telephone,
                    'lieu_naissance': member.lieu_naissance,
                    'date_naissance': member.date_naissance,
                    'photo_status': 'Oui' if member.photo else 'Non',
                    'admin_url': request.build_absolute_uri('/admin-dashboard/members/'),
                })
                
                admin_message = f"""Nouvelle demande d'adhésion reçue:
                
Nom et Prénom: {member.nom_prenom}
Matricule: {member.matricule}
Email: {member.email}
Téléphone: {member.telephone}
Lieu de naissance: {member.lieu_naissance}
Date de naissance: {member.date_naissance}
Photo: {'Oui' if member.photo else 'Non'}
                
Veuillez vous connecter à l'administration pour valider ou rejeter cette demande."""
                
                email = EmailMultiAlternatives(
                    admin_subject,
                    admin_message,
                    settings.EMAIL_HOST_USER,
                    [settings.ASSOCIATION_EMAIL],
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=True)
                
                # Email de confirmation pour le membre
                member_subject = 'Demande d\'adhésion reçue - COMS.A.S'
                
                # Render HTML
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                from django.core.mail import EmailMultiAlternatives
                
                context = {
                    'member': member,
                    'site_url': settings.SITE_URL,
                }
                
                html_content = render_to_string('emails/registration_confirmation.html', context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    member_subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [member.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=True)
                

            except Exception as e:
                # Logger l'erreur mais ne pas bloquer l'inscription
                print(f"Erreur lors de l'envoi de l'email: {e}")
                pass
            
            return redirect('member_registration_success')
    else:
        form = MemberRegistrationForm()
    
    context = {
        'form': form,
        'page_title': _('Devenir membre'),
    }
    return render(request, 'main/member_registration.html', context)


def member_registration_success(request):
    """Page de confirmation après inscription"""
    context = {
        'page_title': _('Demande envoyée'),
    }
    return render(request, 'main/member_registration_success.html', context)

    

def projects(request):
    """Page des projets"""
    # Projets en cours
    ongoing_projects = Project.objects.filter(status='ongoing')
    
    # Projets terminés
    completed_projects = Project.objects.filter(status='completed')
    
    # Projets en planification
    planning_projects = Project.objects.filter(status='planning')
    
    context = {
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects,
        'planning_projects': planning_projects,
    }
    
    return render(request, 'main/projects.html', context)

def project_detail(request, pk):
    """Détail d'un projet"""
    project = get_object_or_404(Project, pk=pk)
    context = {'project': project}
    return render(request, 'main/project_detail.html', context)

def events(request):
    """Page des événements"""
    # Événements à venir
    upcoming_events = Event.objects.filter(
        date_event__gte=timezone.now(),
        is_active=True
    ).order_by('date_event')
    
    # Événements passés
    past_events = Event.objects.filter(
        date_event__lt=timezone.now()
    ).order_by('-date_event')[:6]
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    
    return render(request, 'main/events.html', context)

def event_detail(request, pk):
    """Détail d'un événement"""
    event = get_object_or_404(Event, pk=pk)
    
    # Vérifier si l'inscription est ouverte
    can_register = event.is_registration_open
    
    if request.method == 'POST' and can_register:
        form = EventRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            
            # Vérifier si pas déjà inscrit
            existing = EventRegistration.objects.filter(
                event=event,
                email=registration.email
            ).first()
            
            if existing:
                messages.warning(request, _('Vous êtes déjà inscrit à cet événement.'))
            else:
                registration.is_confirmed = True
                registration.save()
                messages.success(request, _('Votre inscription a été enregistrée avec succès!'))
                
                # Générer le ticket
                try:
                    generate_ticket(registration)
                except Exception as e:
                    print(f"Erreur génération ticket: {e}")

                # Envoyer notification HTML avec pièces jointes
                try:
                    from django.template.loader import render_to_string
                    from django.core.mail import EmailMultiAlternatives
                    
                    html_content = render_to_string('emails/event_registration_confirmation.html', {
                        'participant_name': registration.nom_prenom,
                        'event_title': event.title_fr,
                        'event_date': event.date_event,
                        'event_location': event.location,
                    })
                    
                    subject = f'Confirmation inscription - {event.title_fr}'
                    text_content = f'Bonjour {registration.nom_prenom},\n\nVotre inscription à l\'événement "{event.title_fr}" a bien été enregistrée.\n\nVous trouverez votre ticket en pièce jointe.\n\nCordialement,\nL\'équipe COMS.A.S'
                    
                    email = EmailMultiAlternatives(
                        subject,
                        text_content,
                        settings.EMAIL_HOST_USER,
                        [registration.email],
                    )
                    email.attach_alternative(html_content, "text/html")
                    
                    if registration.ticket_pdf:
                        email.attach_file(registration.ticket_pdf.path)
                    email.send(fail_silently=True)
                except Exception as e:
                    print(f"Erreur envoi email: {e}")
                
                return redirect('event_registration_success', uuid=registration.uuid)
    else:
        form = EventRegistrationForm()
    
    # Participants
    participants = event.eventregistration_set.filter(is_confirmed=True).order_by('nom_prenom')
    
    # Galerie
    images = []
    if event.gallery_album:
        images = event.gallery_album.images.all()

    context = {
        'event': event,
        'form': form,
        'can_register': can_register,
        'participants': participants,
        'images': images,
    }
    
    return render(request, 'main/event_detail.html', context)

def verify_ticket(request, uuid=None):
    """
    Vérifie l'authenticité d'un ticket ou d'une attestation via son UUID.
    """
    registration = None
    if uuid:
        registration = get_object_or_404(EventRegistration, uuid=uuid)
    
    return render(request, 'main/ticket_verify.html', {
        'registration': registration,
        'event': registration.event if registration else None,
        'uuid': uuid
    })

def event_registration_success(request, uuid):
    """Page de confirmation d'inscription à un événement"""
    registration = get_object_or_404(EventRegistration, uuid=uuid)
    context = {
        'event': registration.event,
        'registration': registration
    }
    return render(request, 'main/event_registration_success.html', context)

def gallery(request):
    """Page galerie / multimédia (Albums)"""
    albums = GalleryAlbum.objects.all().order_by('-event_date')
    
    paginator = Paginator(albums, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj
    }
    return render(request, 'main/gallery.html', context)

def gallery_detail(request, pk):
    """Détail d'un album photo"""
    album = get_object_or_404(GalleryAlbum, pk=pk)
    images = album.images.all()
    
    context = {
        'album': album,
        'images': images
    }
    return render(request, 'main/gallery_detail.html', context)

def news(request):
    """Page des actualités"""
    news_list = News.objects.filter(is_published=True)
    
    # Pagination
    paginator = Paginator(news_list, 9)
    page_number = request.GET.get('page')
    news_page = paginator.get_page(page_number)
    
    context = {'news_page': news_page}
    return render(request, 'main/news.html', context)

def news_detail(request, pk):
    """Détail d'une actualité"""
    article = get_object_or_404(News, pk=pk, is_published=True)
    
    # Articles connexes
    related_news = News.objects.filter(
        is_published=True
    ).exclude(pk=pk)[:3]
    
    context = {
        'article': article,
        'related_news': related_news,
    }
    
    return render(request, 'main/news_detail.html', context)



def donations(request):
    """Page des dons et cotisations"""
    # Projets nécessitant des fonds
    funded_projects = Project.objects.filter(
        status__in=['planning', 'ongoing']
    ).order_by('-is_featured', '-created_at')
    
    from .forms import JUINDonationForm
    context = {
        'funded_projects': funded_projects,
        'whatsapp_president': settings.WHATSAPP_PRESIDENT,
        'whatsapp_treasurer_mtn': settings.WHATSAPP_TREASURER_MTN,
        'whatsapp_treasurer_orange': settings.WHATSAPP_TREASURER_ORANGE,
        'donate_form': JUINDonationForm(),
    }
    
    return render(request, 'main/donations.html', context)

def contact(request):
    """Page de contact"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            messages.success(request, _('Votre message a été envoyé avec succès! Nous vous répondrons bientôt.'))
            
            # Envoyer notification par email HTML
            try:
                from django.template.loader import render_to_string
                from django.core.mail import EmailMultiAlternatives
                from django.utils import timezone
                
                html_content = render_to_string('emails/contact_notification.html', {
                    'nom_prenom': contact_message.nom_prenom,
                    'email': contact_message.email,
                    'sujet': contact_message.sujet,
                    'message': contact_message.message,
                    'date_envoi': timezone.now(),
                })
                
                email = EmailMultiAlternatives(
                    f'Nouveau message de contact - {contact_message.sujet}',
                    f'De: {contact_message.nom_prenom} ({contact_message.email})\n\nMessage:\n{contact_message.message}',
                    settings.EMAIL_HOST_USER,
                    [settings.ASSOCIATION_EMAIL],
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=True)
            except Exception as e:
                print(f"Erreur envoi email: {e}")
            
            return redirect('contact_success')
    else:
        form = ContactForm()
    
    context = {'form': form}
    return render(request, 'main/contact.html', context)

def contact_success(request):
    """Page de confirmation de contact"""
    return render(request, 'main/contact_success.html')

@csrf_exempt
def whatsapp_redirect(request):
    """Redirection vers WhatsApp"""
    contact_type = request.GET.get('type', 'president')
    message = request.GET.get('message', '')
    
    if contact_type == 'president':
        phone = settings.WHATSAPP_PRESIDENT
    elif contact_type == 'treasurer_mtn':
        phone = settings.WHATSAPP_TREASURER_MTN
    elif contact_type == 'treasurer_orange':
        phone = settings.WHATSAPP_TREASURER_ORANGE
    else:
        phone = settings.WHATSAPP_PRESIDENT
    
    # Nettoyer le numéro de téléphone
    phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    
    whatsapp_url = f"https://wa.me/{phone}"
    if message:
        whatsapp_url += f"?text={message}"
    
    return redirect(whatsapp_url)

def handler404(request, exception=None):
    """Page d'erreur 404 personnalisée"""
    return render(request, '404.html', status=404)


def handler500(request):
    """Page d'erreur 500 personnalisée"""
    return render(request, '500.html', status=500)


# ------------- SPONSORSHIP VIEWS -------------
from .models import SponsorshipSession, Mentor, Mentee
from .forms import MentorRegistrationForm, MenteeRegistrationForm

def sponsorship_home(request):
    """Page d'accueil du parrainage"""
    active_session = SponsorshipSession.objects.filter(is_active=True).first()
    
    context = {
        'active_session': active_session,
    }
    return render(request, 'main/sponsorship/home.html', context)

def list_mentors(request):
    """Liste des parrains (pour information)"""
    mentors = Mentor.objects.filter(session__is_active=True).order_by('specialty', 'first_name')
    return render(request, 'main/sponsorship/mentor_list.html', {'mentors': mentors})

def register_mentor(request):
    """Inscription Parrain"""
    active_session = SponsorshipSession.objects.filter(is_active=True).first()
    if not active_session:
        messages.error(request, "Aucune session de parrainage n'est active pour le moment.")
        return redirect('sponsorship_home')

    if request.method == 'POST':
        form = MentorRegistrationForm(request.POST)
        if form.is_valid():
            mentor = form.save(commit=False)
            mentor.session = active_session
            # Vérifier unicité email pour cette session
            if Mentor.objects.filter(email=mentor.email, session=active_session).exists():
                messages.error(request, "Cet email est déjà enregistré comme parrain pour cette session.")
            else:
                mentor.save()
                messages.success(request, "Votre inscription en tant que Parrain a été enregistrée avec succès !")
                return redirect('sponsorship_success')
    else:
        form = MentorRegistrationForm()

    return render(request, 'main/sponsorship/register_mentor.html', {'form': form, 'session': active_session})

def register_mentee(request):
    """Inscription Filleul"""
    active_session = SponsorshipSession.objects.filter(is_active=True).first()
    if not active_session:
        messages.error(request, "Aucune session de parrainage n'est active pour le moment.")
        return redirect('sponsorship_home')

    if request.method == 'POST':
        form = MenteeRegistrationForm(request.POST)
        if form.is_valid():
            mentee = form.save(commit=False)
            mentee.session = active_session
            # Vérifier unicité email pour cette session
            if Mentee.objects.filter(email=mentee.email, session=active_session).exists():
                messages.error(request, "Cet email est déjà enregistré comme filleul pour cette session.")
            else:
                mentee.save()
                messages.success(request, "Votre demande de parrainage a été enregistrée avec succès ! L'attribution se fera bientôt.")
                return redirect('sponsorship_success')
    else:
        form = MenteeRegistrationForm()

    return render(request, 'main/sponsorship/register_mentee.html', {'form': form, 'session': active_session})

def sponsorship_success(request):
    return render(request, 'main/sponsorship/success.html')

def list_mentors(request):
    """Liste publique des parrains"""
    active_session = SponsorshipSession.objects.filter(is_active=True).first()
    
    mentors = Mentor.objects.filter(session=active_session).order_by('first_name')
    specialty = request.GET.get('specialty')
    
    if specialty:
        mentors = mentors.filter(specialty=specialty)
        
    context = {
        'mentors': mentors,
        'specialties': Mentor.SPECIALTY_CHOICES,
        'current_specialty': specialty,
        'session': active_session,
    }
    return render(request, 'main/sponsorship_mentors.html', context)

def list_matches(request):
    """Liste publique des binômes (Matches)"""
    active_session = SponsorshipSession.objects.filter(is_active=True).first()
    
    matches = Match.objects.filter(
        session=active_session, 
        is_active=True
    ).select_related('mentor', 'mentee').order_by('mentor__first_name')
    
    context = {
        'matches': matches,
        'session': active_session,
    }
    return render(request, 'main/sponsorship_matches.html', context)


# ============= SYSTÈME DE VOTE (CONCOURS) =============

def contest_list(request):
    """Liste des concours"""
    active_contests = Contest.objects.filter(is_active=True).order_by('-start_date')
    past_contests = Contest.objects.filter(is_active=False).order_by('-end_date')
    
    context = {
        'active_contests': active_contests,
        'past_contests': past_contests,
    }
    return render(request, 'main/contests/list.html', context)

def contest_detail(request, slug):
    """Page de détail d'un concours et vote"""
    contest = get_object_or_404(Contest, slug=slug)
    candidates = contest.candidates.filter(status='approved').order_by('-votes_count', 'name')
    
    # Statistics Calculation
    total_votes = sum(c.votes_count for c in candidates)
    
    # Prepare Chart Data
    chart_labels = []
    chart_data = []
    
    for candidate in candidates:
        if total_votes > 0:
            candidate.percentage = round((candidate.votes_count / total_votes) * 100, 1)
        else:
            candidate.percentage = 0
            
        chart_labels.append(candidate.name)
        chart_data.append(candidate.votes_count)
    
    # Vérifier si l'utilisateur a déjà voté (ou si le vote est checké via IP/Matricule dans la vue AJAX, ici c'est pour l'affichage)
    # On garde la logique simple : si session_key a voté
    has_voted = False
    if contest.is_open():
        ip = get_client_ip(request)
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            
        # Check basic uniqueness via Session/IP purely for UI state (button disabled)
        # Note: True security is in the POST view with Matricule
        has_voted = Vote.objects.filter(
            contest=contest,
            ip_address=ip,
            session_key=session_key
        ).exists()
    
    context = {
        'contest': contest,
        'candidates': candidates,
        'has_voted': has_voted,
        'total_votes': total_votes,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'main/contests/detail.html', context)

@csrf_exempt
def vote_candidate(request, contest_slug, candidate_id):
    """Traitement du vote (AJAX) - Sécurisé par Email et Matricule"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
        
    try:
        data = json.loads(request.body)
        email = data.get('email')
        matricule = data.get('matricule')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données invalides'}, status=400)

    if not email or not matricule:
        return JsonResponse({'error': 'Veuillez saisir votre email et votre matricule.'}, status=400)

    # Nettoyage
    email = email.lower().strip()
    matricule = matricule.upper().strip()

    contest = get_object_or_404(Contest, slug=contest_slug)
    candidate = get_object_or_404(Candidate, pk=candidate_id, contest=contest)
    
    # 1. Vérifier si le concours est ouvert
    if not contest.is_open():
        return JsonResponse({'error': 'Le vote est clos pour ce concours (Date expirée ou inactif).'}, status=403)
        
    # 2. VÉRIFICATION DU MEMBRE
    # RETIRÉ: Le vote est ouvert à tous les étudiants, pas seulement les membres inscrits.
    # On vérifie uniquement l'unicité du vote ci-dessous.

    # 3. VÉRIFICATION DOUBLE VOTE
    # Par Email
    if Vote.objects.filter(contest=contest, voter_email=email).exists():
        return JsonResponse({'error': 'Vous avez déjà voté pour ce concours (Email utilisé).'}, status=403)
        
    # Par Matricule
    if Vote.objects.filter(contest=contest, voter_matricule=matricule).exists():
        return JsonResponse({'error': 'Ce matricule a déjà servi à voter pour ce concours.'}, status=403)

    # 4. Enregistrer le vote
    ip = get_client_ip(request)
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    Vote.objects.create(
        contest=contest,
        candidate=candidate,
        ip_address=ip,
        session_key=session_key,
        voter_email=email,
        voter_matricule=matricule,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # 5. Mettre à jour le compteur (denormalized)
    candidate.votes_count += 1
    candidate.save()
    
    return JsonResponse({'success': True, 'new_count': candidate.votes_count})

def get_client_ip(request):
    """Récupère l'IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# =============================================================================
# NOUVELLES VUES (REQ 2026-02-12)
# =============================================================================

from .models import RequestDocument, Professor, Classroom, Delegate, BlogArticle, PastPresident

def request_documents(request):
    """Liste des modèles de requêtes"""
    documents = RequestDocument.objects.all().order_by('title')
    
    # Filtrer par type si demandé
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(doc_type=doc_type)
        
    context = {
        'documents': documents,
        'current_type': doc_type,
    }
    return render(request, 'main/requests/list.html', context)

def download_document(request, pk):
    """Télécharger un document et incrémenter le compteur"""
    document = get_object_or_404(RequestDocument, pk=pk)
    document.downloads_count += 1
    document.save()
    
    if document.file:
        return redirect(document.file.url)
    return redirect('request_documents')

def department_professors(request):
    """Liste des enseignants"""
    professors = Professor.objects.filter(is_active=True).order_by('name')
    context = {'professors': professors}
    return render(request, 'main/department/professors.html', context)

def department_classrooms(request):
    """Liste des salles de cours"""
    classrooms = Classroom.objects.all().order_by('name')
    context = {'classrooms': classrooms}
    return render(request, 'main/department/classrooms.html', context)

def department_delegates(request):
    """Liste des délégués"""
    delegates = Delegate.objects.all().order_by('level', 'name')
    
    # Regrouper par niveau pour l'affichage
    # Ou on peut le faire dans le template avec {% regroup %}
    
    context = {'delegates': delegates}
    return render(request, 'main/department/delegates.html', context)

def blog_list(request):
    """Liste des articles de blog"""
    articles_list = BlogArticle.objects.filter(is_published=True).order_by('-published_at')
    
    # Filtrer par catégorie
    category = request.GET.get('category')
    if category:
        articles_list = articles_list.filter(category=category)
    
    # Pagination
    paginator = Paginator(articles_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_category': category,
        'categories': BlogArticle.CATEGORIES,
    }
    return render(request, 'main/blog/list.html', context)

def blog_detail(request, slug):
    """Détail d'un article de blog"""
    article = get_object_or_404(BlogArticle, slug=slug, is_published=True)
    
    # Incrémenter les vues (simple)
    # Idéalement utiliser session pour éviter doublons
    session_key = f'viewed_article_{article.pk}'
    if not request.session.get(session_key, False):
        article.views_count += 1
        article.save()
        request.session[session_key] = True
    
    # Articles similaires
    related_articles = BlogArticle.objects.filter(
        category=article.category, 
        is_published=True
    ).exclude(pk=article.pk)[:3]
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'main/blog/detail.html', context)

@csrf_exempt
def like_article(request, slug):
    """J'aime un article (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    article = get_object_or_404(BlogArticle, slug=slug)
    
    # Simple suppression de doublon par session
    session_key = f'liked_article_{article.pk}'
    if not request.session.get(session_key, False):
        article.likes_count += 1
        article.save()
        request.session[session_key] = True
        return JsonResponse({'success': True, 'likes_count': article.likes_count})
    
    return JsonResponse({'success': False, 'error': 'Vous avez déjà aimé cet article.'})

def download_ticket(request, uuid):
    """Télécharger le ticket PDF"""
    registration = get_object_or_404(EventRegistration, uuid=uuid)
    if registration.ticket_pdf:
        response = FileResponse(registration.ticket_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{registration.event.id}.pdf"'
        return response
    else:
        # Regenerate if missing
        try:
            generate_ticket(registration)
            return redirect('download_ticket', uuid=uuid)
        except:
            raise Http404("Ticket introuvable")

def verify_ticket(request, uuid):
    """Vérifier la validité d'un ticket via QR Code"""
    try:
        registration = EventRegistration.objects.get(uuid=uuid)
        context = {'registration': registration, 'valid': True}
    except EventRegistration.DoesNotExist:
        context = {'valid': False}
    
    return render(request, 'main/ticket_verify.html', context)

def archives_list(request):
    """Page des archives (PV, documents)"""
    # Filtres
    selected_level = request.GET.get('level')
    selected_year = request.GET.get('year')
    category_filter = request.GET.get('category')
    
    archives = Archive.objects.all().order_by('-academic_year', '-created_at')
    
    if selected_level:
        archives = archives.filter(level=selected_level)
    
    if selected_year:
        archives = archives.filter(academic_year=selected_year)
        
    if category_filter:
        archives = archives.filter(category=category_filter)
        
    # Listes pour les filtres
    years = Archive.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')
    
    context = {
        'archives': archives,
        'level_choices': Archive.LEVEL_CHOICES,
        'category_choices': Archive.CATEGORY_CHOICES,
        'available_years': years,
        'selected_level': selected_level,
        'selected_year': selected_year,
        'selected_category': category_filter,
    }
    return render(request, 'main/archives.html', context)

def archive_detail(request, slug):
    """Détail d'une archive"""
    archive = get_object_or_404(Archive, slug=slug)
    
    # Incrémenter les vues (si pas déjà vu dans cette session)
    session_key = f'viewed_archive_{archive.pk}'
    if not request.session.get(session_key, False):
        archive.views_count += 1
        archive.save()
        request.session[session_key] = True
    
    # Gestion des commentaires (POST)
    if request.method == 'POST':
        author_name = request.POST.get('author_name', 'Étudiant Anonyme').strip() or 'Étudiant Anonyme'
        content = request.POST.get('content', '').strip()
        
        if content:
            ArchiveComment.objects.create(
                archive=archive,
                author_name=author_name,
                content=content
            )
            messages.success(request, "Merci ! Votre commentaire a été ajouté.")
            return redirect('archive_detail', slug=slug)
            
    comments = archive.comments.all().order_by('-created_at')
    
    # Archives similaires (même niveau)
    related_archives = Archive.objects.filter(
        level=archive.level
    ).exclude(pk=archive.pk)[:3]
    
    context = {
        'archive': archive,
        'comments': comments,
        'related_archives': related_archives,
        'is_liked': request.session.get(f'liked_archive_{archive.pk}', False)
    }
    return render(request, 'main/archive_detail.html', context)

@csrf_exempt
def archive_like(request, slug):
    """Liker une archive (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        archive = get_object_or_404(Archive, slug=slug)
        
        session_key = f'liked_archive_{archive.pk}'
        if not request.session.get(session_key, False):
            archive.likes_count += 1
            archive.save()
            request.session[session_key] = True
            return JsonResponse({'success': True, 'likes_count': archive.likes_count, 'liked': True})
        
        return JsonResponse({'success': False, 'error': 'Vous avez déjà aimé ce document.', 'liked': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def archive_download(request, slug):
    """Télécharger et compter"""
    archive = get_object_or_404(Archive, slug=slug, is_published=True)
    archive.downloads_count += 1
    archive.save()
    
    return redirect(archive.file.url)

def president_list(request):
    """Liste de tous les présidents"""
    presidents = PastPresident.objects.all().order_by('-mandate_start')
    
    context = {
        'presidents': presidents,
    }
    return render(request, 'main/president_list.html', context)

def president_detail(request, president_id):
    """Détail d'un président spécifique"""
    president = get_object_or_404(PastPresident, id=president_id)
    
    context = {
        'president': president,
    }
    return render(request, 'main/president_detail.html', context)


# =============================================================================
# J.U.IN 2026 — VIEWS
# =============================================================================
from .models import JUINEdition, JUINCommission, JUINCommissionApplication, JUINActivity, JUINDonation
from .forms import JUINCommissionApplicationForm, JUINDonationForm


def juin_page(request):
    """Méga-page publique du J.U.IN 2026"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    
    commissions = []
    activities = []
    donations = []
    total_raised = 0
    stats = {}

    if edition:
        commissions = edition.commissions.all().prefetch_related(
            'applications'
        ).order_by('order')
        activities = edition.activities.all().order_by('date_activity')
        donations = edition.donations.filter(is_confirmed=True).order_by('-date_don')
        total_raised = sum(d.montant for d in donations)
        stats = {
            'total_applications': JUINCommissionApplication.objects.filter(
                commission__edition=edition
            ).count(),
            'approved_members': JUINCommissionApplication.objects.filter(
                commission__edition=edition, statut='approved'
            ).count(),
            'total_activities': activities.count(),
            'total_donors': donations.count(),
        }

    # Historical editions for timeline (static data from document)
    historical_editions = [
        {'num': '1ère', 'year': 2004, 'note': 'Édition inaugurale'},
        {'num': '4ème', 'year': 2007, 'budget': '8M', 'note': 'Édition marquante'},
        {'num': '5ème', 'year': 2008, 'budget': '26M', 'note': ''},
        {'num': '7ème', 'year': 2010, 'budget': '6M', 'note': 'Orange Cameroun partenaire'},
        {'num': '12ème', 'year': 2015, 'budget': '3M', 'note': 'KIRO\'O GAMES'},
        {'num': '16ème', 'year': 2019, 'budget': '4M', 'note': 'Orange, EU, Innovoft'},
        {'num': '17ème', 'year': 2022, 'budget': '-', 'note': 'Reprise post-COVID'},
        {'num': '18ème', 'year': 2023, 'budget': '4M', 'note': 'Togettech, Women Techmakers, FNE'},
        {'num': '19ème', 'year': 2024, 'budget': '10M+', 'note': 'Togettech, AmphiMil, CAYSTI, IAC'},
        {'num': '20ème', 'year': 2026, 'budget': '?', 'note': 'Édition actuelle'},
    ]

    # Dynamic data for partners
    institutions = []
    competitions = []
    if edition:
        institutions = edition.sponsors.filter(tier='institution', statut='approved').order_by('order')
        competitions = edition.competitions.all().order_by('name')

    context = {
        'edition': edition,
        'commissions': commissions, # Changed to show all as implied by user
        'activities': activities[:3],
        'institutions': institutions,
        'competitions': competitions,
        'total_raised': total_raised,
        'stats': stats,
        'historical_editions': historical_editions,
        'apply_form': JUINCommissionApplicationForm(edition=edition) if edition else None,
        'donate_form': JUINDonationForm(),
    }
    return render(request, 'main/juin.html', context)


def juin_commissions_list(request):
    """Page listant toutes les commissions du J.U.IN 2026"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    commissions = []
    if edition:
        commissions = edition.commissions.all().prefetch_related('applications').order_by('order')
    
    return render(request, 'main/juin_commissions.html', {
        'edition': edition,
        'commissions': commissions,
        'apply_form': JUINCommissionApplicationForm(edition=edition) if edition else None,
    })


def juin_apply_commission(request):
    """POST: soumettre une candidature à une commission"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    if not edition:
        messages.error(request, "Aucune édition active du J.U.IN pour le moment.")
        return redirect('juin')

    if not edition.applications_open:
        messages.error(request, "Les inscriptions aux commissions sont fermées pour cette édition.")
        return redirect('juin')

    if request.method == 'POST':
        form = JUINCommissionApplicationForm(request.POST, request.FILES, edition=edition)
        if form.is_valid():
            application = form.save(commit=False)
            application.save()

            # Send confirmation email to applicant
            try:
                from django.template.loader import render_to_string
                from django.core.mail import EmailMultiAlternatives
                from django.utils.html import strip_tags

                html = render_to_string('emails/juin_application_received.html', {
                    'nom_prenom': application.nom_prenom,
                    'commission_name': application.commission.name,
                    'commission_code': application.commission.code,
                    'etablissement': application.get_etablissement_display(),
                    'niveau': application.niveau,
                })
                email_msg = EmailMultiAlternatives(
                    subject=f'[J.U.IN 2026] Candidature reçue — {application.commission.code}',
                    body=strip_tags(html),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[application.email],
                )
                email_msg.attach_alternative(html, 'text/html')
                email_msg.send(fail_silently=True)

                # Notify admin
                admin_msg = EmailMultiAlternatives(
                    subject=f'[J.U.IN] Nouvelle candidature — {application.nom_prenom} → {application.commission.code}',
                    body=f"Candidat: {application.nom_prenom}\nEmail: {application.email}\nCommission: {application.commission.name}\nÉtablissement: {application.get_etablissement_display()}\nNiveau: {application.niveau}\n\nMotivation: {application.motivation}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.ASSOCIATION_EMAIL],
                )
                admin_msg.send(fail_silently=True)
            except Exception as e:
                print(f"[J.U.IN Apply] Email error: {e}")

            messages.success(request, "Votre candidature a été envoyée avec succès ! Vous recevrez un email de confirmation.")
            return redirect('juin_apply_success')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = JUINCommissionApplicationForm(edition=edition)

    # Re-render page with form errors
    commissions = edition.commissions.all().prefetch_related('applications').order_by('order')
    activities = edition.activities.all().order_by('date_activity')
    donations = edition.donations.filter(is_confirmed=True).order_by('-date_don')
    total_raised = sum(d.montant for d in donations)
    context = {
        'edition': edition,
        'commissions': commissions,
        'activities': activities,
        'donations': donations,
        'total_raised': total_raised,
        'apply_form': form,
        'donate_form': JUINDonationForm(),
        'scroll_to_form': True,
    }
    return render(request, 'main/juin.html', context)


def juin_apply_success(request):
    """Page de confirmation de candidature J.U.IN"""
    return render(request, 'main/juin_apply_success.html')


def juin_donate(request):
    """POST: soumettre un don et initier le paiement FreemoPay"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    if not edition or not edition.donations_open:
        messages.error(request, "Les dons ne sont pas disponibles pour le moment.")
        return redirect('juin')

    if request.method == 'POST':
        form = JUINDonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.edition = edition
            
            # Si paiement Mobile Money, on initie FreemoPay
            if donation.type_paiement in ('mtn', 'orange'):
                import uuid
                external_id = str(uuid.uuid4())
                donation.external_id = external_id
                donation.save()
                
                service = FreemopayService()
                res = service.initiate_payment(
                    amount=donation.montant,
                    phone_number=donation.telephone,
                    description=f"Don JUIN 2026 - {donation.nom_prenom}",
                    external_id=external_id
                )
                
                if res and res.get('success'):
                    donation.freemopay_reference = res.get('reference')
                    donation.payment_status = 'initiated'
                    donation.save()
                    
                    messages.success(request, f"Paiement initié ! {res.get('instructions')}")
                    return render(request, 'main/juin_payment_waiting.html', {
                        'donation': donation,
                        'instructions': res.get('instructions')
                    })
                elif res:
                    messages.error(request, f"Erreur FreemoPay: {res.get('error')}")
                else:
                    messages.error(request, "Erreur de connexion au service de paiement.")
                    donation.payment_status = 'failed'
                    donation.save()
                    return redirect('juin_donate')
            else:
                # Autres modes (espèces...) -> confirmation manuelle par admin
                donation.save()
                messages.success(request, "Merci pour votre promesse de don ! Nous vous contacterons pour finaliser.")
                return redirect('juin')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire de don.")
            return redirect('juin_donate')
    
    # GET: Render the dedicated donation page
    donations = edition.donations.filter(is_confirmed=True).order_by('-date_don') if edition else []
    total_raised = sum(d.montant for d in donations)
    
    return render(request, 'main/juin_donate.html', {
        'edition': edition,
        'donate_form': JUINDonationForm(),
        'donations': donations,
        'total_raised': total_raised,
    })


@csrf_exempt
def juin_payment_webhook(request):
    """Webhook pour recevoir les notifications de paiement FreemoPay"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reference = data.get('reference')
            status = data.get('status')
            external_id = data.get('externalId')
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[FREEMOPAY WEBHOOK] Ref: {reference}, Status: {status}, ExternalId: {external_id}")
            
            from .models import JUINDonation
            donation = JUINDonation.objects.filter(external_id=external_id).first()
            if donation:
                if status in ('SUCCESS', 'COMPLETED', 'PAID', 'SUCCESSFUL'):
                    donation.is_confirmed = True
                    donation.payment_status = 'completed'
                    donation.save()
                    logger.info(f"[FREEMOPAY WEBHOOK] Don confirmé pour {donation.nom_prenom}")
                elif status in ('FAILED', 'FAILURE', 'ERROR', 'EXPIRED'):
                    donation.payment_status = 'failed'
                    donation.save()
                elif status in ('CANCELLED', 'CANCELED'):
                    donation.payment_status = 'cancelled'
                    donation.save()
                    
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'method not allowed'}, status=405)


def juin_payment_status_check(request, external_id):
    """Vérifier le statut du paiement (AJAX polling)"""
    donation = get_object_or_404(JUINDonation, external_id=external_id)
    return JsonResponse({
        'status': donation.payment_status,
        'is_confirmed': donation.is_confirmed
    })


def juin_sponsor_request(request):
    """Formulaire de demande de partenariat"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = JUINSponsorRequestForm(request.POST, request.FILES)
        if form.is_valid():
            sponsor = form.save(commit=False)
            sponsor.edition = edition
            sponsor.save()
            
            # Notify admin
            try:
                from django.core.mail import EmailMessage
                EmailMessage(
                    subject=f'[J.U.IN] Nouvelle demande de sponsor: {sponsor.company_name}',
                    body=f"Entreprise: {sponsor.company_name}\nContact: {sponsor.contact_name}\nEmail: {sponsor.contact_email}\nNiveau: {sponsor.get_tier_display()}\n\nContribution: {sponsor.contribution}",
                    to=[settings.ASSOCIATION_EMAIL],
                ).send(fail_silently=True)
            except:
                pass
                
            messages.success(request, "Votre demande de partenariat a été envoyée avec succès ! Notre équipe vous contactera prochainement.")
            return redirect('juin')
    else:
        form = JUINSponsorRequestForm()
    
    return render(request, 'main/juin_become_partner.html', {'form': form, 'edition': edition})


def juin_sponsors_list(request):
    """Page publique des sponsors validés"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    from .models import JUINSponsor
    sponsors = JUINSponsor.objects.none()
    
    if edition:
        sponsors = edition.sponsors.filter(statut='approved').order_by('order', 'tier')
    
    # Grouper par tier
    tiers = {
        'gold': sponsors.filter(tier='gold'),
        'silver': sponsors.filter(tier='silver'),
        'bronze': sponsors.filter(tier='bronze'),
        'partner': sponsors.filter(tier='partner'),
        'institution': sponsors.filter(tier='institution'),
        'media': sponsors.filter(tier='media'),
    }
    
    return render(request, 'main/juin_sponsors.html', {
        'edition': edition,
        'tiers': tiers,
        'has_sponsors': sponsors.exists()
    })


def juin_activities_all(request):
    """Page d'agenda complet avec filtrage par type"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    activity_type = request.GET.get('type')
    activities = JUINActivity.objects.filter(edition=edition).order_by('date_activity') if edition else []
    
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
        
    context = {
        'edition': edition,
        'activities': activities,
        'current_type': activity_type,
        'types': JUINActivity.TYPE_CHOICES
    }
    return render(request, 'main/juin_activities.html', context)


def juin_competition_register(request, competition_slug):
    """Inscription d'une équipe à une compétition"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    competition = get_object_or_404(JUINCompetition, slug=competition_slug, edition=edition)
    
    if not competition.is_open:
        messages.warning(request, "Les inscriptions pour cette compétition sont fermées.")
        return redirect('juin')
        
    from .forms import JUINTeamRegistrationForm
    if request.method == 'POST':
        form = JUINTeamRegistrationForm(request.POST, request.FILES, competition=competition)
        if form.is_valid():
            team = form.save(commit=False)
            team.competition = competition
            team.save()
            messages.success(request, f"L'équipe {team.name} a été inscrite avec succès ! En attente de validation.")
            return redirect('juin')
    else:
        form = JUINTeamRegistrationForm(competition=competition)
        
    return render(request, 'main/juin_competition_register.html', {
        'form': form,
        'competition': competition,
        'edition': edition
    })


def juin_competitions_status(request):
    """Page affichant l'état des compétitions et les équipes engagées"""
    from django.db import models as db_models
    edition = JUINEdition.objects.filter(is_active=True).first()
    competitions = JUINCompetition.objects.filter(edition=edition).prefetch_related(
        db_models.Prefetch('teams', queryset=JUINTeam.objects.filter(statut='approved'))
    ) if edition else []
    
    context = {
        'edition': edition,
        'competitions': competitions,
    }
    return render(request, 'main/juin_competitions.html', context)


def juin_commission_detail(request, slug):
    """Page de détail d'une commission avec ses membres validés"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    commission = get_object_or_404(JUINCommission, slug=slug, edition=edition)
    
    # Membres validés groupés par rôle (Order: President, Vice-President, Rapporteur Adjoint, Rapporteur Principal, Membre)
    from django.db.models import Case, When, Value, IntegerField
    role_order = Case(
        When(commission_role='president', then=Value(1)),
        When(commission_role='vice_president', then=Value(2)),
        When(commission_role='rapporteur_adj', then=Value(3)),
        When(commission_role='rapporteur', then=Value(4)),
        When(commission_role='membre', then=Value(5)),
        default=Value(10),
        output_field=IntegerField(),
    )
    members = commission.applications.filter(statut='approved').order_by(role_order, 'nom_prenom')
    
    context = {
        'edition': edition,
        'commission': commission,
        'members': members,
    }
    return render(request, 'main/juin_commission_detail.html', context)


def juin_guide(request):
    """Page Guide & FAQ pour le J.U.IN 2026"""
    return render(request, 'main/juin_guide.html')



# =============================================================================
# NEW FEATURES: PROJECTS & COMMISSIONS
# =============================================================================
from .forms import ProjectSubmissionForm, ClubCommissionApplicationForm

def project_submit(request):
    """Soumission d'un projet par un visiteur"""
    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save()
            messages.success(request, "Votre projet a été soumis avec succès ! Nous vous contacterons bientôt.")
            return redirect('project_submit_success')
    else:
        form = ProjectSubmissionForm()
    
    return render(request, 'main/project_submit.html', {'form': form})

def project_submit_success(request):
    """Page de succès après soumission de projet"""
    return render(request, 'main/project_submit_success.html')

def club_commissions_list(request):
    """Liste des directions permanentes du Club"""
    commissions = ClubCommission.objects.all()
    return render(request, 'main/club_commissions_list.html', {'commissions': commissions})

def club_commission_detail(request, slug):
    """Détail d'une direction avec ses membres"""
    commission = get_object_or_404(ClubCommission, slug=slug)
    
    # Ordering members by role
    from django.db.models import Case, When, Value, IntegerField
    role_order = Case(
        When(role_applied='director', then=Value(1)),
        When(role_applied='deputy_director', then=Value(2)),
        When(role_applied='rapporteur', then=Value(3)),
        When(role_applied='deputy_rapporteur', then=Value(4)),
        When(role_applied='member', then=Value(5)),
        default=Value(10),
        output_field=IntegerField(),
    )
    members = commission.applications.filter(status='approved').order_by(role_order, 'nom_prenom')
    
    return render(request, 'main/club_commission_detail.html', {
        'commission': commission,
        'members': members
    })

def club_commission_apply(request):
    """Formulaire de candidature à une direction"""
    if request.method == 'POST':
        form = ClubCommissionApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre candidature a été envoyée avec succès !")
            return redirect('club_commission_apply_success')
    else:
        form = ClubCommissionApplicationForm()
        
    return render(request, 'main/club_commission_apply.html', {'form': form})

def club_commission_apply_success(request):
    """Page de succès après candidature"""
    return render(request, 'main/club_commission_apply_success.html')


def member_portfolio(request, slug):
    member = get_object_or_404(Member, portfolio_slug=slug, portfolio_enabled=True)
    
    member_projects = Project.objects.filter(title_fr__icontains=member.nom_prenom) | \
                      Project.objects.filter(description_fr__icontains=member.nom_prenom)

    from django.db.models import Q  # ← Import Q directement
    
    similar_members = Member.objects.filter(
        portfolio_enabled=True
    ).exclude(id=member.id).filter(
        Q(promotion=member.promotion) | Q(niveau=member.niveau)  # ← Q sans préfixe models.
    ).order_by('?')[:3]
    
    from .models import EventRegistration
    registrations = EventRegistration.objects.filter(email=member.email, is_confirmed=True).select_related('event')
    
    return render(request, 'main/member_portfolio.html', {
        'member': member,
        'member_projects': member_projects,
        'similar_members': similar_members,
        'registrations': registrations
    })

def delegate_detail(request, slug):
    """Page de détail d'un délégué"""
    delegate = get_object_or_404(Delegate, slug=slug)
    latest_news = BlogArticle.objects.filter(is_published=True).order_by('-published_at')[:3]
    return render(request, 'main/delegate_detail.html', {
        'delegate': delegate,
        'latest_news': latest_news
    })

# =============================================================================
# NEW MODULES: ACADEMIC RESOURCES & JOB BOARD
# =============================================================================

from .models import AcademicResource, JobOffer, NIVEAU_CHOICES, RESOURCE_TYPE_CHOICES, OFFER_TYPE_CHOICES
from .forms import AcademicResourceForm, JobOfferForm

def resources_list(request):
    """Page listant les ressources académiques"""
    resources = AcademicResource.objects.filter(is_approved=True).order_by('-created_at')
    
    # Filtres
    niveau = request.GET.get('niveau')
    resource_type = request.GET.get('type')
    
    if niveau:
        resources = resources.filter(niveau=niveau)
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
        
    return render(request, 'main/resources_list.html', {
        'resources': resources,
        'niveaux': NIVEAU_CHOICES,
        'types': RESOURCE_TYPE_CHOICES,
    })

def resource_upload(request):
    """Soumettre une ressource"""
    if request.method == 'POST':
        form = AcademicResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.is_approved = False  # Modération requise
            resource.save()
            messages.success(request, "Merci ! Votre ressource a été soumise et est en attente de modération.")
            return redirect('resources_list')
    else:
        form = AcademicResourceForm()
        
    return render(request, 'main/resource_upload.html', {'form': form})

def job_board(request):
    """Job Board Alumni"""
    offers = JobOffer.objects.filter(is_active=True, is_approved=True).order_by('-created_at')
    
    offer_type = request.GET.get('type')
    if offer_type:
        offers = offers.filter(offer_type=offer_type)
        
    return render(request, 'main/job_board.html', {
        'offers': offers,
        'types': OFFER_TYPE_CHOICES,
    })

def job_offer_create(request):
    """Publier une offre d'emploi ou de stage"""
    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.is_approved = False
            offer.save()
            messages.success(request, "Merci ! L'offre a été soumise avec succès.")
            return redirect('job_board')
    else:
        form = JobOfferForm()
        
    return render(request, 'main/job_offer_create.html', {'form': form})

def members_list(request):
    """Annuaire de tous les membres du COMSAS"""
    members = Member.objects.filter(is_active=True).order_by('nom_prenom')
    
    # Recherche
    q = request.GET.get('q', '')
    if q:
        members = members.filter(Q(nom_prenom__icontains=q) | Q(skills__icontains=q) | Q(technologies__icontains=q))
    
    paginator = Paginator(members, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'main/members_list.html', {
        'members': page_obj,
        'q': q
    })

def contest_candidate_register(request, contest_slug):
    """Inscription individuelle à un concours (Général)"""
    contest = get_object_or_404(Contest, slug=contest_slug, is_active=True)
    
    if not contest.allow_public_candidates:
        messages.error(request, "Les inscriptions publiques ne sont pas ouvertes pour ce concours.")
        if 'miss-mister' in contest.slug:
            return redirect('juin_miss_mister')
        return redirect('contest_detail', slug=contest.slug)

    if request.method == 'POST':
        from .forms import CandidateRegistrationForm
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.contest = contest
            candidate.status = 'pending'
            candidate.save()
            messages.success(request, "Votre candidature a été soumise avec succès ! Elle sera visible après validation par l'administration.")
            if 'miss-mister' in contest.slug:
                return redirect('juin_miss_mister')
            return redirect('contest_detail', slug=contest.slug)
    else:
        from .forms import CandidateRegistrationForm
        form = CandidateRegistrationForm()
        
    template_name = 'main/juin_contest/register.html' if 'miss-mister' in contest.slug else 'main/contests/candidate_register.html'
        
    return render(request, template_name, {'form': form, 'contest': contest})

def juin_miss_mister_register(request, contest_slug=None):
    """Vue dédiée à l'inscription Miss/Mister JUIN 2026"""
    if contest_slug:
        contest = get_object_or_404(Contest, slug=contest_slug)
    else:
        contest = Contest.objects.filter(slug__icontains='juin').filter(slug__icontains='miss-mister').first()
    if not contest:
        contest = Contest.objects.filter(slug='juin-miss-mister-2026').first()
    
    if not contest:
        messages.error(request, "Le concours Miss & Mister J.U.IN 2026 n'est pas encore configuré.")
        return redirect('juin')

    if not contest.is_active:
        messages.warning(request, "Les inscriptions pour ce concours ne sont pas encore ouvertes.")
        return redirect('juin_miss_mister')

    if request.method == 'POST':
        from .forms import CandidateRegistrationForm
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.contest = contest
            candidate.status = 'pending'
            candidate.save()
            messages.success(request, "Votre candidature a été soumise avec succès ! Elle sera visible après validation.")
            return redirect('juin_miss_mister')
    else:
        from .forms import CandidateRegistrationForm
        form = CandidateRegistrationForm()
        
    return render(request, 'main/juin_contest/register.html', {
        'form': form, 
        'contest': contest,
        'title': "Inscription Miss & Mister"
    })

def juin_candidates_status(request, contest_slug):
    """Affichage des candidats retenus pour un concours"""
    contest = get_object_or_404(Contest, slug=contest_slug)
    candidates = Candidate.objects.filter(contest=contest, status='approved').order_by('name')
    
    return render(request, 'main/juin_candidates.html', {
        'contest': contest,
        'candidates': candidates
    })

from .freemopay_service import FreemopayPaymentProcessor, FreemopayWebhookHandler

@csrf_exempt
def juin_freemopay_webhook(request):
    """Webhook pour recevoir les notifications de paiement Freemopay"""
    if request.method == 'POST':
        result = FreemopayWebhookHandler.handle_webhook(request.body)
        if result.get('success'):
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error', 'message': result.get('error')}, status=400)
    return HttpResponseForbidden()

def contest_vote_initiate(request):
    """Initier un vote payant (100 FCFA/voix)"""
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        vote_count = int(request.POST.get('vote_count', 1))
        phone = request.POST.get('phone')
        
        if not candidate_id or not phone or vote_count < 1:
            return JsonResponse({'success': False, 'error': 'Données invalides'}, status=400)
            
        candidate = get_object_or_404(Candidate, id=candidate_id)
        amount = vote_count * 100
        transaction_id = f"VOTE-{uuid.uuid4().hex[:8].upper()}"
        
        voter_name = request.POST.get('voter_name')
        voter_school = request.POST.get('voter_school')
        operator = request.POST.get('operator')
        is_anonymous = request.POST.get('is_anonymous') == 'true'
        
        vote = Vote.objects.create(
            contest=candidate.contest,
            candidate=candidate,
            voter_phone=phone,
            operator=operator,
            voter_name=voter_name,
            voter_school=voter_school,
            is_anonymous=is_anonymous,
            vote_count=vote_count,
            amount=amount,
            transaction_id=transaction_id,
            status='pending',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        from .freemopay_service import FreemopayPaymentProcessor
        processor = FreemopayPaymentProcessor()
        result = processor.process_vote_payment(vote)
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'transaction_id': transaction_id,
                'amount': amount,
                'message': result.get('message')
            })
        else:
            vote.status = 'failed'
            vote.save()
            return JsonResponse({'success': False, 'error': result.get('error')})
            
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

def vote_status_check(request, transaction_id):
    """Vérifier le statut d'un vote (polling)"""
    vote = get_object_or_404(Vote, transaction_id=transaction_id)
    
    # Si toujours en cours, on peut tenter une vérification active si besoin
    if vote.status == 'processing':
        processor = FreemopayPaymentProcessor()
        check = processor.verify_payment_status(vote)
        if check.get('success') and check.get('status') == 'completed':
            processor.confirm_payment(vote)
            
    return JsonResponse({
        'status': vote.status,
        'is_confirmed': vote.status == 'completed',
        'candidate_name': vote.candidate.name,
        'vote_count': vote.vote_count
    })

def vote_complete(request, transaction_id):
    """Page de confirmation finale du vote (Succès ou Échec)"""
    vote = get_object_or_404(Vote, transaction_id=transaction_id)
    return render(request, 'main/contests/vote_complete.html', {'vote': vote})


# ============= MISS & MISTER J.U.IN 2026 =============

def juin_miss_mister_contest(request):
    """Page principale du concours Miss & Mister J.U.IN 2026"""
    # Recherche spécifique par slug exact pour J.U.IN 2026
    contest = Contest.objects.filter(slug='juin-miss-mister-2026').first()
    if not contest:
        # Fallback sur une recherche plus large si le slug a été modifié
        contest = Contest.objects.filter(slug__icontains='juin').filter(slug__icontains='miss-mister').first()
    
    # Si toujours pas trouvé, on ne prend rien plutôt que de prendre le mauvais
    if not contest:
        candidates = []
        misses = []
        misters = []
    else:
        candidates = Candidate.objects.filter(contest=contest, status='approved').order_by('candidate_type', 'name')
        # Séparer Miss et Mister
        misses = [c for c in candidates if c.candidate_type == 'miss']
        misters = [c for c in candidates if c.candidate_type == 'mister']
    
    context = {
        'contest': contest,
        'misses': misses,
        'misters': misters,
        'candidates': candidates,
    }
    return render(request, 'main/juin_contest/list.html', context)

def juin_candidate_detail(request, pk):
    """Page de détail d'un candidat Miss/Mister"""
    candidate = get_object_or_404(Candidate, pk=pk)
    contest = candidate.contest
    
    # Stats simples
    total_votes_contest = sum(c.votes_count for c in contest.candidates.all())
    rank = Candidate.objects.filter(contest=contest, votes_count__gt=candidate.votes_count).count() + 1
    
    context = {
        'candidate': candidate,
        'contest': contest,
        'rank': rank,
        'total_votes_contest': total_votes_contest,
        'percentage': round((candidate.votes_count / total_votes_contest * 100), 1) if total_votes_contest > 0 else 0
    }
    return render(request, 'main/juin_contest/detail.html', context)

def juin_contest_results(request):
    """Page des résultats en temps réel avec graphiques"""
    contest = Contest.objects.filter(slug__icontains='miss-mister', is_active=True).first()
    if not contest:
        contest = Contest.objects.first()
        
    candidates = Candidate.objects.filter(contest=contest, status='approved').order_by('-votes_count')
    
    # Data for charts
    labels = [c.name for c in candidates]
    votes_data = [c.votes_count for c in candidates]
    
    # Results per school
    school_results = {}
    for c in candidates:
        school = c.school or "Autre"
        school_results[school] = school_results.get(school, 0) + c.votes_count
    
    school_labels = list(school_results.keys())
    school_data = list(school_results.values())
    
    context = {
        'contest': contest,
        'candidates': candidates,
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(votes_data),
        'school_labels': json.dumps(school_labels),
        'school_data': json.dumps(school_data),
    }
    return render(request, 'main/juin_contest/results.html', context)

