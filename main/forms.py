from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from .models import (
    Member, EventRegistration, EventRegistrationCode, Contact, 
    ProjectSubmission, ClubCommission, ClubCommissionApplication,
    AcademicResource, JobOffer, Candidate, JUINTeam
)
from django.utils import timezone



class MemberRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription des membres"""
    
    class Meta:
        model = Member
        fields = [
            'nom_prenom', 'matricule', 'date_naissance', 'lieu_naissance', 
            'telephone', 'email', 'niveau', 'photo', 'bio', 'skills', 'technologies', 'other_roles', 'needs',
            'github_url', 'linkedin_url', 'twitter_url', 'website_url'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.TextInput(attrs={'placeholder': 'Ex: Leadership, Gestion de projet...'}),
            'technologies': forms.TextInput(attrs={'placeholder': 'Ex: Python, React, PostgreSQL...'}),
            'other_roles': forms.TextInput(attrs={'placeholder': 'Ex: UI/UX Designer, Rédacteur web...'}),
            'needs': forms.TextInput(attrs={'placeholder': 'Ex: Recherche stage, Mentorat technique...'}),
            'github_url': forms.URLInput(attrs={'placeholder': 'https://github.com/votre_profil'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/votre_profil'}),
            'twitter_url': forms.URLInput(attrs={'placeholder': 'https://x.com/votre_profil'}),
            'website_url': forms.URLInput(attrs={'placeholder': 'https://votresite.com'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_enctype = 'multipart/form-data'  # Important pour les fichiers
        self.helper.layout = Layout(
            Fieldset(
                _('Informations personnelles'),
                Row(
                    Column('nom_prenom', css_class='form-group col-md-6 mb-3'),
                    Column('matricule', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('date_naissance', css_class='form-group col-md-6 mb-3'),
                    Column('lieu_naissance', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('telephone', css_class='form-group col-md-6 mb-3'),
                    Column('email', css_class='form-group col-md-6 mb-3'),
                ),
                'niveau',
                'photo',  # Ajout du champ photo
                'bio',
            ),
            Fieldset(
                _('Portfolio & Compétences'),
                'skills',
                'technologies',
                'other_roles',
                'needs',
            ),
            Fieldset(
                _('Réseaux Sociaux et Web'),
                'github_url',
                'linkedin_url',
                'twitter_url',
                'website_url',
            ),
            HTML('''
                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="terms" required>
                    <label class="form-check-label" for="terms">
                        {% trans "J'accepte les statuts et le règlement intérieur de l'association" %}
                    </label>
                </div>
            '''),
            Submit('submit', _('Envoyer ma demande d\'adhésion'), css_class='btn btn-primary btn-lg')
        )
        
        # Ajouter des classes CSS personnalisées
        for field_name, field in self.fields.items():
            if field_name != 'photo':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control',
                })
        
        self.fields['photo'].required = True
    
    def clean_photo(self):
        """Validation de la photo"""
        photo = self.cleaned_data.get('photo')
        if photo:
            # Vérifier la taille du fichier (max 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("La taille de l'image ne doit pas dépasser 5 MB."))
            
            # Vérifier le type de fichier
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError(_("Le fichier doit être une image."))
        
        return photo

class EventRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription aux événements"""
    registration_code = forms.CharField(
        max_length=10,
        required=False,
        label=_("Code d'inscription (remis en présentiel)"),
        help_text=_("Code unique à 6 caractères qui vous a été remis physiquement."),
        widget=forms.TextInput(attrs={
            'class': 'form-control font-monospace text-uppercase fw-bold',
            'placeholder': 'Ex: A9X2B4',
            'maxlength': '10',
            'autocomplete': 'off',
            'style': 'letter-spacing: 3px; text-transform: uppercase;'
        })
    )

    class Meta:
        model = EventRegistration
        fields = ['nom_prenom', 'email', 'telephone', 'promotion', 'message', 'photo']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    
    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_enctype = 'multipart/form-data'
        
        requires_code = bool(self.event and getattr(self.event, 'requires_registration_code', False))
        self.fields['registration_code'].required = requires_code

        # Éléments du formulaire
        fieldset_elements = [
            Row(
                Column('nom_prenom', css_class='form-group col-md-6 mb-3'),
                Column('promotion', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('telephone', css_class='form-group col-md-6 mb-3'),
            ),
        ]

        if requires_code:
            fieldset_elements.append(
                Row(
                    Column('registration_code', css_class='form-group col-md-12 mb-3'),
                )
            )
        else:
            self.fields['registration_code'].widget = forms.HiddenInput()

        fieldset_elements.extend(['photo', 'message'])

        self.helper.layout = Layout(
            Fieldset(
                _('Inscription à l\'événement'),
                *fieldset_elements
            ),
            Submit('submit', _('S\'inscrire à l\'événement'), css_class='btn btn-success btn-lg')
        )
        
        # Ajouter des classes CSS
        for field_name, field in self.fields.items():
            if field_name not in ['photo', 'registration_code']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })
            elif field_name == 'photo':
                field.widget.attrs.update({
                    'class': 'form-control'
                })
                
        self.fields['photo'].required = True

    def clean_registration_code(self):
        code = self.cleaned_data.get('registration_code', '').strip().upper()
        if self.event and getattr(self.event, 'requires_registration_code', False):
            if not code:
                raise forms.ValidationError(_("Le code d'inscription remis en présentiel est obligatoire pour cet événement."))
            code_obj = EventRegistrationCode.objects.filter(event=self.event, code__iexact=code).first()
            if not code_obj:
                raise forms.ValidationError(_("Ce code d'inscription n'est pas valide pour cet événement. Veuillez vérifier la saisie."))
            if code_obj.is_used:
                input_email = (self.data.get('email') or '').strip().lower()
                # Si le code a déjà été utilisé par cette même personne (cas d'un double-clic ou rechargement)
                if (code_obj.used_by and code_obj.used_by.email.strip().lower() == input_email) or \
                   (EventRegistration.objects.filter(event=self.event, email__iexact=input_email, registration_code_entered__iexact=code).exists()):
                    self.cleaned_code_obj = code_obj
                    self.is_duplicate_submission = True
                    return code
                raise forms.ValidationError(_("Ce code d'inscription a déjà été utilisé. Chaque code est à usage unique et n'est plus valable."))
            self.cleaned_code_obj = code_obj
        return code

    def clean_photo(self):
        """Validation de la photo"""
        photo = self.cleaned_data.get('photo')
        if photo:
            # Vérifier la taille du fichier (max 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("La taille de l'image ne doit pas dépasser 5 MB."))
            
            # Vérifier le type de fichier
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError(_("Le fichier doit être une image."))
        
        return photo

