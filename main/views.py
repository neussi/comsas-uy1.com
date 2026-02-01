from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Member, Project, Event, EventRegistration, 
    News, Gallery, Contact, SiteSettings,
    SponsorshipSession, Mentor, Mentee, Match,
    Contest, Candidate, Vote,
)
from .forms import (
    MemberRegistrationForm, EventRegistrationForm, 
    ContactForm
)

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
    
    context = {
        'site_settings': site_settings,
        'featured_events': featured_events,
        'featured_projects': featured_projects,
        'recent_news': recent_news,
        'featured_gallery': featured_gallery,
        'bureau_members': bureau_members,
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
    bureau_members = Member.objects.filter(
        member_type='bureau',
        is_active=True
    ).order_by('poste_bureau')
    
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
                admin_message = f"""
                Nouvelle demande d'adhésion reçue:
                
                Nom et Prénom: {member.nom_prenom}
                Matricule: {member.matricule}
                Email: {member.email}
                Téléphone: {member.telephone}
                Lieu de naissance: {member.lieu_naissance}
                Date de naissance: {member.date_naissance}
                Photo: {'Oui' if member.photo else 'Non'}
                
                Veuillez vous connecter à l'administration pour valider ou rejeter cette demande.
                """
                
                send_mail(
                    admin_subject,
                    admin_message,
                    settings.EMAIL_HOST_USER,
                    [settings.ASSOCIATION_EMAIL],
                    fail_silently=True,
                )
                
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
        form = EventRegistrationForm(request.POST)
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
                registration.save()
                messages.success(request, _('Votre inscription a été enregistrée avec succès!'))
                
                # Envoyer notification
                try:
                    send_mail(
                        f'Nouvelle inscription - {event.title_fr}',
                        f'Participant: {registration.nom_prenom}\nEmail: {registration.email}',
                        settings.EMAIL_HOST_USER,
                        [settings.ASSOCIATION_EMAIL],
                        fail_silently=True,
                    )
                except:
                    pass
                
                return redirect('event_registration_success', pk=event.pk)
    else:
        form = EventRegistrationForm()
    
    context = {
        'event': event,
        'form': form,
        'can_register': can_register,
    }
    
    return render(request, 'main/event_detail.html', context)

def event_registration_success(request, pk):
    """Page de confirmation d'inscription à un événement"""
    event = get_object_or_404(Event, pk=pk)
    context = {'event': event}
    return render(request, 'main/event_registration_success.html', context)

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

def gallery(request):
    """Page de la galerie"""
    # Images
    images = Gallery.objects.filter(media_type='image').order_by('-created_at')
    
    # Vidéos
    videos = Gallery.objects.filter(media_type='video').order_by('-created_at')
    
    context = {
        'images': images,
        'videos': videos,
    }
    
    return render(request, 'main/gallery.html', context)

def donations(request):
    """Page des dons et cotisations"""
    # Projets nécessitant des fonds
    funded_projects = Project.objects.filter(
        status__in=['planning', 'ongoing']
    ).order_by('-is_featured', '-created_at')
    
    context = {
        'funded_projects': funded_projects,
        'whatsapp_president': settings.WHATSAPP_PRESIDENT,
        'whatsapp_treasurer_mtn': settings.WHATSAPP_TREASURER_MTN,
        'whatsapp_treasurer_orange': settings.WHATSAPP_TREASURER_ORANGE,
    }
    
    return render(request, 'main/donations.html', context)

def contact(request):
    """Page de contact"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            messages.success(request, _('Votre message a été envoyé avec succès! Nous vous répondrons bientôt.'))
            
            # Envoyer notification par email
            try:
                send_mail(
                    f'Nouveau message de contact - {contact_message.sujet}',
                    f'De: {contact_message.nom_prenom} ({contact_message.email})\n\nMessage:\n{contact_message.message}',
                    settings.EMAIL_HOST_USER,
                    [settings.ASSOCIATION_EMAIL],
                    fail_silently=True,
                )
            except:
                pass
            
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
    context = {
        'error_code': '404',
        'error_title': 'Page non trouvée',
        'error_message': 'Désolé, la page que vous recherchez n\'existe pas ou a été déplacée.',
    }
    return render(request, 'errors/404.html', context, status=404)


def handler500(request):
    """Page d'erreur 500 personnalisée"""
    context = {
        'error_code': '500',
        'error_title': 'Erreur serveur',
        'error_message': 'Une erreur interne s\'est produite. Notre équipe technique a été notifiée et travaille à résoudre le problème.',
    }
    return render(request, 'errors/500.html', context, status=500)


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
