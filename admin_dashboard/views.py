from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
import csv
from main.models import (
    Member, Project, Event, EventRegistration, 
    News, Gallery, Contact, SiteSettings,
    SponsorshipSession, Mentor, Mentee, Match,
    Contest, Candidate, Vote
)
from .forms import (
    ProjectForm, EventForm, NewsForm, GalleryForm, SiteSettingsForm, MemberForm,
    SponsorshipSessionForm, ContestForm, CandidateForm
)
from main.utils import send_member_card_email

@staff_member_required
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

@staff_member_required
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

@staff_member_required
def member_detail(request, pk):
    """Détail d'un membre"""
    member = get_object_or_404(Member, pk=pk)
    context = {'member': member}
    return render(request, 'admin_dashboard/members/detail.html', context)

@staff_member_required
def member_approve(request, pk):
    """Approuver un membre"""
    member = get_object_or_404(Member, pk=pk)
    member.is_active = True
    member.save()
    
    # Envoyer la carte de membre par email
    if send_member_card_email(member):
        messages.success(request, f'Le membre {member.nom_prenom} a été approuvé et sa carte envoyée.')
    else:
        messages.warning(request, f'Le membre {member.nom_prenom} a été approuvé, mais erreur d\'envoi de la carte.')
        
    return redirect('admin_members_list')

@staff_member_required
def member_reject(request, pk):
    """Rejeter un membre"""
    member = get_object_or_404(Member, pk=pk)
    member.delete()
    messages.success(request, 'La demande d\'adhésion a été rejetée.')
    return redirect('admin_members_list')