class ContactForm(forms.ModelForm):
    """Formulaire de contact"""
    
    class Meta:
        model = Contact
        fields = ['nom_prenom', 'email', 'telephone', 'sujet', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Contactez-nous'),
                Row(
                    Column('nom_prenom', css_class='form-group col-md-6 mb-3'),
                    Column('email', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('telephone', css_class='form-group col-md-6 mb-3'),
                    Column('sujet', css_class='form-group col-md-6 mb-3'),
                ),
                'message',
            ),
            Submit('submit', _('Envoyer le message'), css_class='btn btn-primary btn-lg')
        )
        
        # Ajouter des classes CSS
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

class NewsletterForm(forms.Form):
    """Formulaire d'inscription à la newsletter"""
    email = forms.EmailField(
        label=_('Adresse e-mail'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre adresse e-mail')
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'newsletter-form'
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='col-md-8'),
                Column(
                    Submit('submit', _('S\'abonner'), css_class='btn btn-primary'),
                    css_class='col-md-4'
                ),
            )
        )

# ------------- SPONSORSHIP FORMS -------------
from .models import Mentor, Mentee, SponsorshipSession, COMPETENCIES_LIST, DOMAINS_LIST
from PIL import Image

def validate_portrait_photo(photo):
    """Validation stricte du format et du poids de la photo portrait"""
    if not photo:
        raise forms.ValidationError(_("La photo portrait officielle est obligatoire."))
    
    # Validation du poids (Max 5 Mo)
    max_size = 5 * 1024 * 1024
    if photo.size > max_size:
        raise forms.ValidationError(_("Le fichier photo est trop lourd (%(size).1f Mo). La taille maximale autorisée est de 5 Mo.") % {
            'size': photo.size / (1024 * 1024)
        })

    # Validation du format (JPEG, PNG, WEBP)
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    content_type = getattr(photo, 'content_type', '')
    if content_type and content_type not in allowed_types:
        raise forms.ValidationError(_("Format non pris en charge. Veuillez télécharger une image au format JPG, PNG ou WEBP."))

    try:
        img = Image.open(photo)
        img.verify()
    except Exception:
        raise forms.ValidationError(_("Fichier image corrompu ou invalide. Veuillez sélectionner une photo valide."))

    return photo


class MentorRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription des parrains professionnels et académiques"""
    photo = forms.ImageField(
        required=True,
        label=_("Photo Portrait Officielle *"),
        help_text=_("Photo nette et professionnelle (JPEG, PNG, WEBP, max 5 Mo). Un outil de recadrage est à votre disposition ci-dessous."),
        validators=[validate_portrait_photo]
    )
    profession = forms.CharField(
        max_length=150,
        required=True,
        label=_("Profession / Poste actuel *"),
        widget=forms.TextInput(attrs={'placeholder': _('Ex: Ingénieur DevOps, Data Scientist, Tech Lead...')})
    )
    company = forms.CharField(
        max_length=150,
        required=False,
        label=_("Entreprise / Organisation"),
        widget=forms.TextInput(attrs={'placeholder': _('Ex: Google, MTN, Orange, Startup, Freelance...')})
    )
    years_of_experience = forms.IntegerField(
        min_value=0,
        max_value=60,
        initial=1,
        required=True,
        label=_("Années d'expérience *"),
        widget=forms.NumberInput(attrs={'min': 0, 'max': 60})
    )
    bio = forms.CharField(
        required=False,
        label=_("Présentation / Biographie succincte"),
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': _('Présentez votre parcours, vos réalisations et ce que vous souhaitez apporter à vos filleuls...')})
    )
    expertise_domains_list = forms.MultipleChoiceField(
        choices=DOMAINS_LIST,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Domaines d'expertise & Compétences clés * (Cochez tout ce qui s'applique)")
    )
    
    class Meta:
        model = Mentor
        fields = ['first_name', 'last_name', 'phone', 'email', 'level', 'specialty', 'profession', 'company', 'years_of_experience', 'bio', 'photo', 'max_mentees']

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        return validate_portrait_photo(photo)
    
    def clean(self):
        cleaned_data = super().clean()
        domains = cleaned_data.get('expertise_domains_list')
        if domains:
            self.instance.expertise_domains = ", ".join(domains)
        return cleaned_data


class MenteeRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription des filleuls"""
    photo = forms.ImageField(
        required=True,
        label=_("Photo Portrait Officielle *"),
        help_text=_("Photo nette (JPEG, PNG, WEBP, max 5 Mo). Un outil de recadrage est à votre disposition ci-dessous."),
        validators=[validate_portrait_photo]
    )
    desired_specialty = forms.CharField(
        max_length=100,
        required=True,
        label=_("Spécialité visée *"),
        widget=forms.TextInput(attrs={'placeholder': _('Ex: Génie Logiciel, Data Science, Cybersécurité, Systèmes & Cloud...')})
    )
    skills_to_acquire = forms.CharField(
        required=True,
        label=_("Compétences que vous souhaitez acquérir *"),
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': _('Listez les technologies, outils ou compétences précises que vous souhaitez développer avec votre parrain (ex: Docker, Architecture Microservices, Machine Learning...)...')})
    )
    competencies_list = forms.MultipleChoiceField(
        choices=COMPETENCIES_LIST,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Compétences techniques actuelles *")
    )
    professional_domains_list = forms.MultipleChoiceField(
        choices=DOMAINS_LIST,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Domaines professionnels visés * (Max 2)")
    )
    bio = forms.CharField(
        required=False,
        label=_("Motivations / Présentation"),
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': _('Expliquez brièvement vos attentes vis-à-vis du parrainage...')})
    )

    class Meta:
        model = Mentee
        fields = ['first_name', 'last_name', 'phone', 'email', 'level', 'desired_specialty', 'skills_to_acquire', 'bio', 'photo']

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        return validate_portrait_photo(photo)

    def clean_professional_domains_list(self):
        domains = self.cleaned_data.get('professional_domains_list')
        if domains and len(domains) > 2:
            raise forms.ValidationError(_("Vous ne pouvez sélectionner que 2 domaines professionnels maximum."))
        return domains

    def clean(self):
        cleaned_data = super().clean()
        competencies = cleaned_data.get('competencies_list')
        domains = cleaned_data.get('professional_domains_list')
        
        if competencies:
            self.instance.competencies = ", ".join(competencies)
        if domains:
            self.instance.professional_domains = ", ".join(domains)
        
        return cleaned_data


# =============================================================================
# EVENT ACTIVITY FORMS
# =============================================================================
from .models import EventActivity, EventActivityApplication

class EventActivityApplicationForm(forms.ModelForm):
    """Formulaire d'inscription à une activité d'événement (Individuel, Équipe ou Gaming)"""
    
    class Meta:
        model = EventActivityApplication
        fields = [
            'full_name', 'email', 'phone', 'level', 'notes',
            'team_name', 'captain_name', 'team_members', 'team_size',
            'gamer_tag', 'game_name', 'gaming_platform', 'gaming_id'
        ]

    def __init__(self, *args, **kwargs):
        self.activity = kwargs.pop('activity', None)
        super().__init__(*args, **kwargs)
        
        # Champs optionnels par défaut (rendus obligatoires conditionnellement dans clean())
        optional_conditional_fields = [
            'team_name', 'captain_name', 'team_members', 'team_size',
            'gamer_tag', 'game_name', 'gaming_platform', 'gaming_id',
            'level', 'notes'
        ]
        for f in optional_conditional_fields:
            if f in self.fields:
                self.fields[f].required = False

        if self.activity and self.activity.activity_type != 'team':
            self.fields['team_size'].initial = 1

        # Styles par défaut
        for fname, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        if not self.activity:
            return cleaned_data

        activity_type = self.activity.activity_type
        
        # Validation spécifique aux équipes
        if activity_type == 'team':
            team_name = cleaned_data.get('team_name')
            captain_name = cleaned_data.get('captain_name')
            team_members = cleaned_data.get('team_members')
            team_size = cleaned_data.get('team_size') or 1
            
            if not team_name:
                self.add_error('team_name', _("Le nom de l'équipe est obligatoire."))
            if not captain_name:
                self.add_error('captain_name', _("Le nom du capitaine est obligatoire."))
            if not team_members:
                self.add_error('team_members', _("La composition des membres de l'équipe est obligatoire."))
                
            min_size = self.activity.min_team_size
            max_size = self.activity.max_team_size
            if team_size < min_size or team_size > max_size:
                self.add_error('team_size', _("La taille de l'équipe doit être comprise entre %(min)s et %(max)s membres.") % {
                    'min': min_size, 'max': max_size
                })

        # Validation spécifique au Gaming
        elif activity_type == 'gaming':
            gamer_tag = cleaned_data.get('gamer_tag')
            gaming_platform = cleaned_data.get('gaming_platform')
            if not gamer_tag:
                self.add_error('gamer_tag', _("Votre pseudo GamerTag est obligatoire."))
            if not gaming_platform:
                self.add_error('gaming_platform', _("La plateforme de jeu est obligatoire."))

        return cleaned_data


# =============================================================================
# J.U.IN 2026 FORMS
# =============================================================================
from .models import JUINCommissionApplication, JUINDonation, JUINCommission

