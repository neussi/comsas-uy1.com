from django.contrib import admin
from .models import (
    Member, Project, Event, EventRegistration, News, Gallery, 
    Contact, SiteSettings, SponsorshipSession, Mentor, Mentee
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


# --- ADMIN CLASSES ---

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom', 'member_type', 'promotion', 'is_active')
    list_filter = ('member_type', 'is_active', 'promotion')
    search_fields = ('nom_prenom', 'email')
    actions = [validate_and_send_card, export_to_csv]

    def save_model(self, request, obj, form, change):
        if change:
            # Check if is_active changed from False to True
            try:
                old_obj = Member.objects.get(pk=obj.pk)
                if not old_obj.is_active and obj.is_active:
                     super().save_model(request, obj, form, change)
                     # Send email
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
    list_display = ('title_fr', 'status', 'budget_required', 'budget_collected', 'created_at')
    list_filter = ('status', 'is_featured')
    search_fields = ('title_fr',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title_fr', 'date_event', 'location', 'is_active')
    list_filter = ('is_active', 'is_featured')
    search_fields = ('title_fr', 'location')

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom', 'event', 'email', 'is_confirmed', 'registration_date')
    list_filter = ('is_confirmed', 'event')

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
