from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from main.models import Project, Event, News, Gallery, SiteSettings, Member, SponsorshipSession, Contest, Candidate

class MemberForm(forms.ModelForm):
    """Formulaire pour les membres"""
    
    class Meta:
        model = Member
        fields = [
            'nom_prenom', 'date_naissance', 'lieu_naissance', 'niveau',
            'telephone', 'email', 'profession', 'adresse', 'member_type',
            'poste_bureau', 'photo', 'bio', 'is_active'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Informations personnelles'),
                Row(
                    Column('nom_prenom', css_class='form-group col-md-6 mb-3'),
                    Column('email', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('date_naissance', css_class='form-group col-md-6 mb-3'),
                    Column('lieu_naissance', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('niveau', css_class='form-group col-md-6 mb-3'),
                    Column('telephone', css_class='form-group col-md-6 mb-3'),
                ),
                'profession',
                'adresse',
            ),
            Fieldset(
                _('Statut et rôle'),
                Row(
                    Column('member_type', css_class='form-group col-md-6 mb-3'),
                    Column('is_active', css_class='form-group col-md-6 mb-3'),
                ),
                'poste_bureau',
            ),
            Fieldset(
                _('Photo et biographie'),
                'photo',
                'bio',
            ),
            Submit('submit', _('Enregistrer'), css_class='btn btn-primary')
        )

class ProjectForm(forms.ModelForm):
    """Formulaire pour les projets"""
        
    class Meta:
        model = Project
        fields = [
            'title_fr', 'title_en', 'description_fr', 'description_en',
            'image', 'status', 'budget_required', 'budget_collected',
            'start_date', 'end_date', 'is_featured'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'budget_required': forms.NumberInput(attrs={'step': '0.01'}),
            'budget_collected': forms.NumberInput(attrs={'step': '0.01'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Informations du projet'),
                Row(
                    Column('title_fr', css_class='form-group col-md-6 mb-3'),
                    Column('title_en', css_class='form-group col-md-6 mb-3'),
                ),
                'description_fr',
                'description_en',
                'image',
                Row(
                    Column('status', css_class='form-group col-md-4 mb-3'),
                    Column('is_featured', css_class='form-group col-md-4 mb-3'),
                    Column('', css_class='form-group col-md-4 mb-3'),
                ),
            ),
            Fieldset(
                _('Budget et dates'),
                Row(
                    Column('budget_required', css_class='form-group col-md-6 mb-3'),
                    Column('budget_collected', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('start_date', css_class='form-group col-md-6 mb-3'),
                    Column('end_date', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            Submit('submit', _('Enregistrer'), css_class='btn btn-primary')
        )

class EventForm(forms.ModelForm):
    """Formulaire pour les événements"""
        
    class Meta:
        model = Event
        fields = [
            'title_fr', 'title_en', 'description_fr', 'description_en',
            'image', 'date_event', 'location', 'max_participants',
            'registration_deadline', 'is_featured', 'is_active'
        ]
        widgets = {
            'date_event': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class NewsForm(forms.ModelForm):
    """Formulaire pour les actualités"""
    
    class Meta:
        model = News
        fields = [
            'title_fr', 'title_en', 'content_fr', 'content_en',
            'image', 'author', 'publication_date', 'is_published', 'is_featured'
        ]
        widgets = {
            'publication_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class GalleryForm(forms.ModelForm):
    """Formulaire pour la galerie"""
    
    class Meta:
        model = Gallery
        fields = [
            'title_fr', 'title_en', 'description_fr', 'description_en',
            'media_type', 'image', 'video_url', 'video_file', 'is_featured'
        ]

class SiteSettingsForm(forms.ModelForm):
    """Formulaire pour les paramètres du site"""
    
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'slogan_fr', 'slogan_en', 'description_fr', 'description_en',
            'president_message_fr', 'president_message_en', 'logo', 'hero_image',
            'facebook_url', 'whatsapp_group_url', 'linkedin_url'
        ]

class SponsorshipSessionForm(forms.ModelForm):
    """Formulaire pour les sessions de parrainage"""
    class Meta:
        model = SponsorshipSession
        fields = ['name', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Détails de la session'),
                'name',
                Row(
                    Column('start_date', css_class='form-group col-md-6 mb-3'),
                    Column('end_date', css_class='form-group col-md-6 mb-3'),
                ),
                'is_active',
            ),
            Submit('submit', _('Enregistrer la session'), css_class='btn btn-primary btn-lg w-100')
        )
        # Styling
        for field in self.fields.values():
            if field.widget.input_type != 'checkbox':
                field.widget.attrs.update({'class': 'form-control'})

class ContestForm(forms.ModelForm):
    """Formulaire pour les concours"""
    class Meta:
        model = Contest
        fields = ['title', 'slug', 'description', 'image', 'start_date', 'end_date', 'is_active', 'allow_public_candidates']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Informations du concours'),
                'title',
                'slug',
                'description',
                'image',
                Row(
                    Column('start_date', css_class='form-group col-md-6 mb-3'),
                    Column('end_date', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('is_active', css_class='form-group col-md-6 mb-3'),
                    Column('allow_public_candidates', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            Submit('submit', _('Enregistrer le concours'), css_class='btn btn-primary btn-lg w-100')
        )

class CandidateForm(forms.ModelForm):
    """Formulaire pour les candidats"""
    class Meta:
        model = Candidate
        fields = ['contest', 'name', 'description', 'image', 'video_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Détails du candidat'),
                'contest',
                'name',
                'description',
                'image',
                'video_url',
                'status',
            ),
            Submit('submit', _('Enregistrer le candidat'), css_class='btn btn-primary btn-lg w-100')
        )

from main.models import RequestDocument, Professor, Classroom, Delegate, BlogArticle

class RequestDocumentForm(forms.ModelForm):
    """Formulaire pour les modèles de demandes"""
    class Meta:
        model = RequestDocument
        fields = ['title', 'doc_type', 'description', 'file', 'image_preview']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Informations du document'),
                'title',
                Row(
                    Column('doc_type', css_class='form-group col-md-6 mb-3'),
                    Column('file', css_class='form-group col-md-6 mb-3'),
                ),
                'description',
                'image_preview',
            ),
            Submit('submit', _('Enregistrer le document'), css_class='btn btn-primary btn-lg w-100')
        )

class ProfessorForm(forms.ModelForm):
    """Formulaire pour les enseignants"""
    class Meta:
        model = Professor
        fields = ['name', 'grade', 'specialty', 'office_description', 'office_photo', 'profile_photo', 'is_active', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Identité'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-3'),
                    Column('email', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('grade', css_class='form-group col-md-6 mb-3'),
                    Column('specialty', css_class='form-group col-md-6 mb-3'),
                ),
                'profile_photo',
            ),
            Fieldset(
                _('Bureau'),
                'office_description',
                'office_photo',
            ),
            Fieldset(
                _('Statut'),
                'is_active',
            ),
            Submit('submit', _('Enregistrer l\'enseignant'), css_class='btn btn-primary btn-lg w-100')
        )

class ClassroomForm(forms.ModelForm):
    """Formulaire pour les salles"""
    class Meta:
        model = Classroom
        fields = ['name', 'capacity', 'location_description', 'is_lab', 'photo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Détails de la salle'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-3'),
                    Column('capacity', css_class='form-group col-md-6 mb-3'),
                ),
                'is_lab',
                'photo',
            ),
            Fieldset(
                _('Localisation'),
                'location_description',
            ),
            Submit('submit', _('Enregistrer la salle'), css_class='btn btn-primary btn-lg w-100')
        )

