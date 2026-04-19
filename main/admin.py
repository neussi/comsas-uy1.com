from django.contrib import admin
from .models import (
    Member, Project, Event, EventRegistration, 
    Professor, Classroom, Delegate, News, Gallery, GalleryAlbum, 
    Contact, SiteSettings, SponsorshipSession, Mentor, Mentee, Match,
    Contest, Candidate, Vote, Archive, ArchiveComment,
    JUINEdition, JUINCommission, JUINCommissionApplication, JUINCompetition,
    JUINActivity, JUINDonation, JUINSponsor, JUINTeam,
    ProjectSubmission, ClubCommission, ClubCommissionApplication,
    AcademicResource, JobOffer
)

# Sponsorship System Utils
import csv
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import Count
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from django.core.mail import EmailMessage
from django.conf import settings
from .utils import generate_member_card, send_member_card_email

# --- Actions Communes et Spécifiques doivent être définies AVANT leur utilisation ---

def export_to_csv(modeladmin, request, queryset):
    """Export selected items to CSV"""
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name}.csv'
    writer = csv.writer(response)
    
    # Headers
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])
    
    # Data
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if callable(value):
                value = value()
            data_row.append(str(value))
        writer.writerow(data_row)
    return response
export_to_csv.short_description = "Exporter vers Excel (CSV)"

def validate_and_send_card(modeladmin, request, queryset):
    """
    Valide le membre et envoie sa carte de membre par email.
    """
    success_count = 0
    fail_count = 0

    for member in queryset:
        try:
            # 1. Valider le membre
            member.is_active = True
            member.save()

            # 2. Envoyer Email via Utils
            if send_member_card_email(member):
                success_count += 1
            else:
                fail_count += 1
            
        except Exception as e:
            # En prod, on loggerait l'erreur
            print(f"Erreur pour {member.nom_prenom}: {e}")
            fail_count += 1

    if success_count > 0:
        messages.success(request, f"{success_count} membres validés et informés par email.")
    if fail_count > 0:
        messages.warning(request, f"{fail_count} erreurs lors de l'envoi.")

validate_and_send_card.short_description = "Valider et Envoyer Carte de Membre"

def match_mentees(modeladmin, request, queryset):
    """Auto-match mentees to available mentors based on specialty"""
    success_count = 0
    fail_count = 0
    
    from .models import Match

    for mentee in queryset.filter(match__isnull=True):
        # Find mentors in same session with matching specialty and available spots
        available_mentors = Mentor.objects.annotate(
            current_count=Count('match_set')
        ).filter(
            session=mentee.session,
            specialty=mentee.desired_specialty,
            current_count__lt=models.F('max_mentees')
        ).order_by('current_count')
        
        if available_mentors.exists():
            mentor = available_mentors.first()
            Match.objects.create(
                session=mentee.session, 
                mentor=mentor, 
                mentee=mentee
            )
            success_count += 1
        else:
            fail_count += 1
            
    if success_count > 0:
        messages.success(request, f"{success_count} filleuls ont été attribués avec succès.")
    if fail_count > 0:
        messages.warning(request, f"{fail_count} filleuls n'ont pas pu être attribués (pas de parrain disponible dans la spécialité).")
match_mentees.short_description = "Lancer l'attribution automatique (Matching)"

