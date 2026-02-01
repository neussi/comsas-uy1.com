# admin_dashboard/auth_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django import forms
from main.models import Member

class AdminLoginForm(AuthenticationForm):
    """Formulaire de connexion admin personnalisé"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur',
            'autocomplete': 'username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe',
            'autocomplete': 'current-password'
        })
    
    def confirm_login_allowed(self, user):
        """Vérifier que l'utilisateur peut se connecter au dashboard admin"""
        if not user.is_active:
            raise forms.ValidationError(
                "Ce compte est inactif.",
                code='inactive'
            )
        
        if not (user.is_staff or user.is_superuser):
            raise forms.ValidationError(
                "Vous n'avez pas les permissions nécessaires pour accéder au dashboard admin.",
                code='no_permission'
            )

class AdminRegistrationForm(forms.Form):
    """Formulaire de demande d'accès admin"""
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre prénom'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur souhaité'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@example.com'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })
    )
    
    requested_role = forms.ChoiceField(
        choices=[
            ('', 'Sélectionnez un rôle'),
            ('bureau', 'Membre du Bureau'),
            ('moderator', 'Modérateur'),
            ('editor', 'Éditeur de contenu'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    justification = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Expliquez pourquoi vous avez besoin d\'un accès administrateur...'
        })
    )
    
    current_position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Secrétaire général, Trésorier...'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Vérifier que l'email correspond à un membre
        try:
            member = Member.objects.get(email=email, is_active=True)
        except Member.DoesNotExist:
            raise forms.ValidationError(
                "Cet email ne correspond à aucun membre actif de l'association."
            )
        
        # Vérifier qu'il n'y a pas déjà un compte admin avec cet email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Un compte administrateur existe déjà avec cet email."
            )
        
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Ce nom d'utilisateur est déjà pris."
            )
        
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        return cleaned_data

class AdminPasswordResetForm(PasswordResetForm):
    """Formulaire de réinitialisation de mot de passe admin"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'votre.email@example.com'
        })

def admin_login_view(request):
    """Vue de connexion admin"""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard_home')
    
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None and (user.is_staff or user.is_superuser):
                login(request, user)
                messages.success(request, f'Bienvenue {user.get_full_name() or user.username} !')
                
                # Redirection vers la page demandée ou dashboard
                next_page = request.GET.get('next', 'admin_dashboard_home')
                return redirect(next_page)
            else:
                messages.error(request, 'Identifiants incorrects ou permissions insuffisantes.')
    else:
        form = AdminLoginForm()
    
    return render(request, 'admin_dashboard/auth/login.html', {'form': form})

def admin_logout_view(request):
    """Vue de déconnexion admin"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('admin_login')

def admin_register_view(request):
    """Vue de demande d'accès admin"""
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            # Sauvegarder la demande (vous pouvez créer un modèle AdminRequest)
            # Pour l'instant, on envoie juste un email aux administrateurs
            
            data = form.cleaned_data
            
            # Email aux administrateurs
            subject = 'Nouvelle demande d\'accès administrateur - A²ELBM2'
            message = render_to_string('admin_dashboard/emails/admin_request.html', {
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'username': data['username'],
                'email': data['email'],
                'requested_role': data['requested_role'],
                'justification': data['justification'],
                'current_position': data['current_position'],
            })
            
            # Récupérer les emails des super-utilisateurs
            admin_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
            
            if admin_emails:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails,
                    fail_silently=False,
                )
            
            # Email de confirmation au demandeur
            send_mail(
                'Demande d\'accès reçue - A²ELBM2',
                f'Bonjour {data["first_name"]},\n\nNous avons bien reçu votre demande d\'accès administrateur. Elle sera examinée dans les plus brefs délais.\n\nCordialement,\nL\'équipe A²ELBM2',
                settings.DEFAULT_FROM_EMAIL,
                [data['email']],
                fail_silently=False,
            )
            
            messages.success(
                request, 
                'Votre demande a été envoyée avec succès ! Vous recevrez une réponse par email dans les 48h.'
            )
            return redirect('admin_login')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'admin_dashboard/auth/register.html', {'form': form})

def admin_password_reset_view(request):
    """Vue de réinitialisation de mot de passe admin"""
    if request.method == 'POST':
        form = AdminPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Vérifier que l'email appartient à un administrateur
            try:
                user = User.objects.get(email=email, is_staff=True)
                
                # Générer le token de réinitialisation
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Envoyer l'email de réinitialisation
                subject = 'Réinitialisation de votre mot de passe administrateur - A²ELBM2'
                message = render_to_string('admin_dashboard/emails/password_reset.html', {
                    'user': user,
                    'uid': uid,
                    'token': token,
                    'domain': request.get_host(),
                    'protocol': 'https' if request.is_secure() else 'http',
                })
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(
                    request, 
                    'Un email de réinitialisation a été envoyé à votre adresse.'
                )
                return redirect('admin_login')
                
            except User.DoesNotExist:
                messages.error(
                    request, 
                    'Aucun compte administrateur trouvé avec cette adresse email.'
                )
    else:
        form = AdminPasswordResetForm()
    
    return render(request, 'admin_dashboard/auth/password_reset.html', {'form': form})