class DelegateForm(forms.ModelForm):
    """Formulaire pour les délégués"""
    class Meta:
        model = Delegate
        fields = ['name', 'level', 'year', 'phone', 'email', 'motto', 'photo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Identité'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-3'),
                    Column('email', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('phone', css_class='form-group col-md-6 mb-3'),
                    Column('photo', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            Fieldset(
                _('Mandat'),
                Row(
                    Column('level', css_class='form-group col-md-4 mb-3'),
                    Column('year', css_class='form-group col-md-4 mb-3'),
                    Column('motto', css_class='form-group col-md-4 mb-3'),
                ),
            ),
            Submit('submit', _('Enregistrer le délégué'), css_class='btn btn-primary btn-lg w-100')
        )

class BlogArticleForm(forms.ModelForm):
    """Formulaire pour les articles de blog"""
    class Meta:
        model = BlogArticle
        fields = ['title', 'slug', 'category', 'image', 'content', 'author', 'is_published', 'published_at']
        widgets = {
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _('Contenu'),
                'title',
                'slug',
                Row(
                    Column('category', css_class='form-group col-md-6 mb-3'),
                    Column('image', css_class='form-group col-md-6 mb-3'),
                ),
                'content',
            ),
            Fieldset(
                _('Publication'),
                Row(
                    Column('author', css_class='form-group col-md-4 mb-3'),
                    Column('published_at', css_class='form-group col-md-4 mb-3'),
                    Column('is_published', css_class='form-group col-md-4 mb-3'),
                ),
            ),
            Submit('submit', _('Enregistrer l\'article'), css_class='btn btn-primary btn-lg w-100')
        )