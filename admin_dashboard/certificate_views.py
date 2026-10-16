from django.shortcuts import render, get_object_or_404, redirect
from .views import custom_staff_member_required
from django.contrib import messages
from io import BytesIO
from django.db.models import Q
from main.models import Event, EventRegistration

# Certificate Management Views

@custom_staff_member_required
def event_certificates_manage(request, pk):
    """Manage certificates for an event"""
    event = get_object_or_404(Event, pk=pk)
    registrations = EventRegistration.objects.filter(
        event=event, 
        is_confirmed=True
    ).prefetch_related('attendances').order_by('nom_prenom')
    
    present_query = Q(has_participated=True) | Q(attendances__is_present=True)
    present_registrations = registrations.filter(present_query).distinct()
    
    total_participants = registrations.count()
    present_count = present_registrations.count()
    certificates_generated = registrations.exclude(certificate_pdf='').count()
    present_certificates_generated = present_registrations.exclude(certificate_pdf='').count()
    
    context = {
        'event': event,
        'registrations': registrations,
        'total_participants': total_participants,
        'present_count': present_count,
        'certificates_generated': certificates_generated,
        'present_certificates_generated': present_certificates_generated,
    }
    
    return render(request, 'admin_dashboard/events/certificates.html', context)


@custom_staff_member_required
def generate_all_certificates(request, pk):
    """Generate certificates for all confirmed participants"""
    from main.certificate_utils import generate_certificate
    
    event = get_object_or_404(Event, pk=pk)
    
    if not event.certificate_enabled:
        messages.error(request, "Les attestations ne sont pas activées pour cet événement.")
        return redirect('admin_event_certificates', pk=pk)
    
    registrations = EventRegistration.objects.filter(event=event, is_confirmed=True)
    generated_count = 0
    
    for registration in registrations:
        try:
            generate_certificate(registration)
            generated_count += 1
        except Exception as e:
            messages.warning(request, f"Erreur pour {registration.nom_prenom}: {str(e)}")
    
    messages.success(request, f"{generated_count} attestation(s) générée(s) avec succès!")
    return redirect('admin_event_certificates', pk=pk)


@custom_staff_member_required
def generate_present_certificates(request, pk):
    """Générer les attestations UNIQUEMENT pour les participants marqués présents"""
    from main.certificate_utils import generate_certificate
    
    event = get_object_or_404(Event, pk=pk)
    
    if not event.certificate_enabled:
        messages.error(request, "Les attestations ne sont pas activées pour cet événement.")
        return redirect('admin_event_certificates', pk=pk)
    
    present_query = Q(has_participated=True) | Q(attendances__is_present=True)
    present_registrations = EventRegistration.objects.filter(
        event=event, 
        is_confirmed=True
    ).filter(present_query).distinct()
    
    if not present_registrations.exists():
        messages.warning(request, "Aucun participant n'a été marqué comme présent pour cet événement. Veuillez d'abord émarger ou valider les présences.")
        return redirect('admin_event_certificates', pk=pk)
    
    generated_count = 0
    for registration in present_registrations:
        try:
            generate_certificate(registration)
            generated_count += 1
        except Exception as e:
            messages.warning(request, f"Erreur pour {registration.nom_prenom}: {str(e)}")
    
    messages.success(request, f"{generated_count} attestation(s) générée(s) avec succès pour les participants présents !")
    return redirect('admin_event_certificates', pk=pk)


