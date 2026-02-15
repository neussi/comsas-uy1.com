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