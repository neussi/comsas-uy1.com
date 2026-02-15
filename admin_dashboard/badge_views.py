from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from io import BytesIO
from main.models import Event, EventRegistration
from main.badge_utils import generate_badge
import zipfile
import os
from django.http import HttpResponse

# Badge Management Views

@staff_member_required
def event_badges_manage(request, pk):
    """Manage badges for an event"""
    event = get_object_or_404(Event, pk=pk)
    
    # Get all confirmed registrations
    registrations = EventRegistration.objects.filter(event=event, is_confirmed=True).order_by('nom_prenom')
    
    # Check if badges are enabled
    if not getattr(event, 'badge_enabled', True):
        messages.warning(request, "Les badges ne sont pas activés pour cet événement.")
    
    # Calculate stats
    total_confirmed = registrations.count()
    badges_generated = registrations.exclude(badge_pdf='').count() if registrations.exists() else 0
    badges_pending = total_confirmed - badges_generated
    
    context = {
        'event': event,
        'registrations': registrations,
        'total_confirmed': total_confirmed,
        'badges_generated': badges_generated,
        'badges_pending': badges_pending,
    }
    
    return render(request, 'admin_dashboard/events/badges.html', context)

@staff_member_required
def generate_all_badges(request, pk):
    """Generate all badges for an event"""
    event = get_object_or_404(Event, pk=pk)
    registrations = EventRegistration.objects.filter(event=event, is_confirmed=True)
    
    count = 0
    errors = 0
    
    for reg in registrations:
        try:
            # Generate badge if not exists or force regenerate? Usually force regenerate
            # But let's check if we want to overwrite. Let's overwrite to ensure config updates.
            generate_badge(reg)
            count += 1
        except Exception as e:
            errors += 1
            print(f"Error generating badge for {reg}: {e}")
            
    if errors > 0:
        messages.warning(request, f"{count} badges générés avec succès, mais {errors} erreurs rencontrées.")
    else:
        messages.success(request, f"{count} badges générés avec succès pour {event.title_fr}.")
        
    return redirect('admin_event_badges', pk=pk)

@staff_member_required
def download_badges_zip(request, pk):
    """Download all generated badges as a ZIP file"""
    event = get_object_or_404(Event, pk=pk)
    registrations = EventRegistration.objects.filter(event=event, is_confirmed=True).exclude(badge_pdf='')
    
    if not registrations.exists():
        messages.error(request, "Aucun badge n'a été généré pour cet événement.")
        return redirect('admin_event_badges', pk=pk)
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for reg in registrations:
            if reg.badge_pdf:
                file_path = reg.badge_pdf.path
                if os.path.exists(file_path):
                    # Use a clean filename in the archive
                    archive_name = f"{reg.nom_prenom.replace(' ', '_')}_badge.pdf"
                    zip_file.write(file_path, archive_name)
    
    # Prepare response
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="badges_{event.pk}_{event.date_event.strftime("%Y%m%d")}.zip"'
    
    return response

@staff_member_required
def regenerate_badge(request, registration_id):
    """Regenerate a single badge"""
    registration = get_object_or_404(EventRegistration, pk=registration_id)
    event_pk = registration.event.pk
    
    try:
        generate_badge(registration)
        messages.success(request, f"Badge régénéré pour {registration.nom_prenom}.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération: {str(e)}")
        
    return redirect('admin_event_badges', pk=event_pk)