@custom_staff_member_required
def send_present_certificates(request, pk):
    """
    Générer et envoyer par email les attestations (et badges) UNIQUEMENT aux participants marqués présents.
    """
    from main.certificate_utils import generate_certificate
    from main.badge_utils import generate_badge
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.conf import settings
    
    event = get_object_or_404(Event, pk=pk)
    
    if not event.certificate_enabled:
        messages.error(request, "Les attestations ne sont pas activées pour cet événement.")
        return redirect('admin_event_certificates', pk=pk)
        
    present_query = Q(has_participated=True) | Q(attendances__is_present=True)
    present_registrations = EventRegistration.objects.filter(
        event=event, 
        is_confirmed=True
    ).filter(present_query).distinct()
    
    if not present_registrations.exists():
        messages.warning(request, "Aucun participant n'a été marqué comme présent pour cet événement. Veuillez d'abord émarger ou valider les présences.")
        return redirect('admin_event_certificates', pk=pk)
        
    count = 0
    errors = 0
    
    for reg in present_registrations:
        try:
            # 1. Générer l'attestation si manquante
            if not reg.certificate_pdf or not reg.certificate_pdf.name:
                generate_certificate(reg)
                reg.refresh_from_db()
                
            # 2. Générer le badge si activé et manquant
            if event.badge_enabled and (not reg.badge_pdf or not reg.badge_pdf.name):
                generate_badge(reg)
                reg.refresh_from_db()
                
            # 3. Préparer l'email officiel
            subject = f"Votre Attestation de Participation — {event.title_fr}"
            html_content = render_to_string('emails/event_certificate_delivery.html', {
                'participant_name': reg.nom_prenom,
                'event_title': event.title_fr,
                'event_date': event.date_event,
                'event_location': event.location,
            })
            text_content = (
                f"Bonjour {reg.nom_prenom},\n\n"
                f"Félicitations pour votre présence et participation active à l'événement \"{event.title_fr}\".\n\n"
                f"Veuillez trouver ci-joint votre attestation officielle de participation délivrée par le COMSAS (Université de Yaoundé 1).\n\n"
                f"Cordialement,\n"
                f"L'équipe du Club Informatique COMSAS\n"
                f"Université de Yaoundé 1"
            )
            
            from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
            email = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [reg.email],
            )
            email.attach_alternative(html_content, "text/html")
            
            # Attacher l'attestation
            if reg.certificate_pdf and reg.certificate_pdf.name:
                try:
                    email.attach_file(reg.certificate_pdf.path)
                except Exception as file_err:
                    print(f"Erreur pièce jointe attestation: {file_err}")
                    
            # Attacher le badge si activé
            if event.badge_enabled and reg.badge_pdf and reg.badge_pdf.name:
                try:
                    email.attach_file(reg.badge_pdf.path)
                except Exception as file_err:
                    print(f"Erreur pièce jointe badge: {file_err}")
                    
            email.send(fail_silently=False)
            reg.congratulations_email_sent = True
            reg.save(update_fields=['congratulations_email_sent'])
            count += 1
        except Exception as e:
            errors += 1
            print(f"Erreur envoi attestation pour {reg.email}: {e}")
            
    event.certificates_sent = True
    event.save(update_fields=['certificates_sent'])
    
    if errors > 0:
        messages.warning(request, f"{count} attestation(s) envoyée(s) par email aux participants présents. ({errors} erreur(s) d'envoi)")
    else:
        messages.success(request, f"{count} attestation(s) envoyée(s) par email avec succès à tous les participants présents !")
        
    return redirect('admin_event_certificates', pk=pk)


