from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from .models import Member, EventRegistration, Contact



class MemberRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription des membres"""
    
    class Meta:
        model = Member
        fields = [
            'nom_prenom', 'matricule', 'date_naissance', 'lieu_naissance', 
            'telephone', 'email', 'niveau', 'photo', 'bio'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
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
                'bio',
                'photo',  # Ajout du champ photo
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
    
    class Meta:
        model = EventRegistration
        fields = ['nom_prenom', 'email', 'telephone', 'promotion', 'message', 'photo']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                _('Inscription à l\'événement'),
                Row(
                    Column('nom_prenom', css_class='form-group col-md-6 mb-3'),
                    Column('promotion', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('email', css_class='form-group col-md-6 mb-3'),
                    Column('telephone', css_class='form-group col-md-6 mb-3'),
                ),
                'photo',  # Champ photo ajouté
                'message',
            ),
            Submit('submit', _('S\'inscrire à l\'événement'), css_class='btn btn-success btn-lg')
        )
        
        # Ajouter des classes CSS
        for field_name, field in self.fields.items():
            if field_name != 'photo':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control'
                })

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

class MentorRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription des parrains"""
    # Use MultipleChoiceField for checkboxes logic, but model has TextField.
    # We'll need to clean the data to join list into string.
    expertise_domains_list = forms.MultipleChoiceField(
        choices=DOMAINS_LIST,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Domaines d'expertise (Cochez tout ce qui s'applique)")
    )
    
    class Meta:
        model = Mentor
        fields = ['first_name', 'last_name', 'phone', 'email', 'level', 'specialty', 'max_mentees']
        # removed expertise_domains from fields, handled manually

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Informations Personnelles'),
                Row(
                    Column('first_name', css_class='form-group col-md-6 mb-3'),
                    Column('last_name', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('email', css_class='form-group col-md-6 mb-3'),
                    Column('phone', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('level', css_class='form-group col-md-6 mb-3'),
                    Column('specialty', css_class='form-group col-md-6 mb-3'),
                ),
                'expertise_domains_list',
                'max_mentees',
            ),
            Submit('submit', _('Devenir Parrain'), css_class='btn btn-primary btn-lg w-100')
        )
        # Styling
        for field_name, field in self.fields.items():
            if field_name != 'expertise_domains_list':
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        domains = cleaned_data.get('expertise_domains_list')
        if domains:
            # Join list into comma-separated string for the model
            self.instance.expertise_domains = ", ".join(domains)
        return cleaned_data

class MenteeRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription des filleuls"""
    competencies_list = forms.MultipleChoiceField(
        choices=COMPETENCIES_LIST,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Compétences techniques actuelles")
    )
    
    professional_domains_list = forms.MultipleChoiceField(
        choices=DOMAINS_LIST,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Domaines professionnels visés (Max 2)")
    )

    class Meta:
        model = Mentee
        fields = ['first_name', 'last_name', 'phone', 'email', 'level', 'desired_specialty']
        # removed text fields, handled manually

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Informations Personnelles'),
                Row(
                    Column('first_name', css_class='form-group col-md-6 mb-3'),
                    Column('last_name', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('email', css_class='form-group col-md-6 mb-3'),
                    Column('phone', css_class='form-group col-md-6 mb-3'),
                ),
                'level',
            ),
            Fieldset(
                _('Projet Professionnel'),
                'desired_specialty',
                'competencies_list',
                'professional_domains_list',
            ),
            Submit('submit', _('Trouver un Parrain'), css_class='btn btn-success btn-lg w-100')
        )
        # Styling
        for field_name, field in self.fields.items():
            if 'list' not in field_name:
                field.widget.attrs.update({'class': 'form-control'})

    def clean_professional_domains_list(self):
        domains = self.cleaned_data.get('professional_domains_list')
        if len(domains) > 2:
            raise forms.ValidationError(_("Vous ne pouvez sélectionner que 2 domaines maximum."))
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
                commission__edition=edition,
                email=email
            ).exists()
            if exists:
                raise forms.ValidationError(
                    "Cette adresse e-mail a déjà soumis une candidature pour cette édition du J.U.IN."
                )
        return cleaned_data


class JUINDonationForm(forms.ModelForm):
    """Formulaire de don / soutien au J.U.IN avec paiement Mobile Money"""

    class Meta:
        model = JUINDonation
        fields = ['nom_prenom', 'email', 'telephone', 'montant', 'type_paiement', 'message', 'is_anonymous']
        widgets = {
            'message': forms.TextInput(attrs={'placeholder': 'Un mot d\'encouragement pour les organisateurs…'}),
            'montant': forms.NumberInput(attrs={'min': 500, 'step': 500, 'placeholder': 'Ex: 5000'}),
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
        if montant and montant < 500:
            raise forms.ValidationError("Le montant minimum est de 500 FCFA.")
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
            'name', 'captain_name', 'captain_phone', 'captain_email',
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
        
        if competition:
            if competition.comp_type == 'sport':
                self.fields['project_title'].label = "Nom du Club / Quartier (Optionnel)"
                self.fields['project_description'].label = "Commentaire additionnel"
                self.fields['project_description'].widget.attrs['placeholder'] = "Infos sur les couleurs de l'équipe, etc."
            elif competition.comp_type == 'computer':
                self.fields['project_title'].required = True
                self.fields['project_description'].required = True

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("L'image ne doit pas dépasser 5 MB.")
        return logo