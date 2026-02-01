
# admin_dashboard/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def admin_required(view_func):
    """
    Décorateur pour vérifier que l'utilisateur est un administrateur
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Vous devez vous connecter pour accéder à cette page.')
            return redirect(f"{reverse('admin_login')}?next={request.path}")
        
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Vous n\'avez pas les permissions nécessaires pour accéder à cette page.')
            return redirect('admin_login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper