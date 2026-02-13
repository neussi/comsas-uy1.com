from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from io import BytesIO
from main.models import Event, EventRegistration

# Certificate Management Views

@staff_member_required
def event_certificates_manage(request, pk):
    """Manage certificates for an event"""
    event = get_object_or_404(Event, pk=pk)
    registrations = EventRegistration.objects.filter(event=event, is_confirmed=True)
    
    context = {
        'event': event,
        'registrations': registrations,
        'total_participants': registrations.count(),
        'certificates_generated': registrations.exclude(certificate_pdf='').count(),
    }
    
    return render(request, 'admin_dashboard/events/certificates.html', context)


@staff_member_required
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


@staff_member_required
def download_certificates_zip(request, pk):
    """Download all certificates as a ZIP file"""
    import zipfile
    from django.http import HttpResponse
    
    event = get_object_or_404(Event, pk=pk)
    registrations = EventRegistration.objects.filter(
        event=event, 
        is_confirmed=True
    ).exclude(certificate_pdf='')
    
    if not registrations.exists():
        messages.error(request, "Aucune attestation n'a été générée pour cet événement.")
        return redirect('admin_event_certificates', pk=pk)
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for registration in registrations:
            if registration.certificate_pdf:
                # Get the file path
                file_path = registration.certificate_pdf.path
                # Create a clean filename
                filename = f"attestation_{registration.nom_prenom.replace(' ', '_')}_{registration.uuid}.pdf"
                # Add to ZIP
                zip_file.write(file_path, filename)
    
    # Prepare response
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="attestations_{event.title_fr.replace(" ", "_")}.zip"'
    
    return response


@staff_member_required
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