def export_sponsorship_pdf(modeladmin, request, queryset):
    """Generate PDF report for Sponsorship matches"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_parrainage.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Rapport de Parrainage - A²ELBM2", styles['Title']))
    elements.append(Spacer(1, 12))

    # Table Data
    data = [['Filleul', 'Niveau', 'Spécialité Visée', 'Parrain Attribué', 'Téléphone Parrain']]
    
    for mentee in queryset:
        match = getattr(mentee, 'match', None)
        mentor = match.mentor if match else None
        
        mentor_info = f"{mentor.first_name} {mentor.last_name}" if mentor else "Non attribué"
        mentor_phone = mentor.phone if mentor else "-"
        
        data.append([
            f"{mentee.first_name} {mentee.last_name}",
            mentee.get_level_display(),
            mentee.get_desired_specialty_display(),
            mentor_info,
            mentor_phone
        ])

    # Table Style
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    return response
export_sponsorship_pdf.short_description = "Générer Rapport PDF"

def send_email_safe(to, subject, body):
    """Utilitaire : envoie un email en silence (ne bloque pas si erreur)"""
    try:
        from django.core.mail import send_mail
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=True)
        return True
    except Exception:
        return False


def approve_application_action(modeladmin, request, queryset):
    """Approuve et envoie email de confirmation autoamtiquement."""
    count = 0
    for app in queryset.exclude(statut='approved'):
        app.statut = 'approved'
        from django.utils import timezone
        if hasattr(app, 'date_traitement'):
            app.date_traitement = timezone.now()
        app.save()
        send_email_safe(
            to=app.email,
            subject="✅ Candidature acceptée — COM.S.AS",
            body=(
                f"Bonjour {app.nom_prenom},\n\n"
                "Félicitations ! Votre candidature a été examinée et acceptée.\n"
                "Vous recevrez prochainement les prochaines instructions.\n\n"
                "Cordialement,\nL'équipe COM.S.AS"
            )
        )
        count += 1
    messages.success(request, f"{count} candidature(s) approuvée(s) et email(s) envoyé(s).")
approve_application_action.short_description = "✅ Approuver et notifier par email"


def reject_application_action(modeladmin, request, queryset):
    """Rejette et envoie email de regret."""
    count = 0
    for app in queryset.exclude(statut='rejected'):
        app.statut = 'rejected'
        from django.utils import timezone
        if hasattr(app, 'date_traitement'):
            app.date_traitement = timezone.now()
        app.save()
        send_email_safe(
            to=app.email,
            subject="❌ Candidature non retenue — COM.S.AS",
            body=(
                f"Bonjour {app.nom_prenom},\n\n"
                "Merci pour l'intérêt que vous portez à COM.S.AS.\n"
                "Après examen, votre candidature n'a malheureusement pas été retenue cette fois.\n"
                "N'hésitez pas à retenter votre chance lors de la prochaine édition.\n\n"
                "Cordialement,\nL'équipe COM.S.AS"
            )
        )
        count += 1
    messages.warning(request, f"{count} candidature(s) rejetée(s) et email(s) envoyé(s).")
reject_application_action.short_description = "❌ Rejeter et notifier par email"


def approve_commission_application(modeladmin, request, queryset):
    """Approuve la candidature et crée un profil membre si inexistant"""
    success_count = 0
    for app in queryset.filter(status='pending'):
        app.status = 'approved'
        app.save()
        member, created = Member.objects.get_or_create(
            email=app.email,
            defaults={
                'nom_prenom': app.nom_prenom,
                'telephone': app.telephone,
                'niveau': app.niveau,
                'photo': app.photo,
                'is_active': True,
                'member_type': 'simple'
            }
        )
        if not created:
            member.is_active = True
            member.save()
        send_email_safe(
            to=app.email,
            subject="✅ Candidature acceptée — Commission Club",
            body=(
                f"Bonjour {app.nom_prenom},\n\n"
                "Nous avons le plaisir de vous informer que votre candidature \n"
                f"pour la commission '{app.commission}' a été acceptée.\n\n"
                "Cordialement,\nL'équipe COM.S.AS"
            )
        )
        success_count += 1
    messages.success(request, f"{success_count} candidatures approuvées, membres synchronisés et emails envoyés.")
approve_commission_application.short_description = "✅ Approuver, créer membre et notifier"


def reject_club_commission(modeladmin, request, queryset):
    """Rejette candidature commission Club avec email"""
    count = 0
    for app in queryset.exclude(status='rejected'):
        app.status = 'rejected'
        app.save()
        send_email_safe(
            to=app.email,
            subject="❌ Candidature non retenue — Commission Club",
            body=(
                f"Bonjour {app.nom_prenom},\n\n"
                f"Merci de l'intérêt pour la commission '{app.commission}'.\n"
                "Votre candidature n'a malheureusement pas été retenue cette fois-ci.\n\n"
                "Cordialement,\nL'équipe COM.S.AS"
            )
        )
        count += 1
    messages.warning(request, f"{count} candidature(s) rejetée(s) et email(s) envoyé(s).")
reject_club_commission.short_description = "❌ Rejeter et notifier par email"


def publish_project(modeladmin, request, queryset):
    """Marque un projet soumis comme validé et le rend visible sur le site."""
    count = 0
    for submission in queryset:
        # Create or link to a real Project visible on the site
        project, created = Project.objects.get_or_create(
            title_fr=submission.project_name,
            defaults={
                'description_fr': submission.description,
                'status': 'active',
                'is_featured': False,
            }
        )
        submission.is_reviewed = True
        submission.save()
        send_email_safe(
            to=submission.submitter_email,
            subject="✅ Votre projet a été publié — COM.S.AS",
            body=(
                f"Bonjour {submission.submitter_name},\n\n"
                f"Votre projet '{ submission.project_name}' a été examiné et publié sur la plateforme COM.S.AS !\n"
                "Vous pouvez le consulter sur notre site.\n\n"
                "Cordialement,\nL'équipe COM.S.AS"
            )
        )
        count += 1
    messages.success(request, f"{count} projet(s) publié(s) sur le site et porteurs notifiés.")
publish_project.short_description = "✅ Valider et publier le projet sur le site"


def mark_reviewed(modeladmin, request, queryset):
    """Marque comme traité sans publier."""
    queryset.update(is_reviewed=True)
    messages.success(request, "Projets marqués comme traités.")
mark_reviewed.short_description = "🔄 Marquer comme traité (sans publication)"


def approve_commission_application(modeladmin, request, queryset):
    """Approuve la candidature et crée un profil membre si inexistant (Club)"""
    success_count = 0
    for app in queryset.filter(status='pending'):
        app.status = 'approved'
        app.save()
        member, created = Member.objects.get_or_create(
            email=app.email,
            defaults={
                'nom_prenom': app.nom_prenom,
                'telephone': app.telephone,
                'niveau': app.niveau,
                'photo': app.photo,
                'is_active': True,
                'member_type': 'simple'
            }
        )
        if not created:
            member.is_active = True
            member.save()
        send_email_safe(
            to=app.email,
            subject="✅ Candidature Commission Club — Acceptée",
            body=(
                f"Bonjour {app.nom_prenom},\n\n"
                f"Votre candidature pour la commission '{app.commission}' a été acceptée. Bienvenue !\n\n"
                "Cordialement,\nL'équipe COM.S.AS"
            )
        )
        success_count += 1
    messages.success(request, f"{success_count} candidatures approuvées, membres synchronisés et emails envoyés.")
approve_commission_application.short_description = "✅ Approuver, créer membre et notifier"


# --- ADMIN CLASSES ---

@admin.register(JUINTeam)
class JUINTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition', 'captain_name', 'members_count', 'statut')
    list_filter = ('competition__edition', 'competition', 'statut')
    search_fields = ('name', 'captain_name', 'captain_email')
    list_editable = ('statut',)
    actions = ['approve_teams']

    def approve_teams(self, request, queryset):
        count = queryset.update(statut='approved')
        self.message_user(request, f"{count} équipes ont été approuvées.")
    approve_teams.short_description = "Marquer les équipes sélectionnées comme approuvées"


@admin.register(AcademicResource)
class AcademicResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'niveau', 'subject', 'is_approved', 'created_at')
    list_filter = ('resource_type', 'niveau', 'is_approved')
    search_fields = ('title', 'subject', 'description')
    list_editable = ('is_approved',)
    actions = ['approve_resources']
    
    def approve_resources(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} ressources ont été approuvées.")
    approve_resources.short_description = "Approuver les ressources sélectionnées"


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'offer_type', 'is_approved', 'is_active', 'created_at')
    list_filter = ('offer_type', 'is_approved', 'is_active')
    search_fields = ('title', 'company', 'location', 'description')
    list_editable = ('is_approved', 'is_active')
    actions = ['approve_offers']
    
    def approve_offers(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} offres ont été approuvées.")
    approve_offers.short_description = "Approuver les offres sélectionnées"

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom', 'email', 'telephone', 'niveau', 'member_type', 'is_active', 'date_adhesion')
    list_filter = ('member_type', 'is_active', 'niveau')
    search_fields = ('nom_prenom', 'email', 'telephone', 'matricule')
    list_editable = ('is_active', 'member_type')
    actions = [validate_and_send_card, export_to_csv]
    fieldsets = (
        ('Identité & Contact', {
            'fields': ('nom_prenom', 'matricule', 'email', 'telephone', 'date_naissance', 'lieu_naissance', 'adresse', 'photo')
        }),
        ('Statut & Rôle', {
            'fields': ('member_type', 'poste_bureau', 'niveau', 'promotion', 'profession', 'is_active')
        }),
        ('Portfolio & Réseaux', {
            'fields': ('bio', 'skills', 'technologies', 'other_roles', 'needs', 'github_url', 'linkedin_url', 'twitter_url', 'website_url', 'portfolio_slug', 'portfolio_enabled')
        }),
    )

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = Member.objects.get(pk=obj.pk)
                if not old_obj.is_active and obj.is_active:
                    super().save_model(request, obj, form, change)
                    if send_member_card_email(obj):
                        messages.success(request, f"Carte de membre envoyée à {obj.nom_prenom}")
                    else:
                        messages.warning(request, f"Erreur lors de l'envoi de la carte à {obj.nom_prenom}")
                    return
            except Member.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title_fr', 'status', 'budget_required', 'budget_collected', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured')
    list_editable = ('status', 'is_featured')
    search_fields = ('title_fr', 'description_fr')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title_fr', 'date_event', 'location', 'is_active', 'is_featured', 'certificates_sent')
    list_filter = ('is_active', 'is_featured', 'certificates_sent')
    list_editable = ('is_active', 'is_featured')
    search_fields = ('title_fr', 'location')
    actions = ['send_event_certificates']

    def send_event_certificates(self, request, queryset):
        """
        Génère et envoie les attestations par email pour tous les participants confirmés des événements sélectionnés.
        """
        for event in queryset:
            registrations = EventRegistration.objects.filter(event=event, is_confirmed=True)
            count = 0
            
            from .certificate_utils import generate_certificate
            from .badge_utils import generate_badge
            
            for reg in registrations:
                try:
                    # 1. Générer l'attestation si activée
                    cert_url = None
                    if event.certificate_enabled:
                        cert_url = generate_certificate(reg)
                    
                    # 2. Générer le badge si activé
                    if event.badge_enabled:
                        generate_badge(reg)
                        
                    # 3. Envoyer l'email
                    subject = f"Votre attestation : {event.title_fr}"
                    message = f"Bonjour {reg.nom_prenom},\n\nFélicitations pour votre participation à l'événement '{event.title_fr}'.\n\nVous trouverez ci-joint votre attestation de participation (si applicable) ainsi que votre badge.\n\nCordialement,\nL'équipe COM.S.AS"
                    
                    email = EmailMessage(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [reg.email],
                    )
                    
                    # Attach certificate
                    if reg.certificate_pdf:
                        email.attach_file(reg.certificate_pdf.path)
                    
                    # Attach badge
                    if reg.badge_pdf:
                        email.attach_file(reg.badge_pdf.path)
                        
                    email.send(fail_silently=True)
                    count += 1
                except Exception as e:
                    self.message_user(request, f"Erreur pour {reg.email}: {str(e)}", messages.ERROR)
            
            event.certificates_sent = True
            event.save()
            self.message_user(request, f"{count} attestations/badges envoyés pour '{event.title_fr}'.")
            
    send_event_certificates.short_description = "📧 Générer et envoyer les attestations"

    fieldsets = (
        ('Informations Générales', {
            'fields': ('title_fr', 'title_en', 'description_fr', 'description_en', 'image', 'date_event', 
                       'location', 'max_participants', 'registration_deadline', 'is_featured', 'is_active')
        }),
        ('Configuration des Attestations', {
            'fields': ('certificate_enabled', 'certificate_title', 'certificate_main_text', 'certificate_description', 
                       'certificate_president_name', 'certificate_president_title', 
                       'certificate_dept_head_name', 'certificate_dept_head_title', 'president_signature', 'certificates_sent'),
            'classes': ('collapse',)
        }),
        ('Partenaires', {
            'fields': ('partner_logo_1', 'partner_logo_2', 'partner_logo_3'),
            'classes': ('collapse',)
        }),
        ('Badges & Galerie', {
            'fields': ('badge_enabled', 'gallery_album'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom', 'event', 'email', 'telephone', 'is_confirmed', 'registration_date')
    list_filter = ('is_confirmed', 'event')
    search_fields = ('nom_prenom', 'email', 'telephone')
    list_editable = ('is_confirmed',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title_fr', 'publication_date', 'is_published', 'is_featured')
    list_filter = ('is_published', 'is_featured')

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title_fr', 'media_type', 'created_at')
    list_filter = ('media_type', 'is_featured')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom', 'sujet', 'created_at', 'is_read')
    list_filter = ('is_read', 'is_replied')

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name',)

@admin.register(SponsorshipSession)
class SponsorshipSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'level', 'specialty', 'max_mentees', 'current_mentees_count')
    list_filter = ('level', 'specialty', 'session')
    search_fields = ('first_name', 'last_name', 'email')
    actions = [export_to_csv]

@admin.register(Mentee)
class MenteeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'level', 'desired_specialty')
    list_filter = ('level', 'desired_specialty', 'session')
    search_fields = ('first_name', 'last_name', 'email')
    actions = [match_mentees, export_to_csv, export_sponsorship_pdf]

# =============================================================================
# ADMIN POUR NOUVELLES FONCTIONNALITÉS
# =============================================================================

from .models import RequestDocument, Professor, Classroom, Delegate, BlogArticle, PastPresident

@admin.register(PastPresident)
class PastPresidentAdmin(admin.ModelAdmin):
    list_display = ('name', 'mandate_start', 'mandate_end', 'is_current')
    list_filter = ('is_current', 'mandate_start')
    search_fields = ('name', 'current_function')
    ordering = ('-mandate_start',)
    fieldsets = (
        ('Identité', {
            'fields': ('name', 'photo', 'current_function')
        }),
        ('Mandat', {
            'fields': ('mandate_start', 'mandate_end', 'is_current')
        }),
        ('Contenu', {
            'fields': ('bio',)
        }),
        ('Réseaux Sociaux', {
            'fields': ('facebook_link', 'linkedin_link', 'twitter_link'),
            'classes': ('collapse',)
        }),
    )

@admin.register(RequestDocument)
class RequestDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'doc_type', 'downloads_count', 'created_at')
    list_filter = ('doc_type', 'created_at')
    search_fields = ('title', 'description')
    fieldsets = (
        ('Informations Générales', {
            'fields': ('title', 'doc_type', 'description')
        }),
        ('Fichier & Aperçu', {
            'fields': ('file', 'image_preview')
        }),
        ('Statistiques', {
            'fields': ('downloads_count',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'specialty', 'email', 'is_active')
    list_filter = ('grade', 'is_active')
    search_fields = ('name', 'specialty', 'email')
    fieldsets = (
        ('Identité', {
            'fields': ('name', 'grade', 'specialty', 'email', 'profile_photo')
        }),
        ('Bureau', {
            'fields': ('office_description', 'office_photo')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_lab')
    list_filter = ('is_lab',)
    search_fields = ('name', 'location_description')
    fieldsets = (
        ('Détails de la salle', {
            'fields': ('name', 'capacity', 'is_lab', 'photo')
        }),
        ('Localisation', {
            'fields': ('location_description',)
        }),
    )

@admin.register(Delegate)
class DelegateAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'year', 'phone', 'email')
    list_filter = ('level', 'year')
    search_fields = ('name', 'email', 'phone')
    fieldsets = (
        ('Identité', {
            'fields': ('name', 'email', 'phone', 'photo')
        }),
        ('Mandat', {
            'fields': ('level', 'year', 'motto')
        }),
    )

@admin.register(BlogArticle)
class BlogArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'published_at', 'views_count', 'is_published')
    list_filter = ('category', 'is_published', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'category', 'image', 'content')
        }),
        ('Publication', {
            'fields': ('author', 'published_at', 'is_published')
        }),
        ('Statistiques', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'submitter_name', 'submitter_email', 'domain', 'status', 'is_reviewed', 'created_at')
    list_filter = ('status', 'is_reviewed', 'domain')
    search_fields = ('project_name', 'submitter_name', 'submitter_email')
    list_editable = ('is_reviewed',)
    ordering = ('-created_at',)
    actions = [publish_project, mark_reviewed]
    fieldsets = (
        ('Projet', {'fields': ('project_name', 'description', 'domain', 'status', 'additional_info', 'logo')}),
        ('Porteur', {'fields': ('submitter_name', 'submitter_email', 'submitter_tel', 'presentation_time')}),
        ('Statut Admin', {'fields': ('is_reviewed',)}),
    )

@admin.register(ClubCommission)
class ClubCommissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ClubCommissionApplication)
class ClubCommissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom', 'email', 'telephone', 'commission', 'role_applied', 'motivation_courte', 'status', 'created_at')
    list_filter = ('status', 'commission', 'role_applied')
    search_fields = ('nom_prenom', 'email', 'telephone')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    actions = [approve_commission_application, reject_club_commission, export_to_csv]
    fieldsets = (
        ('Candidat', {'fields': ('nom_prenom', 'email', 'telephone', 'niveau', 'photo')}),
        ('Candidature', {'fields': ('commission', 'role_applied', 'motivation')}),
        ('Décision', {'fields': ('status', 'created_at')}),
    )

    def motivation_courte(self, obj):
        return (obj.motivation or '')[:60] + '...' if obj.motivation else ''
@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'allow_public_candidates', 'is_active')
    list_filter = ('is_active', 'allow_public_candidates')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'contest', 'status', 'votes_count', 'total_revenue', 'created_at')
    list_filter = ('status', 'contest')
    search_fields = ('name', 'description')
    list_editable = ('status',)
    actions = ['approve_candidates', 'reject_candidates']

    def approve_candidates(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f"{count} candidats ont été approuvés.")
    approve_candidates.short_description = "✅ Approuver les candidats sélectionnés"

    def reject_candidates(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count} candidats ont été rejetés.")
    reject_candidates.short_description = "❌ Rejeter les candidats sélectionnés"

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'contest', 'candidate', 'vote_count', 'amount', 'status', 'created_at')
    list_filter = ('status', 'contest', 'created_at')
    search_fields = ('transaction_id', 'voter_phone', 'voter_email')
    readonly_fields = ('created_at',)

