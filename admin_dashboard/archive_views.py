from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from main.models import Archive
from .forms import ArchiveForm

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

@login_required
@user_passes_test(is_admin)
def archive_list(request):
    archives = Archive.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard/archives/list.html', {'archives': archives})

@login_required
@user_passes_test(is_admin)
def archive_create(request):
    if request.method == 'POST':
        form = ArchiveForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Archive ajoutée avec succès.")
            return redirect('admin_archive_list')
    else:
        form = ArchiveForm()
    return render(request, 'admin_dashboard/archives/form.html', {'form': form, 'title': 'Ajouter une archive'})

@login_required
@user_passes_test(is_admin)
def archive_edit(request, pk):
    archive = get_object_or_404(Archive, pk=pk)
    if request.method == 'POST':
        form = ArchiveForm(request.POST, request.FILES, instance=archive)
        if form.is_valid():
            form.save()
            messages.success(request, "Archive modifiée avec succès.")
            return redirect('admin_archive_list')
    else:
        form = ArchiveForm(instance=archive)
    return render(request, 'admin_dashboard/archives/form.html', {'form': form, 'title': 'Modifier l\'archive'})

@login_required
@user_passes_test(is_admin)
def archive_delete(request, pk):
    archive = get_object_or_404(Archive, pk=pk)
    if request.method == 'POST':
        archive.delete()
        messages.success(request, "Archive supprimée.")
        return redirect('admin_archive_list')
    return render(request, 'admin_dashboard/archives/confirm_delete.html', {'object': archive})