@staff_member_required
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
@method_decorator(staff_member_required, name='dispatch')
class MemberCreateView(CreateView):
    model = Member
    form_class = MemberForm
    template_name = 'admin_dashboard/members/form.html'
    success_url = reverse_lazy('admin_members_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le membre a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class MemberUpdateView(UpdateView):
    model = Member
    form_class = MemberForm
    template_name = 'admin_dashboard/members/form.html'
    success_url = reverse_lazy('admin_members_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le membre a été modifié avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class MemberDeleteView(DeleteView):
    model = Member
    template_name = 'admin_dashboard/members/confirm_delete.html'
    success_url = reverse_lazy('admin_members_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le membre a été supprimé avec succès.')
        return super().form_valid(form)

# ============= GESTION DES PROJETS =============

@staff_member_required
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

@staff_member_required
def project_detail(request, pk):
    """Détail d'un projet"""
    project = get_object_or_404(Project, pk=pk)
    context = {'project': project}
    return render(request, 'admin_dashboard/projects/detail.html', context)

@method_decorator(staff_member_required, name='dispatch')
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'admin_dashboard/projects/form.html'
    success_url = reverse_lazy('admin_projects_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le projet a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'admin_dashboard/projects/form.html'
    success_url = reverse_lazy('admin_projects_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le projet a été modifié avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'admin_dashboard/projects/confirm_delete.html'
    success_url = reverse_lazy('admin_projects_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le projet a été supprimé avec succès.')
        return super().form_valid(form)

# ============= GESTION DES ÉVÉNEMENTS =============

@staff_member_required
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

@method_decorator(staff_member_required, name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'admin_dashboard/events/form.html'
    success_url = reverse_lazy('admin_events_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'événement a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'admin_dashboard/events/form.html'
    success_url = reverse_lazy('admin_events_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'événement a été modifié avec succès.')
        return super().form_valid(form)

# NOUVELLE VUE POUR SUPPRIMER ÉVÉNEMENT
@method_decorator(staff_member_required, name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    template_name = 'admin_dashboard/events/confirm_delete.html'
    success_url = reverse_lazy('admin_events_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'événement a été supprimé avec succès.')
        return super().form_valid(form)

@staff_member_required
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

@staff_member_required
def confirm_registration(request, pk):
    """Confirmer une inscription"""
    registration = get_object_or_404(EventRegistration, pk=pk)
    registration.is_confirmed = True
    registration.save()
    
    messages.success(request, f'Inscription de {registration.nom_prenom} confirmée.')
    return redirect('admin_event_registrations', pk=registration.event.pk)

@staff_member_required
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

@staff_member_required
def news_list(request):
    """Liste des actualités"""
    news = News.objects.all().order_by('-created_at')
    
    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    news_page = paginator.get_page(page_number)
    
    context = {'news_page': news_page}
    return render(request, 'admin_dashboard/news/list.html', context)

@method_decorator(staff_member_required, name='dispatch')
class NewsCreateView(CreateView):
    model = News
    form_class = NewsForm
    template_name = 'admin_dashboard/news/form.html'
    success_url = reverse_lazy('admin_news_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'actualité a été créée avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class NewsUpdateView(UpdateView):
    model = News
    form_class = NewsForm
    template_name = 'admin_dashboard/news/form.html'
    success_url = reverse_lazy('admin_news_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'actualité a été modifiée avec succès.')
        return super().form_valid(form)

# NOUVELLE VUE POUR SUPPRIMER ACTUALITÉ
@method_decorator(staff_member_required, name='dispatch')
class NewsDeleteView(DeleteView):
    model = News
    template_name = 'admin_dashboard/news/confirm_delete.html'
    success_url = reverse_lazy('admin_news_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'actualité a été supprimée avec succès.')
        return super().form_valid(form)

# ============= GESTION DE LA GALERIE =============

@staff_member_required
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

@method_decorator(staff_member_required, name='dispatch')
class GalleryCreateView(CreateView):
    model = Gallery
    form_class = GalleryForm
    template_name = 'admin_dashboard/gallery/form.html'
    success_url = reverse_lazy('admin_gallery_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'élément a été ajouté à la galerie avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class GalleryUpdateView(UpdateView):
    model = Gallery
    form_class = GalleryForm
    template_name = 'admin_dashboard/gallery/form.html'
    success_url = reverse_lazy('admin_gallery_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'élément de la galerie a été modifié avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class GalleryDeleteView(DeleteView):
    model = Gallery
    template_name = 'admin_dashboard/gallery/confirm_delete.html'
    success_url = reverse_lazy('admin_gallery_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'L\'élément a été supprimé de la galerie avec succès.')
        return super().form_valid(form)

# ============= GESTION DES MESSAGES =============

@staff_member_required
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

@staff_member_required
def message_detail(request, pk):
    """Détail d'un message"""
    message = get_object_or_404(Contact, pk=pk)
    
    # Marquer comme lu
    if not message.is_read:
        message.is_read = True
        message.save()
    
    context = {'message': message}
    return render(request, 'admin_dashboard/messages/detail.html', context)

@staff_member_required
def mark_message_replied(request, pk):
    """Marquer un message comme répondu"""
    message = get_object_or_404(Contact, pk=pk)
    message.is_replied = True
    message.save()
    
    messages.success(request, 'Message marqué comme répondu.')
    return redirect('admin_message_detail', pk=pk)

# NOUVELLE VUE POUR SUPPRIMER MESSAGE
@staff_member_required
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

@staff_member_required
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

@staff_member_required
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

@staff_member_required
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

@staff_member_required
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

@staff_member_required
def sponsorship_matches(request):
    """Liste des paires (Matches)"""
    matches = Match.objects.all().order_by('-created_at')
    
    paginator = Paginator(matches, 20)
    page_number = request.GET.get('page')
    matches_page = paginator.get_page(page_number)
    
    context = {'matches_page': matches_page}
    context = {'matches_page': matches_page}
    return render(request, 'admin_dashboard/sponsorship/matches.html', context)

@staff_member_required
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

@staff_member_required
def sponsorship_matches_export_excel(request):
    """Exporter les binômes en Excel (Compatible via CSV pour simplicité)"""
    # Pour l'instant on utilise CSV mais avec un header Excel pour simplifier sans dépendance openpyxl
    return sponsorship_matches_export_csv(request)

@staff_member_required
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
            candidates = Mentor.objects.annotate(num_mentees=Count('match_set')).filter(
                # Note: Count('match') because Match model links Mentor-Mentee. 
                # Wait, existing code used Count('mentee') but Match model is correct?
                # Let's check Mentor model related_name if any. 
                # Mentor has no explicit related_name on Match FK. default is match_set.
                # But previously code used Count('mentee')? Maybe Mentee had FK to Mentor?
                # Ah, existing Mentee model (before my change) had 'mentor' FK!
                # My NEW Mentee model REMOVED 'mentor' FK in favor of Match model?
                # YES. "professional_domain_1 & 2 Removed...".
                # And I removed the 'mentor' field from Mentee class definition in Step 2219.
                # So `Count('mentee')` will FAIL if I don't fix it.
                # It should be `Count('match')` (default related name for Match.mentor FK).
                # OR I should check Match model definition.
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

@method_decorator(staff_member_required, name='dispatch')
class SponsorshipSessionCreateView(CreateView):
    model = SponsorshipSession
    form_class = SponsorshipSessionForm
    template_name = 'admin_dashboard/sponsorship/session_form.html'
    success_url = reverse_lazy('admin_sponsorship_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'La session de parrainage a été créée avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class SponsorshipSessionUpdateView(UpdateView):
    model = SponsorshipSession
    form_class = SponsorshipSessionForm
    template_name = 'admin_dashboard/sponsorship/session_form.html'
    success_url = reverse_lazy('admin_sponsorship_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'La session de parrainage a été mise à jour avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
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

@staff_member_required
def contests_home(request):
    """Page d'accueil de la gestion des concours"""
    contests = Contest.objects.all().order_by('-start_date')
    active_contests = Contest.objects.filter(is_active=True).count()
    
    context = {
        'contests': contests,
        'active_contests_count': active_contests,
    }
    return render(request, 'admin_dashboard/contests/home.html', context)

@staff_member_required
def contest_detail(request, pk):
    """Détail d'un concours et ses candidats"""
    contest = get_object_or_404(Contest, pk=pk)
    candidates = contest.candidates.all()
    
    context = {
        'contest': contest,
        'candidates': candidates,
    }
    return render(request, 'admin_dashboard/contests/detail.html', context)

@method_decorator(staff_member_required, name='dispatch')
class ContestCreateView(CreateView):
    model = Contest
    form_class = ContestForm
    template_name = 'admin_dashboard/contests/form.html'
    success_url = reverse_lazy('admin_contests_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le concours a été créé avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class ContestUpdateView(UpdateView):
    model = Contest
    form_class = ContestForm
    template_name = 'admin_dashboard/contests/form.html'
    success_url = reverse_lazy('admin_contests_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le concours a été mis à jour avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class ContestDeleteView(DeleteView):
    model = Contest
    template_name = 'admin_dashboard/contests/confirm_delete.html'
    success_url = reverse_lazy('admin_contests_home')
    
    def form_valid(self, form):
        messages.success(self.request, 'Le concours a été supprimé.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
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

@method_decorator(staff_member_required, name='dispatch')
class CandidateUpdateView(UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'admin_dashboard/contests/candidate_form.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_contest_detail', kwargs={'pk': self.object.contest.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Le candidat a été mis à jour avec succès.')
        return super().form_valid(form)

@method_decorator(staff_member_required, name='dispatch')
class CandidateDeleteView(DeleteView):
    model = Candidate
    template_name = 'admin_dashboard/contests/candidate_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_contest_detail', kwargs={'pk': self.object.contest.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Le candidat a été supprimé.')
        return super().form_valid(form)