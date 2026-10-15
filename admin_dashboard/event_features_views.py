import csv
import random
import string
from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.paginator import Paginator

from main.models import Event, EventRegistration, EventRegistrationCode, EventAttendance, Gallery
from .views import custom_staff_member_required
from .forms import EventMediaForm


def generate_code_string(length=6):
    """Génère un code lisible de 6 caractères (lettres majuscules et chiffres sans confusion)"""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(random.choice(chars) for _ in range(length))


# ==============================================================================
# 1. GESTION DES CODES D'INSCRIPTION PRÉSENTIELS (USAGE UNIQUE)
# ==============================================================================

@custom_staff_member_required
def event_codes_manage(request, pk):
    """Page de gestion et génération des codes d'inscription pour un événement"""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            try:
                quantity = int(request.POST.get('quantity', 20))
                if quantity <= 0:
                    quantity = 20
                if quantity > 500:
                    quantity = 500
            except ValueError:
                quantity = 20
            
            existing_codes = set(EventRegistrationCode.objects.filter(event=event).values_list('code', flat=True))
            new_codes = []
            attempts = 0
            max_attempts = quantity * 15
            
            while len(new_codes) < quantity and attempts < max_attempts:
                attempts += 1
                c = generate_code_string(6)
                if c not in existing_codes:
                    existing_codes.add(c)
                    new_codes.append(EventRegistrationCode(event=event, code=c))
            
            EventRegistrationCode.objects.bulk_create(new_codes)
            messages.success(request, f"{len(new_codes)} nouveau(x) code(s) d'inscription généré(s) avec succès !")
            return redirect('admin_event_codes', pk=pk)
            
        elif action == 'delete_unused':
            deleted_count, _ = EventRegistrationCode.objects.filter(event=event, is_used=False).delete()
            messages.success(request, f"{deleted_count} code(s) inutilisé(s) supprimé(s).")
            return redirect('admin_event_codes', pk=pk)

    codes_qs = event.registration_codes.all().select_related('used_by').order_by('is_used', '-created_at')
    
    # Filtre de recherche
    search_query = request.GET.get('q', '').strip()
    if search_query:
        codes_qs = codes_qs.filter(code__icontains=search_query)

    status_filter = request.GET.get('status')
    if status_filter == 'used':
        codes_qs = codes_qs.filter(is_used=True)
    elif status_filter == 'available':
        codes_qs = codes_qs.filter(is_used=False)

    paginator = Paginator(codes_qs, 30)
    page_number = request.GET.get('page')
    codes_page = paginator.get_page(page_number)

    context = {
        'event': event,
        'codes_page': codes_page,
        'total_codes': event.registration_codes.count(),
        'used_codes': event.registration_codes.filter(is_used=True).count(),
        'available_codes': event.registration_codes.filter(is_used=False).count(),
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_dashboard/events/codes.html', context)


@custom_staff_member_required
def event_codes_download_txt(request, pk):
    """Télécharger la liste des codes disponibles sous forme de fichier TXT imprimable"""
    event = get_object_or_404(Event, pk=pk)
    only_available = request.GET.get('filter') != 'all'
    
    if only_available:
        codes = event.registration_codes.filter(is_used=False).order_by('id')
        title_suffix = "DISPONIBLES"
    else:
        codes = event.registration_codes.all().order_by('is_used', 'id')
        title_suffix = "TOUS"

    response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="codes_{event.title_fr[:20].replace(" ", "_")}_{title_suffix.lower()}.txt"'

    lines = [
        "==========================================================================",
        " CLUB INFORMATIQUE COMSAS - UNIVERSITÉ DE YAOUNDÉ 1",
        f" CODES D'INSCRIPTION EN PRÉSENTIEL ({title_suffix})",
        "==========================================================================",
        f" Activité / Événement : {event.title_fr}",
        f" Date de l'événement  : {event.date_event.strftime('%d/%m/%Y à %H:%M')}",
        f" Lieu                 : {event.location}",
        f" Fichier généré le    : {timezone.now().strftime('%d/%m/%Y à %H:%M')}",
        f" Nombre total de codes: {codes.count()}",
        "--------------------------------------------------------------------------",
        " INSTRUCTIONS :",
        " 1. Distribuez ces codes aux étudiants en présentiel.",
        " 2. Chaque code comporte 6 caractères et ne peut être utilisé qu'UNE seule fois.",
        " 3. Dès validation lors de l'inscription en ligne, le code est désactivé.",
        "==========================================================================\n",
    ]

    for index, code_obj in enumerate(codes, 1):
        status = "UTILISÉ" if code_obj.is_used else "DISPONIBLE"
        used_info = f" (Utilisé par {code_obj.used_by.nom_prenom})" if code_obj.is_used and code_obj.used_by else ""
        lines.append(f"[{index:03d}]  CODE : {code_obj.code}    [{status}{used_info}]")

    lines.append("\n======================= FIN DU DOCUMENT =======================")
    response.write("\n".join(lines))
    return response


@custom_staff_member_required
def event_codes_download_csv(request, pk):
    """Exporter les codes d'inscription au format CSV"""
    event = get_object_or_404(Event, pk=pk)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="codes_{event.title_fr[:20].replace(" ", "_")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Code (6 car.)', 'Statut', 'Date Création', 'Utilisé Par', 'Email Participant', 'Date Utilisation'])
    
    for c in event.registration_codes.all().select_related('used_by').order_by('is_used', 'code'):
        writer.writerow([
            c.code,
            'Utilisé' if c.is_used else 'Disponible',
            c.created_at.strftime('%Y-%m-%d %H:%M'),
            c.used_by.nom_prenom if c.used_by else '',
            c.used_by.email if c.used_by else '',
            c.used_at.strftime('%Y-%m-%d %H:%M') if c.used_at else ''
        ])
    return response


# ==============================================================================
# 2. FEUILLE D'ÉMARGEMENT / APPEL & VALIDATION DE PARTICIPATION
# ==============================================================================

def send_participation_congratulations_email(registration):
    """Envoie l'email de félicitations confirmant la participation effective et l'arrivée de l'attestation"""
    event = registration.event
    subject = f"Félicitations pour votre participation à {event.title_fr} !"
    html_content = render_to_string('emails/event_participation_congratulations.html', {
        'participant_name': registration.nom_prenom,
        'event_title': event.title_fr,
        'event_date': event.date_event,
        'event_location': event.location,
    })
    text_content = (
        f"Bonjour {registration.nom_prenom},\n\n"
        f"Le comité d'organisation du Club Informatique COMSAS vous félicite chaleureusement "
        f"pour votre présence et votre participation active à l'événement '{event.title_fr}'.\n\n"
        f"Votre présence a bien été validée.\n\n"
        f"Votre attestation officielle de participation est en cours d'établissement et vous sera "
        f"transmise très prochainement par email.\n\n"
        f"Cordialement,\nL'équipe COMS.A.S\nUniversité de Yaoundé 1"
    )
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [registration.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)
    registration.congratulations_email_sent = True
    registration.save(update_fields=['congratulations_email_sent'])


@custom_staff_member_required
def event_attendance_sheet(request, pk):
    """Feuille d'émargement et d'appel multi-jours avec validation finale et félicitations"""
    event = get_object_or_404(Event, pk=pk)
    duration_days = max(1, event.duration_days)
    days_list = list(range(1, duration_days + 1))

    registrations = event.eventregistration_set.filter(is_confirmed=True).prefetch_related('attendances').order_by('nom_prenom')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_attendance':
            # Enregistrer la feuille d'appel complète
            for reg in registrations:
                for day in days_list:
                    key = f'att_{reg.id}_{day}'
                    is_present = bool(request.POST.get(key))
                    EventAttendance.objects.update_or_create(
                        registration=reg,
                        day_number=day,
                        defaults={'is_present': is_present}
                    )
            messages.success(request, "La feuille d'appel a été enregistrée avec succès.")
            return redirect('admin_event_attendance', pk=pk)

        elif action == 'validate_single':
            reg_id = request.POST.get('registration_id')
            reg = get_object_or_404(EventRegistration, id=reg_id, event=event)
            send_email = request.POST.get('send_email') == '1'
            
            reg.has_participated = True
            reg.participation_validated_at = timezone.now()
            reg.save(update_fields=['has_participated', 'participation_validated_at'])

            if send_email and not reg.congratulations_email_sent:
                try:
                    send_participation_congratulations_email(reg)
                    messages.success(request, f"Participation validée et email de félicitations envoyé à {reg.nom_prenom} !")
                except Exception as e:
                    messages.warning(request, f"Participation validée mais erreur d'envoi email pour {reg.nom_prenom}: {e}")
            else:
                messages.success(request, f"Participation validée pour {reg.nom_prenom}.")
            return redirect('admin_event_attendance', pk=pk)

        elif action == 'bulk_validate_and_email':
            selected_ids = request.POST.getlist('selected_reg_ids')
            if not selected_ids:
                messages.warning(request, "Aucun participant sélectionné.")
                return redirect('admin_event_attendance', pk=pk)

            validated_count = 0
            emails_sent_count = 0
            regs_to_update = EventRegistration.objects.filter(event=event, id__in=selected_ids)

            for reg in regs_to_update:
                reg.has_participated = True
                reg.participation_validated_at = timezone.now()
                reg.save(update_fields=['has_participated', 'participation_validated_at'])
                validated_count += 1

                if not reg.congratulations_email_sent:
                    try:
                        send_participation_congratulations_email(reg)
                        emails_sent_count += 1
                    except Exception as e:
                        print(f"Erreur envoi félicitations à {reg.email}: {e}")

            messages.success(request, f"{validated_count} participant(s) validé(s), et {emails_sent_count} email(s) de félicitations envoyé(s) !")
            return redirect('admin_event_attendance', pk=pk)

    # Préparer les données de chaque participant pour affichage simple
    participants_data = []
    for reg in registrations:
        attendance_map = {att.day_number: att.is_present for att in reg.attendances.all()}
        days_presence = [{'day': day, 'present': attendance_map.get(day, False)} for day in days_list]
        participants_data.append({
            'registration': reg,
            'days_presence': days_presence,
            'present_count': sum(1 for d in days_presence if d['present']),
        })

    # Statistiques de présence par jour
    stats_per_day = []
    for day in days_list:
        present_count = EventAttendance.objects.filter(registration__event=event, day_number=day, is_present=True).count()
        stats_per_day.append({'day': day, 'present_count': present_count})

    context = {
        'event': event,
        'duration_days': duration_days,
        'days_list': days_list,
        'participants_data': participants_data,
        'stats_per_day': stats_per_day,
        'total_registrations': registrations.count(),
        'total_participated': registrations.filter(has_participated=True).count(),
        'total_emails_sent': registrations.filter(congratulations_email_sent=True).count(),
    }
    return render(request, 'admin_dashboard/events/attendance.html', context)


@custom_staff_member_required
def event_attendance_export_csv(request, pk):
    """Exporter la feuille de présence et d'émargement au format CSV"""
    event = get_object_or_404(Event, pk=pk)
    duration_days = max(1, event.duration_days)
    days_list = list(range(1, duration_days + 1))
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="presence_{event.title_fr[:20].replace(" ", "_")}.csv"'
    
    writer = csv.writer(response)
    header = ['Nom & Prénom', 'Email', 'Téléphone', 'Promotion', 'Code Inscription']
    for day in days_list:
        header.append(f'Jour {day}')
    header.extend(['Participation Validée', 'Email Félicitations Envoyé'])
    writer.writerow(header)

    registrations = event.eventregistration_set.filter(is_confirmed=True).prefetch_related('attendances').order_by('nom_prenom')
    for reg in registrations:
        att_map = {att.day_number: att.is_present for att in reg.attendances.all()}
        row = [
            reg.nom_prenom,
            reg.email,
            reg.telephone,
            reg.promotion,
            reg.registration_code_entered or '',
        ]
        for day in days_list:
            row.append('Présent' if att_map.get(day, False) else 'Absent')
        row.append('Oui' if reg.has_participated else 'Non')
        row.append('Oui' if reg.congratulations_email_sent else 'Non')
        writer.writerow(row)

    return response


# ==============================================================================
# 3. GESTION DES MÉDIAS DE L'ÉVÉNEMENT (PHOTOS & VIDÉOS EXPLICATIVES)
# ==============================================================================

@custom_staff_member_required
def event_media_manage(request, pk):
    """Permet à l'administrateur d'ajouter et gérer les vidéos et images explicatives d'un événement"""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        form = EventMediaForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.event = event
            media.save()
            messages.success(request, "Le média explicatif a été ajouté avec succès à l'événement !")
            return redirect('admin_event_media', pk=pk)
    else:
        form = EventMediaForm()

    media_list = event.gallery_media.all().order_by('-created_at')

    context = {
        'event': event,
        'form': form,
        'media_list': media_list,
    }
    return render(request, 'admin_dashboard/events/media.html', context)


@custom_staff_member_required
def event_media_delete(request, pk, media_id):
    """Supprimer un média explicatif lié à un événement"""
    event = get_object_or_404(Event, pk=pk)
    media = get_object_or_404(Gallery, id=media_id, event=event)
    media.delete()
    messages.success(request, "Le média a été supprimé.")
    return redirect('admin_event_media', pk=pk)
