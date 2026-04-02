from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.db import models
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
import csv


# Custom custom_staff_member_required to avoid 'admin' namespace error
def custom_staff_member_required(view_func):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='admin_login' # This should match your custom login name
    )
    return actual_decorator(view_func)

from main.models import (
    Member, Project, Event, EventRegistration, 
    News, Gallery, Contact, SiteSettings,
    SponsorshipSession, Mentor, Mentee, Match,
    Contest, Candidate, Vote,
    RequestDocument, Professor, Classroom, Delegate, BlogArticle,
    ProjectSubmission, ClubCommission, ClubCommissionApplication,
    JUINEdition, JUINCommission, JUINCommissionApplication, JUINCompetition,
    JUINActivity, JUINDonation, JUINSponsor, JUINTeam,
    AcademicResource, JobOffer
)
from .forms import (
    ProjectForm, EventForm, NewsForm, GalleryForm, SiteSettingsForm, MemberForm,
    SponsorshipSessionForm, ContestForm, CandidateForm,
    RequestDocumentForm, ProfessorForm, ClassroomForm, DelegateForm, BlogArticleForm
)
from main.utils import send_member_card_email

@custom_staff_member_required
def dashboard_home(request):
    """Page d'accueil du dashboard"""
    # Statistiques générales
    stats = {
        'total_members': Member.objects.filter(is_active=True).count(),
        'pending_members': Member.objects.filter(is_active=False).count(),
        'total_projects': Project.objects.count(),
        'ongoing_projects': Project.objects.filter(status='ongoing').count(),
        'total_events': Event.objects.count(),
        'upcoming_events': Event.objects.filter(is_active=True).count(),
        'unread_messages': Contact.objects.filter(is_read=False).count(),
        'total_gallery_items': Gallery.objects.count(),
    }
    
    # --- GRAPHIQUES ---

    # 1. Croissance des membres (12 derniers mois)
    one_year_ago = timezone.now() - timezone.timedelta(days=365)
    member_growth_data = Member.objects.filter(date_adhesion__gte=one_year_ago) \
        .annotate(month=TruncMonth('date_adhesion')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')
    
    growth_labels = [item['month'].strftime('%b %Y') for item in member_growth_data]
    growth_values = [item['count'] for item in member_growth_data]

    # 2. Budget Projets (Requis vs Collecté)
    projects_financials = Project.objects.aggregate(
        total_required=Sum('budget_required'),
        total_collected=Sum('budget_collected')
    )
    
    # 3. Top Événements (par inscriptions)
    top_events = Event.objects.annotate(num_registrations=Count('eventregistration')) \
        .order_by('-num_registrations')[:5]
    
    event_labels = [event.title_fr[:20] + '...' for event in top_events]
    event_values = [event.num_registrations for event in top_events]

    # Messages récents non lus
    recent_messages = Contact.objects.filter(is_read=False).order_by('-created_at')[:5]
    
    # Événements à venir
    upcoming_events = Event.objects.filter(is_active=True).order_by('date_event')[:5]
    
    # Projets en cours
    ongoing_projects = Project.objects.filter(status='ongoing')[:5]
    
    # Inscriptions récentes aux événements
    recent_registrations = EventRegistration.objects.order_by('-registration_date')[:10]
    
    # Calculs pour l'affichage en millions
    fn_required = projects_financials['total_required'] or 0
    fn_collected = projects_financials['total_collected'] or 0
    
    context = {
        'stats': stats,
        'recent_messages': recent_messages,
        'upcoming_events': upcoming_events,
        'ongoing_projects': ongoing_projects,
        'recent_registrations': recent_registrations,
        # Chart Data
        'growth_labels': growth_labels,
        'growth_values': growth_values,
        'financial_required': fn_required,
        'financial_collected': fn_collected,
        'financial_required_millions': fn_required / 1000000,
        'financial_collected_millions': fn_collected / 1000000,
        'event_labels': event_labels,
        'event_values': event_values,
    }
    
    return render(request, 'admin_dashboard/home.html', context)



# ============= GESTION DES MEMBRES =============

@custom_staff_member_required
def members_list(request):
    """Liste des membres"""
    members = Member.objects.all().order_by('-date_adhesion')
    
    # Filtrage
    member_type = request.GET.get('type')
    search = request.GET.get('search')
    
    if member_type:
        members = members.filter(member_type=member_type)
    
    if search:
        members = members.filter(
            Q(nom_prenom__icontains=search) | 
            Q(email__icontains=search) |
            Q(promotion__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(members, 20)
    page_number = request.GET.get('page')
    members_page = paginator.get_page(page_number)
    
    context = {
        'members_page': members_page,
        'member_types': Member.MEMBER_TYPES,
        'current_type': member_type,
        'search_query': search,
    }
    
    return render(request, 'admin_dashboard/members/list.html', context)

@custom_staff_member_required
def member_detail(request, pk):
    """Détail d'un membre"""
    member = get_object_or_404(Member, pk=pk)
    context = {'member': member}
    return render(request, 'admin_dashboard/members/detail.html', context)

@custom_staff_member_required
def member_approve(request, pk):
    """Approuver un membre"""
    member = get_object_or_404(Member, pk=pk)
    member.is_active = True
    member.save()
    
    # Envoyer la carte de membre par email
    from main.utils import generate_member_card
    pdf_buffer = generate_member_card(member)
    
    if send_member_card_email(member, pdf_buffer):
        messages.success(request, f'Le membre {member.nom_prenom} a été approuvé et sa carte envoyée.')
    else:
        messages.warning(request, f'Le membre {member.nom_prenom} a été approuvé, mais erreur d\'envoi de la carte.')
        
    return redirect('admin_members_list')

@custom_staff_member_required
def member_reject(request, pk):
    """Rejeter un membre"""
    member = get_object_or_404(Member, pk=pk)
    member.delete()
    messages.success(request, 'La demande d\'adhésion a été rejetée.')
    return redirect('admin_members_list')

@custom_staff_member_required
def member_download_card(request, pk):
    """Télécharger la carte de membre PDF"""
    from django.http import FileResponse
    from main.utils import generate_member_card
    
    member = get_object_or_404(Member, pk=pk)
    
    try:
        buffer = generate_member_card(member)
        buffer.seek(0)
        filename = f"Carte_Membre_{member.matricule or member.pk}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération de la carte : {e}")
        return redirect('admin_member_detail', pk=pk)

# NOUVELLES VUES POUR MEMBRES
@method_decorator(custom_staff_member_required, name='dispatch')
class MemberCreateView(CreateView):
    model = Member
    form_class = MemberForm
    template_name = 'admin_dashboard/members/form.html'
    success_url = reverse_lazy('admin_members_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le membre a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class MemberUpdateView(UpdateView):
    model = Member
    form_class = MemberForm
    template_name = 'admin_dashboard/members/form.html'
    success_url = reverse_lazy('admin_members_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le membre a été modifié avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class MemberDeleteView(DeleteView):
    model = Member
    template_name = 'admin_dashboard/members/confirm_delete.html'
    success_url = reverse_lazy('admin_members_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le membre a été supprimé avec succès.')
        return super().form_valid(form)

# ============= GESTION DES PROJETS =============

@custom_staff_member_required
def projects_list(request):
    """Liste des projets"""
    projects = Project.objects.all().order_by('-created_at')
    
    # Filtrage par statut
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)
    
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    projects_page = paginator.get_page(page_number)
    
    context = {
        'projects_page': projects_page,
        'status_choices': Project.STATUS_CHOICES,
        'current_status': status,
    }
    
    return render(request, 'admin_dashboard/projects/list.html', context)

@custom_staff_member_required
def project_detail(request, pk):
    """Détail d'un projet"""
    project = get_object_or_404(Project, pk=pk)
    context = {'project': project}
    return render(request, 'admin_dashboard/projects/detail.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'admin_dashboard/projects/form.html'
    success_url = reverse_lazy('admin_projects_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le projet a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'admin_dashboard/projects/form.html'
    success_url = reverse_lazy('admin_projects_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le projet a été modifié avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'admin_dashboard/projects/confirm_delete.html'
    success_url = reverse_lazy('admin_projects_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le projet a été supprimé avec succès.')
        return super().form_valid(form)

# ============= GESTION DES ÉVÉNEMENTS =============

@custom_staff_member_required
def events_list(request):
    """Liste des événements"""
    events = Event.objects.all().order_by('-date_event')
    
    # Ajouter le nombre d'inscriptions pour chaque événement
    events = events.annotate(registration_count=Count('eventregistration'))
    
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)
    
    context = {'events_page': events_page}
    return render(request, 'admin_dashboard/events/list.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'admin_dashboard/events/form.html'
    success_url = reverse_lazy('admin_events_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'événement a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'admin_dashboard/events/form.html'
    success_url = reverse_lazy('admin_events_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'événement a été modifié avec succès.')
        return super().form_valid(form)

# NOUVELLE VUE POUR SUPPRIMER ÉVÉNEMENT
@method_decorator(custom_staff_member_required, name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    template_name = 'admin_dashboard/events/confirm_delete.html'
    success_url = reverse_lazy('admin_events_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'événement a été supprimé avec succès.')
        return super().form_valid(form)

@custom_staff_member_required
def event_registrations(request, pk):
    """Liste des inscriptions pour un événement"""
    event = get_object_or_404(Event, pk=pk)
    registrations = event.eventregistration_set.all().order_by('-registration_date')
    
    paginator = Paginator(registrations, 20)
    page_number = request.GET.get('page')
    registrations_page = paginator.get_page(page_number)
    
    context = {
        'event': event,
        'registrations_page': registrations_page,
        'registrations': registrations,
        'confirmed_count': registrations.filter(is_confirmed=True).count(),
        'pending_count': registrations.filter(is_confirmed=False).count(),
    }
    
    return render(request, 'admin_dashboard/events/registrations.html', context)

@custom_staff_member_required
def delete_registration(request, pk):
    """Supprimer une inscription"""
    registration = get_object_or_404(EventRegistration, pk=pk)
    event_pk = registration.event.pk
    registration.delete()
    messages.success(request, "Inscription supprimée avec succès.")
    return redirect('admin_event_registrations', pk=event_pk)

@custom_staff_member_required
def confirm_registration(request, pk):
    """Confirmer une inscription"""
    registration = get_object_or_404(EventRegistration, pk=pk)
    registration.is_confirmed = True
    registration.save()
    
    messages.success(request, f'Inscription de {registration.nom_prenom} confirmée.')
    return redirect('admin_event_registrations', pk=registration.event.pk)

@custom_staff_member_required
def event_registrations_export_excel(request, pk):
    """Exporter les inscriptions à un événement en CSV"""
    event = get_object_or_404(Event, pk=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="inscriptions_{event.title_fr}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nom Prénom', 'Email', 'Téléphone', 'Date Inscription', 'Statut'])
    
    registrations = event.eventregistration_set.all().order_by('nom_prenom')
    for reg in registrations:
        writer.writerow([
            reg.nom_prenom,
            reg.email,
            reg.telephone,
            reg.registration_date.strftime("%d/%m/%Y %H:%M"),
            "Confirmé" if reg.is_confirmed else "En attente"
        ])
    return response

# ============= GESTION DES ACTUALITÉS =============

@custom_staff_member_required
def news_list(request):
    """Liste des actualités"""
    news = News.objects.all().order_by('-created_at')
    
    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    news_page = paginator.get_page(page_number)
    
    context = {'news_page': news_page}
    return render(request, 'admin_dashboard/news/list.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class NewsCreateView(CreateView):
    model = News
    form_class = NewsForm
    template_name = 'admin_dashboard/news/form.html'
    success_url = reverse_lazy('admin_news_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'actualité a été créée avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class NewsUpdateView(UpdateView):
    model = News
    form_class = NewsForm
    template_name = 'admin_dashboard/news/form.html'
    success_url = reverse_lazy('admin_news_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'actualité a été modifiée avec succès.')
        return super().form_valid(form)

# NOUVELLE VUE POUR SUPPRIMER ACTUALITÉ
@method_decorator(custom_staff_member_required, name='dispatch')
class NewsDeleteView(DeleteView):
    model = News
    template_name = 'admin_dashboard/news/confirm_delete.html'
    success_url = reverse_lazy('admin_news_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'actualité a été supprimée avec succès.')
        return super().form_valid(form)

# ============= GESTION DE LA GALERIE =============

@custom_staff_member_required
def gallery_list(request):
    """Liste des éléments de galerie"""
    gallery_items = Gallery.objects.all().order_by('-created_at')
    
    # Filtrage par type
    media_type = request.GET.get('type')
    if media_type:
        gallery_items = gallery_items.filter(media_type=media_type)
    
    paginator = Paginator(gallery_items, 12)
    page_number = request.GET.get('page')
    gallery_page = paginator.get_page(page_number)
    
    context = {
        'gallery_page': gallery_page,
        'media_types': Gallery.MEDIA_TYPES,
        'current_type': media_type,
    }
    
    return render(request, 'admin_dashboard/gallery/list.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class GalleryCreateView(CreateView):
    model = Gallery
    form_class = GalleryForm
    template_name = 'admin_dashboard/gallery/form.html'
    success_url = reverse_lazy('admin_gallery_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'élément a été ajouté à la galerie avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class GalleryUpdateView(UpdateView):
    model = Gallery
    form_class = GalleryForm
    template_name = 'admin_dashboard/gallery/form.html'
    success_url = reverse_lazy('admin_gallery_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'élément de la galerie a été modifié avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class GalleryDeleteView(DeleteView):
    model = Gallery
    template_name = 'admin_dashboard/gallery/confirm_delete.html'
    success_url = reverse_lazy('admin_gallery_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'élément a été supprimé de la galerie avec succès.')
        return super().form_valid(form)

# ============= GESTION DES MESSAGES =============

@custom_staff_member_required
def messages_list(request):
    """Liste des messages de contact"""
    messages_list = Contact.objects.all().order_by('-created_at')
    
    # Filtrage
    status = request.GET.get('status')
    if status == 'unread':
        messages_list = messages_list.filter(is_read=False)
    elif status == 'read':
        messages_list = messages_list.filter(is_read=True)
    
    paginator = Paginator(messages_list, 15)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'messages_page': messages_page,
        'current_status': status,
    }
    
    return render(request, 'admin_dashboard/messages/list.html', context)

@custom_staff_member_required
def message_detail(request, pk):
    """Détail d'un message"""
    message = get_object_or_404(Contact, pk=pk)
    
    # Marquer comme lu
    if not message.is_read:
        message.is_read = True
        message.save()
    
    context = {'message': message}
    return render(request, 'admin_dashboard/messages/detail.html', context)

@custom_staff_member_required
def mark_message_replied(request, pk):
    """Marquer un message comme répondu"""
    message = get_object_or_404(Contact, pk=pk)
    message.is_replied = True
    message.save()
    
    messages.success(request, 'Message marqué comme répondu.')
    return redirect('admin_message_detail', pk=pk)

# NOUVELLE VUE POUR SUPPRIMER MESSAGE
@custom_staff_member_required
def message_delete(request, pk):
    """Supprimer un message"""
    message = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message supprimé avec succès.')
        return redirect('admin_messages_list')
    
    context = {'message': message}
    return render(request, 'admin_dashboard/messages/confirm_delete.html', context)

# ============= PARAMÈTRES DU SITE =============

@custom_staff_member_required
def site_settings(request):
    """Paramètres du site"""
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paramètres du site mis à jour avec succès.')
            return redirect('admin_site_settings')
    else:
        form = SiteSettingsForm(instance=settings_obj)
    
    context = {'form': form}
    return render(request, 'admin_dashboard/settings/form.html', context)

# ============= GESTION DU PARRAINAGE =============

@custom_staff_member_required
def sponsorship_home(request):
    """Page d'accueil de la gestion du parrainage"""
    current_session = SponsorshipSession.objects.filter(is_active=True).first()
    sessions = SponsorshipSession.objects.all().order_by('-start_date')
    
    # Statistiques
    stats = {
        'total_mentors': Mentor.objects.count(),
        'total_mentees': Mentee.objects.count(),
        'active_matches': Match.objects.filter(is_active=True).count(),
        'pending_mentees': Mentee.objects.filter(match__isnull=True).count(),
    }
    
    context = {
        'current_session': current_session,
        'sessions': sessions,
        'stats': stats,
    }
    return render(request, 'admin_dashboard/sponsorship/home.html', context)

@custom_staff_member_required
def sponsorship_mentors(request):
    """Liste des parrains"""
    mentors = Mentor.objects.all().order_by('last_name')
    
    # Filtrage
    specialty = request.GET.get('specialty')
    if specialty:
        mentors = mentors.filter(specialty=specialty)
        
    paginator = Paginator(mentors, 20)
    page_number = request.GET.get('page')
    mentors_page = paginator.get_page(page_number)
    
    context = {
        'mentors_page': mentors_page,
        'specialties': Mentor.SPECIALTY_CHOICES,
        'current_specialty': specialty,
    }
    return render(request, 'admin_dashboard/sponsorship/mentors.html', context)

@custom_staff_member_required
def sponsorship_mentees(request):
    """Liste des filleuls"""
    mentees = Mentee.objects.all().order_by('last_name')
    
    # Filtrage
    specialty = request.GET.get('specialty')
    unmatched = request.GET.get('unmatched')
    
    if specialty:
        mentees = mentees.filter(desired_specialty=specialty)
        
    if unmatched:
        mentees = mentees.filter(match__isnull=True)
        
    paginator = Paginator(mentees, 20)
    page_number = request.GET.get('page')
    mentees_page = paginator.get_page(page_number)
    
    context = {
        'mentees_page': mentees_page,
        'specialties': Mentee.SPECIALTY_CHOICES,
        'current_specialty': specialty,
        'unmatched_only': unmatched,
    }
    return render(request, 'admin_dashboard/sponsorship/mentees.html', context)

@custom_staff_member_required
def sponsorship_matches(request):
    """Liste des paires (Matches)"""
    matches = Match.objects.all().order_by('-created_at')
    
    paginator = Paginator(matches, 20)
    page_number = request.GET.get('page')
    matches_page = paginator.get_page(page_number)
    
    context = {'matches_page': matches_page}
    context = {'matches_page': matches_page}
    return render(request, 'admin_dashboard/sponsorship/matches.html', context)

@custom_staff_member_required
def sponsorship_matches_export_csv(request):
    """Exporter les binômes en CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sponsorship_matches_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Session', 'Mentor', 'Mentor Email', 'Mentor Phone', 'Filleul', 'Filleul Email', 'Filleul Phone', 'Statut'])
    
    matches = Match.objects.all().select_related('mentor', 'mentee', 'session')
    for match in matches:
        writer.writerow([
            match.session.name,
            f"{match.mentor.first_name} {match.mentor.last_name}",
            match.mentor.email,
            match.mentor.phone,
            f"{match.mentee.first_name} {match.mentee.last_name}",
            match.mentee.email,
            match.mentee.phone,
            "Actif" if match.is_active else "Inactif"
        ])
    return response

@custom_staff_member_required
def sponsorship_matches_export_excel(request):
    """Exporter les binômes en Excel (Compatible via CSV pour simplicité)"""
    # Pour l'instant on utilise CSV mais avec un header Excel pour simplifier sans dépendance openpyxl
    return sponsorship_matches_export_csv(request)

@custom_staff_member_required
def sponsorship_auto_match(request):
    """Lancer le matching automatique"""
    if request.method == 'POST':
        # Logique de matching simple (à adapter selon les besoins complexes)
        # On récupère les filleuls sans parrain de la session active
        active_session = SponsorshipSession.objects.filter(is_active=True).first()
        if not active_session:
             messages.error(request, "Aucune session de parrainage active.")
             return redirect('admin_sponsorship_home')
             
        mentees = Mentee.objects.filter(session=active_session, match__isnull=True)
        count = 0
        
        for mentee in mentees:
            # NEW MATCHING ALGORITHM
            # 1. Get all eligible mentors (active session, not full)
            candidates = Mentor.objects.annotate(num_mentees=Count('match')).filter(
                session=active_session,
            ).filter(num_mentees__lt=models.F('max_mentees'))
            
            best_mentor = None
            best_score = -1
            
            # Parse Mentee Domains
            mentee_domains = set(d.strip() for d in mentee.professional_domains.split(',') if d.strip())
            
            for mentor in candidates:
                score = 0
                
                # Criteria 1: Specialty Match (+10)
                if mentor.specialty == mentee.desired_specialty:
                    score += 10
                
                # Criteria 2: Expertise Intersection (+5 per match)
                mentor_domains = set(d.strip() for d in mentor.expertise_domains.split(',') if d.strip())
                common = mentee_domains.intersection(mentor_domains)
                score += len(common) * 5
                
                # Criteria 3: Load Balancing (Prefer less loaded mentors)
                # Small penalty for existing mentees (-0.5)
                score -= mentor.num_mentees * 0.5
                
                if score > best_score:
                    best_score = score
                    best_mentor = mentor
            
            if best_mentor and best_score > 0:
                # Create Match
                Match.objects.get_or_create(
                    session=active_session,
                    mentor=best_mentor,
                    mentee=mentee
                )
                count += 1
                
                # Update local count to affect next iteration (Greedy approach)
                # Since 'candidates' is a QuerySet, modifying 'best_mentor' object won't affect next query 
                # unless we re-query or manually track.
                # For simplicity in this loop, we just proceed. Ideally we'd decrement capacity.
                best_mentor.num_mentees += 1 # Hack for sorting if we were keeping list in memory
                
        messages.success(request, f"{count} matching(s) effectué(s) automatiquement via Scoring.")
        return redirect('admin_sponsorship_home')
    
    
    return redirect('admin_sponsorship_home')

@method_decorator(custom_staff_member_required, name='dispatch')
class SponsorshipSessionCreateView(CreateView):
    model = SponsorshipSession
    form_class = SponsorshipSessionForm
    template_name = 'admin_dashboard/sponsorship/session_form.html'
    success_url = reverse_lazy('admin_sponsorship_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'La session de parrainage a été créée avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class SponsorshipSessionUpdateView(UpdateView):
    model = SponsorshipSession
    form_class = SponsorshipSessionForm
    template_name = 'admin_dashboard/sponsorship/session_form.html'
    success_url = reverse_lazy('admin_sponsorship_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'La session de parrainage a été mise à jour avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class SponsorshipSessionDeleteView(DeleteView):
    model = SponsorshipSession
    template_name = 'admin_dashboard/sponsorship/session_confirm_delete.html'
    success_url = reverse_lazy('admin_sponsorship_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'La session de parrainage a été supprimée.')
        try:
             return super().form_valid(form)
        except Exception as e:
             messages.error(self.request, f"Erreur lors de la suppression : {e}")
             return redirect('admin_sponsorship_home')

# ============= GESTION DES CONCOURS =============

@custom_staff_member_required
def contests_home(request):
    """Page d'accueil de la gestion des concours"""
    contests = Contest.objects.all().order_by('-start_date')
    active_contests = Contest.objects.filter(is_active=True).count()
    
    context = {
        'contests': contests,
        'active_contests_count': active_contests,
    }
    return render(request, 'admin_dashboard/contests/home.html', context)

@custom_staff_member_required
def contest_detail(request, pk):
    """Détail d'un concours et ses candidats"""
    contest = get_object_or_404(Contest, pk=pk)
    candidates = contest.candidates.all()
    
    context = {
        'contest': contest,
        'candidates': candidates,
    }
    return render(request, 'admin_dashboard/contests/detail.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class ContestCreateView(CreateView):
    model = Contest
    form_class = ContestForm
    template_name = 'admin_dashboard/contests/form.html'
    success_url = reverse_lazy('admin_contests_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le concours a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class ContestUpdateView(UpdateView):
    model = Contest
    form_class = ContestForm
    template_name = 'admin_dashboard/contests/form.html'
    success_url = reverse_lazy('admin_contests_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le concours a été mis à jour avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class ContestDeleteView(DeleteView):
    model = Contest
    template_name = 'admin_dashboard/contests/confirm_delete.html'
    success_url = reverse_lazy('admin_contests_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le concours a été supprimé.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class CandidateCreateView(CreateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'admin_dashboard/contests/candidate_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        contest_pk = self.kwargs.get('contest_pk')
        if contest_pk:
            initial['contest'] = get_object_or_404(Contest, pk=contest_pk)
        return initial
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'contest_pk' in self.kwargs:
            context['contest'] = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('admin_contest_detail', kwargs={'pk': self.object.contest.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Le candidat a été ajouté avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class CandidateUpdateView(UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'admin_dashboard/contests/candidate_form.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_contest_detail', kwargs={'pk': self.object.contest.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Le candidat a été mis à jour avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class CandidateDeleteView(DeleteView):
    model = Candidate
    template_name = 'admin_dashboard/contests/candidate_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_contest_detail', kwargs={'pk': self.object.contest.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Le candidat a été supprimé.')
        return super().form_valid(form)
# ============= GESTION DES REQUÊTES =============

@custom_staff_member_required
def requests_list(request):
    """Liste des modèles de requêtes"""
    documents = RequestDocument.objects.all().order_by('-created_at')
    
    # Filtrage
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(doc_type=doc_type)
        
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    documents_page = paginator.get_page(page_number)
    
    context = {
        'documents_page': documents_page,
        'doc_types': RequestDocument.DOC_TYPES,
        'current_type': doc_type,
    }
    return render(request, 'admin_dashboard/requests/list.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class RequestDocumentCreateView(CreateView):
    model = RequestDocument
    form_class = RequestDocumentForm
    template_name = 'admin_dashboard/requests/form.html'
    success_url = reverse_lazy('admin_requests_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le document a été ajouté avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class RequestDocumentUpdateView(UpdateView):
    model = RequestDocument
    form_class = RequestDocumentForm
    template_name = 'admin_dashboard/requests/form.html'
    success_url = reverse_lazy('admin_requests_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le document a été mis à jour avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class RequestDocumentDeleteView(DeleteView):
    model = RequestDocument
    template_name = 'admin_dashboard/requests/confirm_delete.html'
    success_url = reverse_lazy('admin_requests_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le document a été supprimé.')
        return super().form_valid(form)

# ============= GESTION DU DÉPARTEMENT =============

# --- ENSEIGNANTS ---
@custom_staff_member_required
def professors_list(request):
    """Liste des enseignants"""
    professors = Professor.objects.all().order_by('name')
    
    # Filtrage
    grade = request.GET.get('grade')
    if grade:
        professors = professors.filter(grade=grade)
        
    paginator = Paginator(professors, 15)
    page_number = request.GET.get('page')
    professors_page = paginator.get_page(page_number)
    
    context = {
        'professors_page': professors_page,
        'grades': Professor.GRADES,
        'current_grade': grade,
    }
    return render(request, 'admin_dashboard/department/professors_list.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class ProfessorCreateView(CreateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'admin_dashboard/department/professor_form.html'
    success_url = reverse_lazy('admin_professors_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'enseignant a été ajouté avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class ProfessorUpdateView(UpdateView):
    model = Professor
    form_class = ProfessorForm
    template_name = 'admin_dashboard/department/professor_form.html'
    success_url = reverse_lazy('admin_professors_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'enseignant a été mis à jour avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class ProfessorDeleteView(DeleteView):
    model = Professor
    template_name = 'admin_dashboard/department/professor_confirm_delete.html'
    success_url = reverse_lazy('admin_professors_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'enseignant a été supprimé.')
        return super().form_valid(form)

# --- SALLES ---
@custom_staff_member_required
def classrooms_list(request):
    """Liste des salles"""
    classrooms = Classroom.objects.all().order_by('name')
    
    paginator = Paginator(classrooms, 15)
    page_number = request.GET.get('page')
    classrooms_page = paginator.get_page(page_number)
    
    context = {'classrooms_page': classrooms_page}
    return render(request, 'admin_dashboard/department/classrooms_list.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class ClassroomCreateView(CreateView):
    model = Classroom
    form_class = ClassroomForm
    template_name = 'admin_dashboard/department/classroom_form.html'
    success_url = reverse_lazy('admin_classrooms_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'La salle a été ajoutée avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class ClassroomUpdateView(UpdateView):
    model = Classroom
    form_class = ClassroomForm
    template_name = 'admin_dashboard/department/classroom_form.html'
    success_url = reverse_lazy('admin_classrooms_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'La salle a été mise à jour avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class ClassroomDeleteView(DeleteView):
    model = Classroom
    template_name = 'admin_dashboard/department/classroom_confirm_delete.html'
    success_url = reverse_lazy('admin_classrooms_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'La salle a été supprimée.')
        return super().form_valid(form)

# --- DÉLÉGUÉS ---
@custom_staff_member_required
def delegates_list(request):
    """Liste des délégués"""
    delegates = Delegate.objects.all().order_by('level')
    
    paginator = Paginator(delegates, 15)
    page_number = request.GET.get('page')
    delegates_page = paginator.get_page(page_number)
    
    context = {'delegates_page': delegates_page}
    return render(request, 'admin_dashboard/department/delegates_list.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class DelegateCreateView(CreateView):
    model = Delegate
    form_class = DelegateForm
    template_name = 'admin_dashboard/department/delegate_form.html'
    success_url = reverse_lazy('admin_delegates_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le délégué a été ajouté avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class DelegateUpdateView(UpdateView):
    model = Delegate
    form_class = DelegateForm
    template_name = 'admin_dashboard/department/delegate_form.html'
    success_url = reverse_lazy('admin_delegates_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le délégué a été mis à jour avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class DelegateDeleteView(DeleteView):
    model = Delegate
    template_name = 'admin_dashboard/department/delegate_confirm_delete.html'
    success_url = reverse_lazy('admin_delegates_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le délégué a été supprimé.')
        return super().form_valid(form)

# ============= GESTION DU BLOG =============

@custom_staff_member_required
def blog_list(request):
    """Liste des articles de blog"""
    articles = BlogArticle.objects.all().order_by('-published_at')
    
    # Filtrage
    category = request.GET.get('category')
    if category:
        articles = articles.filter(category=category)
        
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    articles_page = paginator.get_page(page_number)
    
    context = {
        'articles_page': articles_page,
        'categories': BlogArticle.CATEGORIES,
        'current_category': category,
    }
    return render(request, 'admin_dashboard/blog/list.html', context)

@method_decorator(custom_staff_member_required, name='dispatch')
class BlogArticleCreateView(CreateView):
    model = BlogArticle
    form_class = BlogArticleForm
    template_name = 'admin_dashboard/blog/form.html'
    success_url = reverse_lazy('admin_blog_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'article a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class BlogArticleUpdateView(UpdateView):
    model = BlogArticle
    form_class = BlogArticleForm
    template_name = 'admin_dashboard/blog/form.html'
    success_url = reverse_lazy('admin_blog_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'article a été mis à jour avec succès.')
        return super().form_valid(form)

@method_decorator(custom_staff_member_required, name='dispatch')
class BlogArticleDeleteView(DeleteView):
    model = BlogArticle
    template_name = 'admin_dashboard/blog/confirm_delete.html'
    success_url = reverse_lazy('admin_blog_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'article a été supprimé.')
        return super().form_valid(form)


# =============================================================================
# J.U.IN 2026 — ADMIN VIEWS
# =============================================================================
from main.models import (
    JUINEdition, JUINCommission, JUINCommissionApplication, 
    JUINActivity, JUINDonation, JUINCompetition, JUINTeam, JUINSponsor
)


@custom_staff_member_required
def juin_dashboard(request):
    """Tableau de bord JUIN 2026"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    stats = {}
    if edition:
        qs = JUINCommissionApplication.objects.filter(commission__edition=edition)
        stats = {
            'total': qs.count(),
            'pending': qs.filter(statut='pending').count(),
            'approved': qs.filter(statut='approved').count(),
            'rejected': qs.filter(statut='rejected').count(),
            'activities': edition.activities.count(),
            'competitions': JUINCompetition.objects.filter(edition=edition).count(),
            'teams': JUINTeam.objects.filter(competition__edition=edition).count(),
            'total_donations': edition.donations.filter(is_confirmed=True).aggregate(Sum('montant'))['montant__sum'] or 0,
            'total_donors': edition.donations.filter(is_confirmed=True).count(),
        }
    recent_apps = JUINCommissionApplication.objects.filter(
        commission__edition=edition
    ).order_by('-date_postulation')[:5] if edition else []
    context = {'edition': edition, 'stats': stats, 'recent_apps': recent_apps}
    return render(request, 'admin_dashboard/juin/dashboard.html', context)


@custom_staff_member_required
def juin_applications_list(request):
    """Liste des candidatures commission J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    apps = JUINCommissionApplication.objects.filter(commission__edition=edition).select_related('commission').order_by('-date_postulation')

    statut = request.GET.get('statut')
    commission_id = request.GET.get('commission')
    search = request.GET.get('search')

    if statut and statut != 'None':
        apps = apps.filter(statut=statut)
    if commission_id and commission_id != 'None':
        apps = apps.filter(commission_id=commission_id)
    if search:
        apps = apps.filter(Q(nom_prenom__icontains=search) | Q(email__icontains=search))

    paginator = Paginator(apps, 20)
    page_number = request.GET.get('page')
    apps_page = paginator.get_page(page_number)

    commissions = JUINCommission.objects.filter(edition=edition) if edition else []
    context = {
        'apps_page': apps_page,
        'edition': edition,
        'commissions': commissions,
        'current_statut': statut,
        'current_commission': commission_id,
        'search_query': search,
        'statut_choices': JUINCommissionApplication.STATUT_CHOICES,
    }
    return render(request, 'admin_dashboard/juin/applications_list.html', context)


@custom_staff_member_required
def juin_application_detail(request, pk):
    """Détail + approuver/rejeter une candidature J.U.IN"""
    app = get_object_or_404(JUINCommissionApplication, pk=pk)
    edition = app.commission.edition

    if request.method == 'POST':
        action = request.POST.get('action')
        notify = request.POST.get('notify') == 'on'

        if action == 'approve':
            role = request.POST.get('commission_role', 'membre')
            new_commission_id = request.POST.get('commission_id')
            if new_commission_id:
                new_commission = get_object_or_404(JUINCommission, pk=new_commission_id, edition=edition)
                app.commission = new_commission
            app.statut = 'approved'
            app.commission_role = role
            app.date_traitement = timezone.now()
            app.save()
            messages.success(request, f"✅ {app.nom_prenom} approuvé(e) comme {app.get_commission_role_display()} dans {app.commission.code}.")

            if notify and app.email:
                try:
                    from django.template.loader import render_to_string
                    from django.core.mail import EmailMultiAlternatives
                    from django.utils.html import strip_tags
                    html = render_to_string('emails/juin_application_approved.html', {
                        'nom_prenom': app.nom_prenom,
                        'commission_name': app.commission.name,
                        'commission_code': app.commission.code,
                        'role': app.get_commission_role_display(),
                        'site_url': '',
                    })
                    msg = EmailMultiAlternatives(
                        subject=f'[J.U.IN 2026] Ta candidature a été approuvée ! 🎉',
                        body=strip_tags(html),
                        from_email=None,
                        to=[app.email],
                    )
                    msg.attach_alternative(html, 'text/html')
                    msg.send(fail_silently=True)
                except Exception as e:
                    messages.warning(request, f"Email non envoyé: {e}")

        elif action == 'reject':
            motif = request.POST.get('motif_rejet', '')
            app.statut = 'rejected'
            app.motif_rejet = motif
            app.date_traitement = timezone.now()
            app.save()
            messages.success(request, f"❌ {app.nom_prenom} rejeté(e).")

            if notify and app.email:
                try:
                    from django.template.loader import render_to_string
                    from django.core.mail import EmailMultiAlternatives
                    from django.utils.html import strip_tags
                    html = render_to_string('emails/juin_application_rejected.html', {
                        'nom_prenom': app.nom_prenom,
                        'commission_name': app.commission.name,
                        'motif': motif,
                    })
                    msg = EmailMultiAlternatives(
                        subject=f'[J.U.IN 2026] Résultat de ta candidature',
                        body=strip_tags(html),
                        from_email=None,
                        to=[app.email],
                    )
                    msg.attach_alternative(html, 'text/html')
                    msg.send(fail_silently=True)
                except Exception as e:
                    messages.warning(request, f"Email non envoyé: {e}")

        return redirect('admin_juin_application_detail', pk=pk)

    commissions = JUINCommission.objects.filter(edition=edition)
    context = {
        'app': app,
        'edition': edition,
        'commissions': commissions,
        'role_choices': JUINCommissionApplication.ROLE_CHOICES,
    }
    return render(request, 'admin_dashboard/juin/application_detail.html', context)


@custom_staff_member_required
def juin_generate_badge(request, pk):
    """Générer et télécharger le badge PDF d'un membre de commission"""
    from django.http import FileResponse
    from main.juin_badge_utils import generate_juin_commission_badge, get_juin_badge_path
    from django.core.files.storage import default_storage

    app = get_object_or_404(JUINCommissionApplication, pk=pk, statut='approved')

    # Generate if not exists
    badge_path = get_juin_badge_path(app)
    if not badge_path:
        generate_juin_commission_badge(app)
        badge_path = get_juin_badge_path(app)

    if badge_path:
        filename = f"Badge_JUIN2026_{app.nom_prenom.replace(' ', '_')}_{app.commission.code}.pdf"
        return FileResponse(open(badge_path, 'rb'), as_attachment=True, filename=filename)
    else:
        messages.error(request, "Erreur lors de la génération du badge.")
        return redirect('admin_juin_application_detail', pk=pk)


@custom_staff_member_required
def juin_activities_list(request):
    """Gérer les activités / agenda du J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    activities = JUINActivity.objects.filter(edition=edition).order_by('date_activity') if edition else []
    context = {'edition': edition, 'activities': activities}
    return render(request, 'admin_dashboard/juin/activities_list.html', context)


@custom_staff_member_required
def juin_activity_toggle_featured(request, pk):
    """Basculer le statut 'en vedette' d'une activité"""
    activity = get_object_or_404(JUINActivity, pk=pk)
    activity.is_featured = not activity.is_featured
    activity.save()
    return redirect('admin_juin_activities')

@custom_staff_member_required
def juin_donations_list(request):
    """Liste des dons J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()

    #  Toujours un QuerySet, jamais une liste
    donations = JUINDonation.objects.filter(edition=edition).order_by('-date_don') if edition else JUINDonation.objects.none()

    confirmed_only = request.GET.get('confirmed')
    if confirmed_only:
        donations = donations.filter(is_confirmed=True)

    total = donations.filter(is_confirmed=True).aggregate(Sum('montant'))['montant__sum'] or 0

    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        if donation_id:
            don = get_object_or_404(JUINDonation, pk=donation_id, edition=edition)
            don.is_confirmed = not don.is_confirmed
            don.save()
            messages.success(request, f"Don de {don.nom_prenom} : statut mis à jour.")
        return redirect('admin_juin_donations')

    paginator = Paginator(donations, 20)
    page_number = request.GET.get('page')
    donations_page = paginator.get_page(page_number)

    context = {
        'edition': edition,
        'donations_page': donations_page,
        'total': total,
        'confirmed_filter': confirmed_only,
    }
    return render(request, 'admin_dashboard/juin/donations_list.html', context)

from main.models import JUINSponsor

@custom_staff_member_required
def juin_sponsors_list(request):
    """Gérer les sponsors / partenaires du J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    sponsors = JUINSponsor.objects.filter(edition=edition).order_by('statut', 'tier') if edition else []
    
    context = {'edition': edition, 'sponsors': sponsors}
    return render(request, 'admin_dashboard/juin/sponsors_list.html', context)


@custom_staff_member_required
def juin_sponsor_detail(request, pk):
    """Détail et validation d'un sponsor"""
    sponsor = get_object_or_404(JUINSponsor, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            sponsor.statut = 'approved'
            sponsor.save()
            messages.success(request, f"Sponsor {sponsor.company_name} approuvé.")
        elif action == 'reject':
            sponsor.statut = 'rejected'
            sponsor.save()
            messages.warning(request, f"Sponsor {sponsor.company_name} rejeté.")
        elif action == 'delete':
            sponsor.delete()
            messages.info(request, "Sponsor supprimé.")
            return redirect('admin_juin_sponsors')
            
        return redirect('admin_juin_sponsor_detail', pk=pk)
        
    context = {'sponsor': sponsor, 'edition': sponsor.edition}
    return render(request, 'admin_dashboard/juin/sponsor_detail.html', context)


# --- JUIN Advanced Management ---

from .forms import (
    JUINEditionForm, JUINCommissionForm, JUINActivityForm, 
    JUINSponsorForm, JUINCompetitionForm, JUINTeamForm
)

@custom_staff_member_required
def juin_edition_manage(request):
    """Gérer l'édition courante ou en créer une nouvelle"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = JUINEditionForm(request.POST, request.FILES, instance=edition)
        if form.is_valid():
            form.save()
            messages.success(request, "Édition J.U.IN mise à jour.")
            return redirect('admin_juin_dashboard')
    else:
        form = JUINEditionForm(instance=edition)
    
    return render(request, 'admin_dashboard/juin/edition_form.html', {'form': form, 'edition': edition})

@custom_staff_member_required
def juin_activity_create(request):
    """Créer une activité J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = JUINActivityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Activité créée.")
            return redirect('admin_juin_activities')
    else:
        form = JUINActivityForm(initial={'edition': edition})
    
    return render(request, 'admin_dashboard/juin/activity_form.html', {'form': form, 'title': "Ajouter une activité"})

@custom_staff_member_required
def juin_activity_edit(request, pk):
    """Modifier une activité J.U.IN"""
    activity = get_object_or_404(JUINActivity, pk=pk)
    if request.method == 'POST':
        form = JUINActivityForm(request.POST, request.FILES, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, "Activité mise à jour.")
            return redirect('admin_juin_activities')
    else:
        form = JUINActivityForm(instance=activity)
    
    return render(request, 'admin_dashboard/juin/activity_form.html', {'form': form, 'title': "Modifier l'activité"})

@custom_staff_member_required
def juin_activity_delete(request, pk):
    """Supprimer une activité J.U.IN"""
    activity = get_object_or_404(JUINActivity, pk=pk)
    if request.method == 'POST':
        activity.delete()
        messages.success(request, "Activité supprimée.")
        return redirect('admin_juin_activities')
    return render(request, 'admin_dashboard/juin/confirm_delete.html', {'object': activity, 'cancel_url': 'admin_juin_activities'})

@custom_staff_member_required
def juin_sponsor_create(request):
    """Ajouter un sponsor J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = JUINSponsorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Sponsor ajouté.")
            return redirect('admin_juin_sponsors')
    else:
        form = JUINSponsorForm(initial={'edition': edition})
    
    return render(request, 'admin_dashboard/juin/sponsor_form.html', {'form': form, 'title': "Ajouter un sponsor"})

@custom_staff_member_required
def juin_sponsor_edit(request, pk):
    """Modifier un sponsor J.U.IN"""
    sponsor = get_object_or_404(JUINSponsor, pk=pk)
    if request.method == 'POST':
        form = JUINSponsorForm(request.POST, request.FILES, instance=sponsor)
        if form.is_valid():
            form.save()
            messages.success(request, "Sponsor mis à jour.")
            return redirect('admin_juin_sponsors')
    else:
        form = JUINSponsorForm(instance=sponsor)
    
    return render(request, 'admin_dashboard/juin/sponsor_form.html', {'form': form, 'title': "Modifier le sponsor"})

@custom_staff_member_required
def juin_commissions_manage(request):
    """Gérer les commissions J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    commissions = JUINCommission.objects.filter(edition=edition).order_by('order', 'name') if edition else []
    return render(request, 'admin_dashboard/juin/commissions_list.html', {'commissions': commissions, 'edition': edition})

@custom_staff_member_required
def juin_commission_create(request):
    """Créer une commission J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = JUINCommissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Commission créée.")
            return redirect('admin_juin_commissions')
    else:
        form = JUINCommissionForm(initial={'edition': edition})
    
    return render(request, 'admin_dashboard/juin/commission_form.html', {'form': form, 'title': "Créer une commission"})

@custom_staff_member_required
def juin_commission_edit(request, pk):
    """Modifier une commission J.U.IN"""
    commission = get_object_or_404(JUINCommission, pk=pk)
    if request.method == 'POST':
        form = JUINCommissionForm(request.POST, instance=commission)
        if form.is_valid():
            form.save()
            messages.success(request, "Commission mise à jour.")
            return redirect('admin_juin_commissions')
    else:
        form = JUINCommissionForm(instance=commission)
    
    return render(request, 'admin_dashboard/juin/commission_form.html', {'form': form, 'title': "Modifier la commission"})

@custom_staff_member_required
def juin_commission_delete(request, pk):
    """Supprimer une commission J.U.IN"""
    commission = get_object_or_404(JUINCommission, pk=pk)
    if request.method == 'POST':
        commission.delete()
        messages.success(request, "Commission supprimée.")
        return redirect('admin_juin_commissions')
    return render(request, 'admin_dashboard/juin/confirm_delete.html', {'object': commission, 'cancel_url': 'admin_juin_commissions'})

@custom_staff_member_required
def juin_competitions_list(request):
    """Liste des compétitions J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    competitions = JUINCompetition.objects.filter(edition=edition).order_by('comp_type', 'name') if edition else []
    return render(request, 'admin_dashboard/juin/competitions_list.html', {'competitions': competitions, 'edition': edition})

@custom_staff_member_required
def juin_competition_create(request):
    """Créer une compétition J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = JUINCompetitionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Compétition créée.")
            return redirect('admin_juin_competitions')
    else:
        form = JUINCompetitionForm(initial={'edition': edition})
    return render(request, 'admin_dashboard/juin/competition_form.html', {'form': form, 'title': "Créer une compétition"})

@custom_staff_member_required
def juin_competition_edit(request, pk):
    """Modifier une compétition J.U.IN"""
    comp = get_object_or_404(JUINCompetition, pk=pk)
    if request.method == 'POST':
        form = JUINCompetitionForm(request.POST, request.FILES, instance=comp)
        if form.is_valid():
            form.save()
            messages.success(request, "Compétition mise à jour.")
            return redirect('admin_juin_competitions')
    else:
        form = JUINCompetitionForm(instance=comp)
    return render(request, 'admin_dashboard/juin/competition_form.html', {'form': form, 'title': "Modifier la compétition"})

@custom_staff_member_required
def juin_competition_delete(request, pk):
    """Supprimer une compétition J.U.IN"""
    comp = get_object_or_404(JUINCompetition, pk=pk)
    if request.method == 'POST':
        comp.delete()
        messages.success(request, "Compétition supprimée.")
        return redirect('admin_juin_competitions')
    return render(request, 'admin_dashboard/juin/confirm_delete.html', {'object': comp, 'cancel_url': 'admin_juin_competitions'})

@custom_staff_member_required
def juin_teams_list(request):
    """Liste des équipes/candidats J.U.IN"""
    edition = JUINEdition.objects.filter(is_active=True).first()
    teams = JUINTeam.objects.filter(competition__edition=edition).select_related('competition').order_by('-date_registration') if edition else []
    
    comp_id = request.GET.get('competition')
    if comp_id:
        teams = teams.filter(competition_id=comp_id)
        
    paginator = Paginator(teams, 20)
    page_number = request.GET.get('page')
    teams_page = paginator.get_page(page_number)
    
    competitions = JUINCompetition.objects.filter(edition=edition) if edition else []
    context = {
        'teams_page': teams_page,
        'edition': edition,
        'competitions': competitions,
        'current_competition': comp_id,
    }
    return render(request, 'admin_dashboard/juin/teams_list.html', context)

@custom_staff_member_required
def juin_team_edit(request, pk):
    """Modifier une équipe J.U.IN"""
    team = get_object_or_404(JUINTeam, pk=pk)
    if request.method == 'POST':
        form = JUINTeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipe mise à jour.")
            return redirect('admin_juin_teams')
    else:
        form = JUINTeamForm(instance=team)
    return render(request, 'admin_dashboard/juin/team_form.html', {'form': form, 'title': "Modifier l'équipe"})

@custom_staff_member_required
def juin_team_delete(request, pk):
    """Supprimer une équipe J.U.IN"""
    team = get_object_or_404(JUINTeam, pk=pk)
    if request.method == 'POST':
        team.delete()
        messages.success(request, "Équipe supprimée.")
        return redirect('admin_juin_teams')
    return render(request, 'admin_dashboard/juin/confirm_delete.html', {'object': team, 'cancel_url': 'admin_juin_teams'})


# ============================================================
# PROJECT SUBMISSIONS MANAGEMENT
# ============================================================

@custom_staff_member_required
def project_submissions_list(request):
    """Liste des projets soumis via le formulaire public."""
    queryset = ProjectSubmission.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    reviewed_filter = request.GET.get('reviewed', '')
    q = request.GET.get('q', '')
    if q:
        queryset = queryset.filter(
            Q(project_name__icontains=q) | Q(submitter_name__icontains=q) | Q(submitter_email__icontains=q)
        )
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if reviewed_filter == '0':
        queryset = queryset.filter(is_reviewed=False)
    elif reviewed_filter == '1':
        queryset = queryset.filter(is_reviewed=True)
    paginator = Paginator(queryset, 20)
    submissions = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_dashboard/projects/submissions_list.html', {
        'submissions': submissions,
        'q': q,
        'status_filter': status_filter,
        'reviewed_filter': reviewed_filter,
        'pending_count': ProjectSubmission.objects.filter(is_reviewed=False).count(),
    })


@custom_staff_member_required
def project_submission_detail(request, pk):
    """Détail et traitement d'une soumission de projet."""
    submission = get_object_or_404(ProjectSubmission, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'publish':
            Project.objects.get_or_create(
                title_fr=submission.project_name,
                defaults={'description_fr': submission.description or '', 'status': 'active', 'is_featured': False}
            )
            submission.is_reviewed = True
            submission.save()
            try:
                from django.core.mail import send_mail
                from django.conf import settings as dj_settings
                send_mail(
                    '✅ Votre projet est publié — COM.S.AS',
                    f'Bonjour {submission.submitter_name},\n\nVotre projet "{submission.project_name}" a été publié sur la plateforme COM.S.AS !\n\nCordialement,\nL\'équipe COM.S.AS',
                    dj_settings.DEFAULT_FROM_EMAIL, [submission.submitter_email], fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, f'Projet "{submission.project_name}" publié et porteur notifié par email.')
        elif action == 'reviewed':
            submission.is_reviewed = True
            submission.save()
            messages.success(request, 'Soumission marquée comme traitée.')
        elif action == 'delete':
            submission.delete()
            messages.success(request, 'Soumission supprimée.')
            return redirect('admin_project_submissions')
        return redirect('admin_project_submission_detail', pk=pk)
    return render(request, 'admin_dashboard/projects/submission_detail.html', {'submission': submission})


@custom_staff_member_required
def project_submission_delete(request, pk):
    submission = get_object_or_404(ProjectSubmission, pk=pk)
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'Soumission supprimée.')
        return redirect('admin_project_submissions')
    return render(request, 'admin_dashboard/projects/submission_confirm_delete.html', {'object': submission})


# ============================================================
# CLUB COMMISSIONS MANAGEMENT
# ============================================================

@custom_staff_member_required
def club_commissions_list(request):
    commissions = ClubCommission.objects.annotate(
        app_count=Count('applications'),
        approved_count=Count('applications', filter=Q(applications__status='approved')),
        pending_count=Count('applications', filter=Q(applications__status='pending')),
    ).order_by('name')
    return render(request, 'admin_dashboard/commissions/list.html', {
        'commissions': commissions,
    })


@custom_staff_member_required
def club_commission_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', 'fa-users')[:50] # Sécurité max_length=50
        if name:
            from django.utils.text import slugify
            slug = slugify(name)
            original_slug = slug
            counter = 1
            while ClubCommission.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            ClubCommission.objects.create(name=name, slug=slug, description=description, icon=icon)
            messages.success(request, 'Commission créée avec succès.')
            return redirect('admin_club_commissions')
    return render(request, 'admin_dashboard/commissions/form.html', {'action': 'Créer'})


@custom_staff_member_required
def club_commission_edit(request, pk):
    commission = get_object_or_404(ClubCommission, pk=pk)
    if request.method == 'POST':
        commission.name = request.POST.get('name', commission.name)
        commission.description = request.POST.get('description', commission.description)
        commission.icon = request.POST.get('icon', commission.icon)[:50] # Sécurité max_length=50
        commission.save()
        messages.success(request, 'Commission mise à jour.')
        return redirect('admin_club_commissions')
    return render(request, 'admin_dashboard/commissions/form.html', {'commission': commission, 'action': 'Modifier'})


@custom_staff_member_required
def club_commission_delete(request, pk):
    commission = get_object_or_404(ClubCommission, pk=pk)
    if request.method == 'POST':
        commission.delete()
        messages.success(request, 'Commission supprimée.')
        return redirect('admin_club_commissions')
    return render(request, 'admin_dashboard/commissions/confirm_delete.html', {'object': commission})


# ============================================================
# CLUB COMMISSION APPLICATIONS MANAGEMENT
# ============================================================

@custom_staff_member_required
def club_applications_list(request):
    queryset = ClubCommissionApplication.objects.select_related('commission').order_by('-created_at')
    status_f = request.GET.get('status', '')
    comm_f = request.GET.get('commission', '')
    q = request.GET.get('q', '')
    if q:
        queryset = queryset.filter(Q(nom_prenom__icontains=q) | Q(email__icontains=q))
    if status_f:
        queryset = queryset.filter(status=status_f)
    if comm_f:
        queryset = queryset.filter(commission__id=comm_f)
    paginator = Paginator(queryset, 20)
    applications = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_dashboard/commissions/applications_list.html', {
        'applications': applications,
        'commissions': ClubCommission.objects.all(),
        'status_f': status_f,
        'comm_f': comm_f,
        'q': q,
        'total': ClubCommissionApplication.objects.count(),
        'pending': ClubCommissionApplication.objects.filter(status='pending').count(),
        'approved': ClubCommissionApplication.objects.filter(status='approved').count(),
    })


@custom_staff_member_required
def club_application_detail(request, pk):
    application = get_object_or_404(ClubCommissionApplication, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        subject = body = None
        if action == 'approve':
            application.status = 'approved'
            application.save()
            member, created = Member.objects.get_or_create(
                email=application.email,
                defaults={
                    'nom_prenom': application.nom_prenom, 'telephone': application.telephone,
                    'niveau': application.niveau, 'photo': application.photo,
                    'is_active': True, 'member_type': 'simple',
                }
            )
            if not created:
                member.is_active = True
                member.save()
            subject = '✅ Candidature acceptée — Commission Club'
            body = f'Bonjour {application.nom_prenom},\n\nVotre candidature pour la commission "{application.commission}" a été acceptée. Bienvenue !\n\nCordialement,\nL\'équipe COM.S.AS'
            messages.success(request, f'Candidature de {application.nom_prenom} approuvée et membre activé.')
        elif action == 'reject':
            application.status = 'rejected'
            application.save()
            subject = '❌ Candidature non retenue — Commission Club'
            body = f'Bonjour {application.nom_prenom},\n\nVotre candidature pour la commission "{application.commission}" n\'a pas été retenue cette fois-ci.\n\nCordialement,\nL\'équipe COM.S.AS'
            messages.warning(request, f'Candidature de {application.nom_prenom} rejetée.')
        elif action == 'delete':
            application.delete()
            messages.success(request, 'Candidature supprimée.')
            return redirect('admin_club_applications')
        if subject and body:
            try:
                from django.core.mail import send_mail
                from django.conf import settings as dj_settings
                send_mail(subject, body, dj_settings.DEFAULT_FROM_EMAIL, [application.email], fail_silently=True)
            except Exception:
                pass
        return redirect('admin_club_application_detail', pk=pk)
    return render(request, 'admin_dashboard/commissions/application_detail.html', {'application': application})


@custom_staff_member_required
def club_application_delete(request, pk):
    application = get_object_or_404(ClubCommissionApplication, pk=pk)
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Candidature supprimée.')
        return redirect('admin_club_applications')
    return render(request, 'admin_dashboard/commissions/confirm_delete.html', {'object': application})