@custom_staff_member_required
def send_single_certificate(request, registration_id):
    """Envoyer l'attestation par email à un participant individuel"""
    from main.certificate_utils import generate_certificate
    from main.badge_utils import generate_badge
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.conf import settings
    
    registration = get_object_or_404(EventRegistration, id=registration_id)
    event = registration.event
    
    if not event.certificate_enabled:
        messages.error(request, "Les attestations ne sont pas activées pour cet événement.")
        return redirect('admin_event_certificates', pk=event.pk)
        
    try:
        if not registration.certificate_pdf or not registration.certificate_pdf.name:
            generate_certificate(registration)
            registration.refresh_from_db()
            
        if event.badge_enabled and (not registration.badge_pdf or not registration.badge_pdf.name):
            generate_badge(registration)
            registration.refresh_from_db()
            
        subject = f"Votre Attestation de Participation — {event.title_fr}"
        html_content = render_to_string('emails/event_certificate_delivery.html', {
            'participant_name': registration.nom_prenom,
            'event_title': event.title_fr,
            'event_date': event.date_event,
            'event_location': event.location,
        })
        text_content = (
            f"Bonjour {registration.nom_prenom},\n\n"
            f"Félicitations pour votre participation à l'événement \"{event.title_fr}\".\n\n"
            f"Vous trouverez en pièce jointe votre attestation officielle de participation délivrée par le COMSAS (Université de Yaoundé 1).\n\n"
            f"Cordialement,\n"
            f"L'équipe COMSAS\n"
            f"Université de Yaoundé 1"
        )
        
        from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [registration.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        if registration.certificate_pdf and registration.certificate_pdf.name:
            email.attach_file(registration.certificate_pdf.path)
            
        if event.badge_enabled and registration.badge_pdf and registration.badge_pdf.name:
            email.attach_file(registration.badge_pdf.path)
            
        email.send(fail_silently=False)
        registration.congratulations_email_sent = True
        registration.save(update_fields=['congratulations_email_sent'])
        messages.success(request, f"Attestation envoyée par email avec succès à {registration.nom_prenom} ({registration.email}) !")
    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi de l'attestation à {registration.nom_prenom} : {str(e)}")
        
    return redirect('admin_event_certificates', pk=event.pk)


@custom_staff_member_required
def download_certificates_zip(request, pk):
    """Download certificates as a ZIP file (all or present only)"""
    import zipfile
    from django.http import HttpResponse
    
    event = get_object_or_404(Event, pk=pk)
    registrations = EventRegistration.objects.filter(
        event=event, 
        is_confirmed=True
    ).exclude(certificate_pdf='')
    
    only_present = request.GET.get('only_present') == '1'
    if only_present:
        registrations = registrations.filter(
            Q(has_participated=True) | Q(attendances__is_present=True)
        ).distinct()
    
    if not registrations.exists():
        messages.error(request, "Aucune attestation correspondante n'a été trouvée pour cet événement.")
        return redirect('admin_event_certificates', pk=pk)
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for registration in registrations:
            if registration.certificate_pdf:
                file_path = registration.certificate_pdf.path
                filename = f"attestation_{registration.nom_prenom.replace(' ', '_')}_{registration.uuid}.pdf"
                try:
                    zip_file.write(file_path, filename)
                except Exception as e:
                    print(f"Error adding {file_path} to ZIP: {e}")
    
    # Prepare response
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    suffix = "_presents" if only_present else ""
    response['Content-Disposition'] = f'attachment; filename="attestations_{event.title_fr.replace(" ", "_")}{suffix}.zip"'
    
    return response


@custom_staff_member_required
def regenerate_certificate(request, registration_id):
    """Regenerate a single certificate"""
    from main.certificate_utils import generate_certificate
    
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    try:
        generate_certificate(registration)
        messages.success(request, f"Attestation régénérée pour {registration.nom_prenom}")
    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
    
    return redirect('admin_event_certificates', pk=registration.event.pk)


@custom_staff_member_required
def preview_certificate_view(request, pk):
    """Prévisualisation en direct de l'attestation de prestige pour un événement"""
    from django.http import HttpResponse
    from main.certificate_utils import generate_preview_certificate
    
    event = get_object_or_404(Event, pk=pk)
    try:
        pdf_buffer = generate_preview_certificate(event)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="apercu_attestation_{event.pk}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors de la prévisualisation de l'attestation : {str(e)}")
        return redirect('admin_event_certificates', pk=pk)


@custom_staff_member_required
def preview_ticket_view(request, pk):
    """Prévisualisation en direct du billet officiel VIP pour un événement"""
    from django.http import HttpResponse
    from main.utils import generate_preview_ticket
    
    event = get_object_or_404(Event, pk=pk)
    try:
        pdf_buffer = generate_preview_ticket(event)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="apercu_billet_{event.pk}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors de la prévisualisation du billet : {str(e)}")
        return redirect('admin_events_list')