class JUINCommissionApplicationForm(forms.ModelForm):
    """Formulaire de candidature à une commission J.U.IN"""

    class Meta:
        model = JUINCommissionApplication
        fields = ['nom_prenom', 'email', 'telephone', 'etablissement', 'niveau', 'photo', 'motivation', 'commission']
        widgets = {
            'motivation': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Expliquez pourquoi vous souhaitez rejoindre cette commission...'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, edition=None, **kwargs):
        super().__init__(*args, **kwargs)
        if edition:
            self.fields['commission'].queryset = JUINCommission.objects.filter(edition=edition).order_by('order', 'name')
        self.fields['commission'].empty_label = "-- Sélectionnez une commission --"

        for field_name, field in self.fields.items():
            if field_name not in ('photo', 'commission'):
                field.widget.attrs.update({'class': 'form-control'})
            elif field_name == 'commission':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
                
        self.fields['photo'].required = True

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La taille de la photo ne doit pas dépasser 5 MB.")
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError("Le fichier doit être une image.")
        return photo

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        commission = cleaned_data.get('commission')
        if email and commission:
            # Check one application per person per edition
            edition = commission.edition
            exists = JUINCommissionApplication.objects.filter(
                commission=commission,
                email=email
            ).exists()
            if exists:
                raise forms.ValidationError(
                    f"Cette adresse e-mail a déjà soumis une candidature pour la commission '{commission.name}'."
                )
        return cleaned_data


class JUINDonationForm(forms.ModelForm):
    """Formulaire de don / soutien au J.U.IN avec paiement Mobile Money"""

    class Meta:
        model = JUINDonation
        fields = ['nom_prenom', 'email', 'telephone', 'montant', 'type_paiement', 'message', 'is_anonymous']
        widgets = {
            'message': forms.TextInput(attrs={'placeholder': 'Un mot d\'encouragement pour les organisateurs…'}),
            'montant': forms.NumberInput(attrs={'min': 100, 'step': 100, 'placeholder': 'Ex: 5000'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Ex: 6XXXXXXXX (sans le +237)'}),
        }
        labels = {
            'telephone': 'Numéro Mobile Money (MTN/Orange)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ('is_anonymous', 'type_paiement'):
                field.widget.attrs.update({'class': 'form-control'})
            elif field_name == 'type_paiement':
                field.widget.attrs.update({'class': 'form-select'})

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant and montant < 100:
            raise forms.ValidationError("Le montant minimum est de 100 FCFA.")
        return montant

    def clean_telephone(self):
        type_p = self.data.get('type_paiement', '')
        telephone = self.cleaned_data.get('telephone', '').strip()
        if type_p in ('mtn', 'orange') and not telephone:
            raise forms.ValidationError("Le numéro Mobile Money est requis pour ce mode de paiement.")
        return telephone


# =============================================================================
# J.U.IN 2026 — SPONSOR / PARTENAIRE FORM
# =============================================================================
from .models import JUINSponsor


class JUINSponsorRequestForm(forms.ModelForm):
    """Formulaire de demande de partenariat / sponsoring J.U.IN"""

    class Meta:
        model = JUINSponsor
        fields = [
            'company_name', 'logo', 'website', 'tier',
            'contact_name', 'contact_email', 'contact_phone',
            'description', 'contribution',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Décrivez votre entreprise / institution…'}),
            'contribution': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex: Financement de 500 000 FCFA, mise à disposition de matériel, formation, lot…'}),
            'logo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ('logo', 'tier'):
                field.widget.attrs.update({'class': 'form-control'})
            elif field_name == 'tier':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
                
        # Logo optionnel — l'admin peut l'ajouter via le dashboard
        self.fields['logo'].required = False

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Le logo ne doit pas dépasser 5 MB.")
            if not logo.content_type.startswith('image/'):
                raise forms.ValidationError("Le fichier doit être une image.")
        return logo


from .models import JUINCompetition, JUINTeam

class JUINTeamRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription d'une équipe à une compétition J.U.IN"""

    class Meta:
        model = JUINTeam
        fields = [
            'name', 'school', 'captain_name', 'captain_phone', 'captain_email',
            'members_count', 'members_list', 'project_title', 'project_description', 'logo'
        ]
        widgets = {
            'members_list': forms.Textarea(attrs={'rows': 4, 'placeholder': '1. Nom Prénom\n2. Nom Prénom...'}),
            'project_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Détails du projet ou composition détaillée...'}),
            'logo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, competition=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'logo':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
                
        self.fields['logo'].required = True

        if competition:
            name_lower = competition.name.lower()
            if competition.comp_type == 'sport':
                self.fields['project_title'].label = "Nom du Club / Quartier (Optionnel)"
                self.fields['project_description'].label = "Commentaire additionnel"
                self.fields['project_description'].widget.attrs['placeholder'] = "Infos sur les couleurs de l'équipe, etc."
                self.fields['project_title'].required = False
                self.fields['project_description'].required = False
            elif competition.comp_type == 'hackathon':
                self.fields['project_title'].label = "Titre du projet (Sujet imposé)"
                self.fields['project_title'].widget.attrs['placeholder'] = "Sera attribué par les organisateurs"
                self.fields['project_title'].required = False
                self.fields['project_description'].label = "Description équipe / Compétences"
                self.fields['project_description'].widget.attrs['placeholder'] = "Décrivez les forces de votre équipe..."
            elif competition.comp_type == 'pitch':
                self.fields['project_title'].label = "Titre de votre Projet / Innovation"
                self.fields['project_title'].required = True
                self.fields['project_description'].label = "Description détaillée du Projet"
                self.fields['project_description'].required = True
            elif competition.comp_type == 'gaming' or competition.comp_type == 'computer':
                self.fields['project_title'].required = False
                self.fields['project_description'].required = False
            else:
                self.fields['project_title'].required = False
                self.fields['project_description'].required = False
        else:
            self.fields['project_title'].required = False
            self.fields['project_description'].required = False

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("L'image ne doit pas dépasser 5 MB.")
        return logo
# =============================================================================
# NEW FEATURES: PROJECTS & COMMISSIONS
# =============================================================================

class ProjectSubmissionForm(forms.ModelForm):
    """Formulaire de soumission de projet par un visiteur"""
    class Meta:
        model = ProjectSubmission
        fields = [
            'project_name', 'description', 'domain', 'presentation_time', 
            'status', 'additional_info', 'submitter_name', 'submitter_email', 'submitter_tel', 'logo'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Décrivez votre projet...'}),
            'additional_info': forms.Textarea(attrs={'rows': 3}),
            'logo': forms.FileInput(attrs={'accept': 'image/*'}),
            'presentation_time': forms.TextInput(attrs={'placeholder': 'Ex: Jeudi à 14h, ou 2024-05-10...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'logo':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['logo'].required = True

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Le logo ne doit pas dépasser 5 MB.")
            if not logo.content_type.startswith('image/'):
                raise forms.ValidationError("Le fichier doit être une image.")
        return logo

class ClubCommissionApplicationForm(forms.ModelForm):
    """Formulaire de candidature à une direction du Club"""
    class Meta:
        model = ClubCommissionApplication
        fields = [
            'commission', 'nom_prenom', 'email', 'telephone', 
            'niveau', 'photo', 'motivation', 'role_applied'
        ]
        widgets = {
            'motivation': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Pourquoi souhaitez-vous rejoindre cette direction ?'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commission'].empty_label = "Sélectionnez une commission"
        self.fields['photo'].required = True
        for field_name, field in self.fields.items():
            if field_name not in ('photo', 'commission'):
                field.widget.attrs.update({'class': 'form-control'})
            elif field_name == 'commission':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class AcademicResourceForm(forms.ModelForm):
    class Meta:
        model = AcademicResource
        fields = ['title', 'resource_type', 'niveau', 'subject', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Informations additionnelles (optionnel)'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = ['title', 'company', 'location', 'offer_type', 'apply_link', 'deadline', 'description', 'requirements']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CandidateRegistrationForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'candidate_type', 'age', 'level', 'school', 'phone', 'description', 'image', 'video_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Décrivez votre parcours et vos motivations...'}),
            'candidate_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

from .models import JUINCandidate

class JUINCandidateRegistrationForm(forms.ModelForm):
    class Meta:
        model = JUINCandidate
        fields = ['name', 'candidate_type', 'age', 'level', 'school', 'phone', 'email', 'description', 'image', 'video_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Décrivez votre parcours et vos motivations...'}),
            'candidate_type': forms.Select(attrs={'class': 'form-select'}),
            'school': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ('candidate_type', 'school'):
                field.widget.attrs.update({'class': 'form-control'})

