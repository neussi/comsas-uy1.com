from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.utils import timezone
import uuid

class Member(models.Model):
    """Modèle pour les membres de l'association"""
    MEMBER_TYPES = [
        ('founder', 'Membre Fondateur'),
        ('bureau', 'Membre du Bureau'),
        ('conseil', 'Conseiller'),
        ('simple', 'Membre Simple'),
    ]
    
    LEVEL_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('ICT-L1', 'ICT-L1'),
        ('ICT-L2', 'ICT-L2'),
        ('ICT-L3', 'ICT-L3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('PhD', 'Doctorat'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nom_prenom = models.CharField(max_length=200, verbose_name="Nom et Prénom")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    lieu_naissance = models.CharField(max_length=100, verbose_name="Lieu de naissance")
    niveau = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Niveau", blank=True, null=True)
    promotion = models.CharField(max_length=20, verbose_name="Promotion (année de sortie)", blank=True, null=True)
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    email = models.EmailField(verbose_name="Adresse e-mail")
    matricule = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Matricule Étudiant")
    profession = models.CharField(max_length=200, verbose_name="Profession actuelle", blank=True, null=True)
    adresse = models.TextField(verbose_name="Adresse actuelle", blank=True, null=True)
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPES, default='simple')
    poste_bureau = models.CharField(max_length=100, blank=True, null=True, verbose_name="Poste au bureau")
    photo = models.ImageField(upload_to='members/', blank=True, null=True)
    bio = RichTextField(blank=True, null=True, verbose_name="Biographie")
    is_active = models.BooleanField(default=False)
    date_adhesion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
        ordering = ['nom_prenom']
    
    def __str__(self):
        return self.nom_prenom

class Project(models.Model):
    """Modèle pour les projets de l'association"""
    STATUS_CHOICES = [
        ('planning', 'En planification'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminé'),
        ('suspended', 'Suspendu'),
    ]
    
    title_fr = models.CharField(max_length=200, verbose_name="Titre (Français)")
    title_en = models.CharField(max_length=200, verbose_name="Titre (Anglais)")
    description_fr = RichTextField(verbose_name="Description (Français)")
    description_en = RichTextField(verbose_name="Description (Anglais)")
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    budget_required = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Budget requis (FCFA)")
    budget_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Budget collecté (FCFA)")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(blank=True, null=True, verbose_name="Date de fin")
    is_featured = models.BooleanField(default=False, verbose_name="Projet en vedette")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title_fr
    
    @property
    def progress_percentage(self):
        if self.budget_required > 0:
            return min((self.budget_collected / self.budget_required) * 100, 100)
        return 0

class Event(models.Model):
    """Modèle pour les événements"""
    title_fr = models.CharField(max_length=200, verbose_name="Titre (Français)")
    title_en = models.CharField(max_length=200, verbose_name="Titre (Anglais)")
    description_fr = RichTextField(verbose_name="Description (Français)")
    description_en = RichTextField(verbose_name="Description (Anglais)")
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    date_event = models.DateTimeField(verbose_name="Date et heure de l'événement")
    location = models.CharField(max_length=200, verbose_name="Lieu")
    max_participants = models.IntegerField(blank=True, null=True, verbose_name="Nombre maximum de participants")
    registration_deadline = models.DateTimeField(verbose_name="Date limite d'inscription")
    is_featured = models.BooleanField(default=False, verbose_name="Événement en vedette")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Certificate Configuration
    certificate_enabled = models.BooleanField(default=True, verbose_name="Activer les attestations")
    certificate_title = models.CharField(max_length=200, blank=True, verbose_name="Titre de l'attestation")
    certificate_description = models.TextField(blank=True, verbose_name="Description pour l'attestation")
    certificate_president_name = models.CharField(max_length=100, default="Président COMS.A.S", verbose_name="Nom du président")
    certificate_president_title = models.CharField(max_length=100, default="Président du COMS.A.S", verbose_name="Titre du président")
    certificate_dept_head_name = models.CharField(max_length=100, default="Chef de département", verbose_name="Nom du chef de département")
    certificate_dept_head_title = models.CharField(max_length=100, default="Chef de département informatique", verbose_name="Titre du chef de département")
    
    # Badge Configuration
    badge_enabled = models.BooleanField(default=True, verbose_name="Activer les badges")

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['date_event']
    
    def __str__(self):
        return self.title_fr
    
    @property
    def is_registration_open(self):
        return timezone.now() < self.registration_deadline and self.is_active
    
    @property
    def registered_count(self):
        return self.eventregistration_set.filter(is_confirmed=True).count()

class EventRegistration(models.Model):
    """Modèle pour les inscriptions aux événements"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    nom_prenom = models.CharField(max_length=200, verbose_name="Nom et Prénom")
    email = models.EmailField(verbose_name="Adresse e-mail")
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    promotion = models.CharField(max_length=20, verbose_name="Promotion")
    message = models.TextField(blank=True, verbose_name="Message/Commentaire")
    photo = models.ImageField(upload_to='participants/photos/', blank=True, null=True, verbose_name="Photo du participant", help_text="Photo pour le badge (optionnel)")
    is_confirmed = models.BooleanField(default=False, verbose_name="Confirmé")
    registration_date = models.DateTimeField(auto_now_add=True)
    
    # Ticketing System
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ticket_pdf = models.FileField(upload_to='tickets/pdfs/', blank=True, null=True, verbose_name="Ticket PDF")
    qr_code = models.ImageField(upload_to='tickets/qrcodes/', blank=True, null=True, verbose_name="Code QR")
    
    # Certificate
    certificate_pdf = models.FileField(upload_to='certificates/', blank=True, null=True, verbose_name="Attestation PDF")
    
    # Badge
    badge_pdf = models.FileField(upload_to='badges/', blank=True, null=True, verbose_name="Badge PDF")
    
    class Meta:
        verbose_name = "Inscription à l'événement"
        verbose_name_plural = "Inscriptions aux événements"
        unique_together = ['event', 'email']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.nom_prenom} - {self.event.title_fr}"

class News(models.Model):
    """Modèle pour les actualités"""
    title_fr = models.CharField(max_length=200, verbose_name="Titre (Français)")
    title_en = models.CharField(max_length=200, verbose_name="Titre (Anglais)")
    content_fr = RichTextField(verbose_name="Contenu (Français)")
    content_en = RichTextField(verbose_name="Contenu (Anglais)")
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    author = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=False, verbose_name="Publié")
    is_featured = models.BooleanField(default=False, verbose_name="Article en vedette")
    publication_date = models.DateTimeField(verbose_name="Date de publication")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        ordering = ['-publication_date']
    
    def __str__(self):
        return self.title_fr

class GalleryAlbum(models.Model):
    """Album photo pour regrouper les images"""
    title_fr = models.CharField(max_length=200, verbose_name="Titre (Français)")
    title_en = models.CharField(max_length=200, verbose_name="Titre (Anglais)")
    description_fr = models.TextField(blank=True, verbose_name="Description (Français)")
    description_en = models.TextField(blank=True, verbose_name="Description (Anglais)")
    cover_image = models.ImageField(upload_to='gallery/albums/', blank=True, null=True, verbose_name="Image de couverture")
    event_date = models.DateField(default=timezone.now, verbose_name="Date de l'événement")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Album Photo"
        verbose_name_plural = "Albums Photos"
        ordering = ['-event_date']

    def __str__(self):
        return self.title_fr

class Gallery(models.Model):
    """Modèle pour la galerie multimédia"""
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Vidéo'),
    ]
    
    title_fr = models.CharField(max_length=200, verbose_name="Titre (Français)")
    title_en = models.CharField(max_length=200, verbose_name="Titre (Anglais)")
    description_fr = models.TextField(blank=True, verbose_name="Description (Français)")
    description_en = models.TextField(blank=True, verbose_name="Description (Anglais)")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name='images', verbose_name="Album", null=True, blank=True)
    image = models.ImageField(upload_to='gallery/images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, verbose_name="URL de la vidéo")
    video_file = models.FileField(upload_to='gallery/videos/', blank=True, null=True)
    is_featured = models.BooleanField(default=False, verbose_name="En vedette")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Média interactif"
        verbose_name_plural = "Médias interactifs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title_fr} ({self.get_media_type_display()})"

class PastPresident(models.Model):
    """Modèle pour les anciens présidents (et le président actuel) de l'association"""
    name = models.CharField(max_length=200, verbose_name="Nom et Prénom")
    mandate_start = models.PositiveIntegerField(verbose_name="Année de début de mandat", help_text="Ex: 2018")
    mandate_end = models.PositiveIntegerField(verbose_name="Année de fin de mandat", help_text="Ex: 2019", blank=True, null=True)
    current_function = models.CharField(max_length=200, verbose_name="Fonction actuelle", blank=True, null=True, help_text="Ex: Ingénieur Logiciel chez Google")
    bio = RichTextField(verbose_name="Biographie / Mot du Président")
    photo = models.ImageField(upload_to='presidents/', verbose_name="Photo de Profil")
    is_current = models.BooleanField(default=False, verbose_name="Est le président actuel ?")
    
    facebook_link = models.URLField(blank=True, null=True, verbose_name="Lien Facebook")
    linkedin_link = models.URLField(blank=True, null=True, verbose_name="Lien LinkedIn")
    twitter_link = models.URLField(blank=True, null=True, verbose_name="Lien Twitter/X")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Président"
        verbose_name_plural = "Présidents"
        ordering = ['-mandate_start']

    def __str__(self):
        mandate = f"{self.mandate_start}"
        if self.mandate_end:
            mandate += f" - {self.mandate_end}"
        else:
            mandate += " - Présent"
        
        status = " (Actuel)" if self.is_current else ""
        return f"{self.name} | {mandate}{status}"

class Contact(models.Model):
    """Modèle pour les messages de contact"""
    nom_prenom = models.CharField(max_length=200, verbose_name="Nom et Prénom")
    email = models.EmailField(verbose_name="Adresse e-mail")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone")
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    is_replied = models.BooleanField(default=False, verbose_name="Répondu")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nom_prenom} - {self.sujet}"

class SiteSettings(models.Model):
    """Paramètres du site"""
    site_name = models.CharField(max_length=200, default="COMS.A.S")
    slogan_fr = models.CharField(max_length=300, verbose_name="Slogan (Français)")
    slogan_en = models.CharField(max_length=300, verbose_name="Slogan (Anglais)")
    description_fr = RichTextField(verbose_name="Description de l'association (Français)")
    description_en = RichTextField(verbose_name="Description de l'association (Anglais)")
    president_message_fr = RichTextField(verbose_name="Message du président (Français)")
    president_message_en = RichTextField(verbose_name="Message du président (Anglais)")
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
    facebook_url = models.URLField(blank=True)
    whatsapp_group_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"
    
    def __str__(self):
        return self.site_name

# ------------- SPONSORSHIP SYSTEM -------------

class SponsorshipSession(models.Model):
    """Session de parrainage (ex: '2025-2')"""
    name = models.CharField(max_length=100, verbose_name="Nom de la session")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    is_active = models.BooleanField(default=True, verbose_name="Session active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Session de Parrainage"
        verbose_name_plural = "Sessions de Parrainage"
        ordering = ['-start_date']

    def __str__(self):
        return self.name

class Mentor(models.Model):
    """Parrain (Senior Student)"""
    LEVEL_CHOICES = [
        ('L3', 'Licence 3'),
        ('ICT-L3', 'ICT-L3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('PHD', 'Doctorat'),
    ]
    SPECIALTY_CHOICES = [
        ('DS', 'Data Science'),
        ('RESEAU', 'Réseau et Système'),
        ('SECU', 'Sécurité Informatique'),
        ('GL', 'Génie Logiciel'),
    ]

    session = models.ForeignKey(SponsorshipSession, on_delete=models.CASCADE, verbose_name="Session")
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name="Niveau")
    
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES, verbose_name="Spécialité")
    expertise_domains = models.TextField(verbose_name="Domaines de compétence (séparés par des virgules)")
    max_mentees = models.IntegerField(default=2, verbose_name="Nombre max de filleuls")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Parrain"
        verbose_name_plural = "Parrains"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_specialty_display()})"
    
    @property
    def current_mentees_count(self):
        return self.mentee_set.count()

# Constants for Sponsorship
COMPETENCIES_LIST = [
    ('python', 'Python'), ('java', 'Java'), ('c_cpp', 'C/C++'), ('javascript', 'JavaScript'),
    ('html_css', 'HTML/CSS'), ('react', 'React/Next.js'), ('flutter', 'Flutter'),
    ('sql', 'SQL/Database'), ('git', 'Git/GitHub'), ('docker', 'Docker'),
    ('ui_ux', 'UI/UX Design'), ('graphic_design', 'Design Graphique'),
    ('communication', 'Communication'), ('project_management', 'Gestion de Projet'),
]

DOMAINS_LIST = [
    ('software_eng', 'Génie Logiciel'), 
    ('data_science', 'Data Science / AI'), 
    ('cybersecurity', 'Cybersécurité'),
    ('cloud_devops', 'Cloud & DevOps'),
    ('network_admin', 'Administration Réseaux'),
    ('mobile_dev', 'Développement Mobile'),
    ('web_dev', 'Développement Web'),
    ('product_management', 'Product Management'),
    ('research', 'Recherche Académique'),
    ('consulting', 'Consulting / Audit'),
]

class Mentee(models.Model):
    """Filleul (Junior Student)"""
    LEVEL_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('ICT-L1', 'ICT-L1'),
        ('ICT-L2', 'ICT-L2'),
        ('ICT-L3', 'ICT-L3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('PhD', 'Doctorat'),
    ]
    SPECIALTY_CHOICES = [
        ('DS', 'Data Science'),
        ('RESEAU', 'Réseau et Système'),
        ('SECU', 'Sécurité Informatique'),
        ('GL', 'Génie Logiciel'),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Adresse e-mail")
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, verbose_name="Niveau d'étude")
    
    desired_specialty = models.CharField(max_length=100, verbose_name="Spécialité souhaitée")
    competencies = models.TextField(verbose_name="Compétences actuelles (Liste)")
    professional_domains = models.TextField(verbose_name="Domaines pro souhaités (Liste)", default="")
    
    session = models.ForeignKey(SponsorshipSession, on_delete=models.CASCADE, verbose_name="Session", null=True) # Added back
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Filleul"
        verbose_name_plural = "Filleuls"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Match(models.Model):
    """Binôme (Pairing)"""
    session = models.ForeignKey(SponsorshipSession, on_delete=models.CASCADE, verbose_name="Session")
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, verbose_name="Parrain")
    mentee = models.OneToOneField(Mentee, on_delete=models.CASCADE, verbose_name="Filleul")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Binôme"
        verbose_name_plural = "Binômes"
        ordering = ['-created_at']
        unique_together = ['mentor', 'mentee']
    
    def __str__(self):
        return f"{self.mentor} - {self.mentee}"

class Contest(models.Model):
    """Concours / Élection"""
    title = models.CharField(max_length=200, verbose_name="Titre du concours")
    slug = models.SlugField(unique=True, help_text="URL conviviale (ex: miss-master-2026)")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='contests/', blank=True, null=True, verbose_name="Image de couverture")
    
    start_date = models.DateTimeField(verbose_name="Date de début")
    end_date = models.DateTimeField(verbose_name="Date de fin")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    allow_public_candidates = models.BooleanField(default=False, verbose_name="Autoriser les candidatures publiques")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Concours"
        verbose_name_plural = "Concours"
        ordering = ['-start_date']

    def __str__(self):
        return self.title
        
    def is_open(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

class Candidate(models.Model):
    """Candidat à un concours"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='candidates', verbose_name="Concours")
    name = models.CharField(max_length=200, verbose_name="Nom du candidat / Projet")
    description = models.TextField(verbose_name="Bio / Description")
    image = models.ImageField(upload_to='candidates/', verbose_name="Photo / Image")
    video_url = models.URLField(blank=True, null=True, verbose_name="Lien Vidéo (YouTube etc.)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved', verbose_name="Statut")
    votes_count = models.IntegerField(default=0, verbose_name="Nombre de votes") # Denormalized for performance
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"
        ordering = ['-votes_count', 'name']

    def __str__(self):
        return f"{self.name} ({self.contest.title})"

class Vote(models.Model):
    """Vote individuel"""
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, verbose_name="Concours")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, verbose_name="Candidat")
    
    # Secure Verification info
    voter_email = models.EmailField(verbose_name="Email Votant", default="")
    voter_matricule = models.CharField(max_length=20, verbose_name="Matricule Votant", default="")
    
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    session_key = models.CharField(max_length=40, blank=True, null=True, verbose_name="Clé de session")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        # Strict "One Person, One Vote" constraints
        constraints = [
            models.UniqueConstraint(fields=['contest', 'voter_email'], name='unique_vote_email_per_contest'),
            models.UniqueConstraint(fields=['contest', 'voter_matricule'], name='unique_vote_matricule_per_contest'),
        ]
        indexes = [
            models.Index(fields=['contest', 'ip_address', 'session_key']),
        ]

    def __str__(self):
        return f"Vote pour {self.candidate} par {self.ip_address}"

# =============================================================================
# NOUVELLES FONCTIONNALITÉS (REQ 2026-02-12)
# =============================================================================

class RequestDocument(models.Model):
    """Modèle de requête (PDF, Word, Image)"""
    DOC_TYPES = [
        ('pdf', 'PDF'),
        ('word', 'Word'),
        ('image', 'Image'),
        ('text', 'Texte'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre du modèle")
    description = models.TextField(verbose_name="Description / Instructions", blank=True)
    file = models.FileField(upload_to='requests/documents/', blank=True, null=True, verbose_name="Fichier (PDF, Docx...)")
    image_preview = models.ImageField(upload_to='requests/previews/', blank=True, null=True, verbose_name="Aperçu (Image)")
    doc_type = models.CharField(max_length=10, choices=DOC_TYPES, default='pdf', verbose_name="Type de fichier")
    
    downloads_count = models.IntegerField(default=0, verbose_name="Nombre de téléchargements")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Modèle de Requête"
        verbose_name_plural = "Modèles de Requêtes"
        ordering = ['title']

    def __str__(self):
        return self.title

class Professor(models.Model):
    """Enseignant du département"""
    GRADES = [
        ('Pr', 'Professeur Titulaire'),
        ('Mc', 'Maître de Conférences'),
        ('Dr', 'Chargé de cours'),
        ('Ass', 'Assistant'),
        ('Mon', 'Moniteur'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom complet")
    grade = models.CharField(max_length=10, choices=GRADES, verbose_name="Grade", blank=True)
    specialty = models.CharField(max_length=200, verbose_name="Spécialité", blank=True)
    
    office_description = RichTextField(verbose_name="Description/Localisation du Bureau", blank=True)
    office_photo = models.ImageField(upload_to='department/offices/', blank=True, null=True, verbose_name="Photo de la porte du bureau")
    profile_photo = models.ImageField(upload_to='department/professors/', blank=True, null=True, verbose_name="Photo de profil")
    
    email = models.EmailField(blank=True, verbose_name="Email professionnel")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"
        ordering = ['name']

    def __str__(self):
        return f"{self.grade} {self.name}"

class Classroom(models.Model):
    """Salle de cours / Laboratoire"""
    name = models.CharField(max_length=100, verbose_name="Nom de la salle (ex: S001)")
    capacity = models.IntegerField(verbose_name="Capacité (places)", blank=True, null=True)
    location_description = RichTextField(verbose_name="Description / Localisation")
    photo = models.ImageField(upload_to='department/classrooms/', blank=True, null=True, verbose_name="Photo de la salle")
    is_lab = models.BooleanField(default=False, verbose_name="Est un laboratoire")
    
    class Meta:
        verbose_name = "Salle de cours"
        verbose_name_plural = "Salles de cours"
        ordering = ['name']

    def __str__(self):
        return self.name

class Delegate(models.Model):
    """Délégué de classe"""
    LEVEL_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('ICT-L1', 'ICT-L1'),
        ('ICT-L2', 'ICT-L2'),
        ('ICT-L3', 'ICT-L3'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom complet")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Niveau")
    photo = models.ImageField(upload_to='department/delegates/', blank=True, null=True, verbose_name="Photo")
    phone = models.CharField(max_length=20, verbose_name="Téléphone (WhatsApp)")
    email = models.EmailField(blank=True, verbose_name="Email")
    year = models.CharField(max_length=9, verbose_name="Année académique (ex: 2025-2026)", default="2025-2026")
    motto = models.CharField(max_length=200, blank=True, verbose_name="Devise / Citation")
    
    class Meta:
        verbose_name = "Délégué"
        verbose_name_plural = "Délégués"
        ordering = ['level', 'name']

    def __str__(self):
        return f"{self.name} ({self.level})"

class BlogArticle(models.Model):
    """Article de blog (Conseils, Tutos...)"""
    CATEGORIES = [
        ('tuto', 'Tutoriel'),
        ('conseil', 'Conseil Académique'),
        ('stage', 'Stage & Emploi'),
        ('master', 'Master & Recherche'),
        ('vie', 'Vie Associative'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, help_text="URL conviviale")
    image = models.ImageField(upload_to='blog/', blank=True, null=True, verbose_name="Image de couverture")
    content = RichTextField(verbose_name="Contenu de l'article")
    category = models.CharField(max_length=20, choices=CATEGORIES, default='conseil', verbose_name="Catégorie")
    
    author = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Auteur")
    published_at = models.DateTimeField(verbose_name="Date de publication", default=timezone.now)
    is_published = models.BooleanField(default=False, verbose_name="Publié")
    
    views_count = models.IntegerField(default=0, verbose_name="Vues")
    likes_count = models.IntegerField(default=0, verbose_name="J'aime")
    
    class Meta:
        verbose_name = "Article de Blog"
        verbose_name_plural = "Articles de Blog"
        ordering = ['-published_at']

    def __str__(self):
        return self.title

class Archive(models.Model):
    """Modèle pour les archives (PV, documents, images)"""
    
    LEVEL_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('ICT-L1', 'ICT-L1'),
        ('ICT-L2', 'ICT-L2'),
        ('ICT-L3', 'ICT-L3'),
        ('OTHER', 'Autre'),
    ]
    
    CATEGORY_CHOICES = [
        ('PV', 'Procès Verbal'),
        ('OTHER', 'Autre Document'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre du document")
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug URL")
    description = models.TextField(blank=True, verbose_name="Description optionnelle")
    file = models.FileField(upload_to='archives/%Y/%m/', verbose_name="Fichier (PDF, Image...)")
    academic_year = models.CharField(max_length=9, default="2023-2024", verbose_name="Année Académique", help_text="Ex: 2023-2024")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name="Niveau d'étude")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='PV', verbose_name="Catégorie")
    
    # Engagement stats
    views_count = models.IntegerField(default=0, verbose_name="Vues")
    downloads_count = models.IntegerField(default=0, verbose_name="Téléchargements")
    likes_count = models.IntegerField(default=0, verbose_name="Likes")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    class Meta:
        verbose_name = "Archive"
        verbose_name_plural = "Archives"
        ordering = ['-academic_year', '-created_at']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            # Ensure unique slug
            unique_slug = base_slug
            counter = 1
            while Archive.objects.filter(slug=unique_slug).exists(): # Note: this check works on create, but might need exclusion for update if not careful. slug usually set once.
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.academic_year})"

    @property
    def is_image(self):
        if not self.file: return False
        try:
            ext = self.file.name.lower().split('.')[-1]
            return ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']
        except: return False

    @property
    def is_pdf(self):
        if not self.file: return False
        try:
            return self.file.name.lower().endswith('.pdf')
        except: return False

class ArchiveComment(models.Model):
    """Commentaires sur les archives"""
    archive = models.ForeignKey(Archive, on_delete=models.CASCADE, related_name='comments', verbose_name="Archive")
    author_name = models.CharField(max_length=100, verbose_name="Nom complet", default="Anonyme")
    content = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    
    class Meta:
        verbose_name = "Commentaire Archive"
        verbose_name_plural = "Commentaires Archives"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Com de {self.author_name} sur {self.archive.title}"


# =============================================================================
# J.U.IN 2026 — JOURNÉES UNIVERSITAIRES DE L'INFORMATIQUE
# =============================================================================

class JUINEdition(models.Model):
    """Édition du J.U.IN"""
    SCHOOL_CHOICES = [
        ('UY1', 'Université de Yaoundé I — Faculté des Sciences'),
        ('ENSPY', 'École Nationale Supérieure Polytechnique de Yaoundé'),
        ('STJEAN', 'Institut Saint-Jean'),
        ('SUPPTIC', "SUP'PTIC"),
        ('OTHER', 'Autre'),
    ]

    edition_number = models.PositiveIntegerField(verbose_name="Numéro d'édition", default=20)
    title = models.CharField(max_length=300, verbose_name="Titre de l'édition")
    theme = models.CharField(max_length=500, verbose_name="Thème")
    slogan = models.CharField(max_length=200, default="Coder • Innover • Entreprendre", verbose_name="Slogan")
    description = models.TextField(verbose_name="Description / Argumentaire scientifique")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    location = models.CharField(max_length=300, verbose_name="Lieu", default="Campus UY1 — Esplanade extension 1")
    cover_image = models.ImageField(upload_to='juin/covers/', blank=True, null=True, verbose_name="Image de couverture")
    is_active = models.BooleanField(default=True, verbose_name="Édition active (courante)")
    applications_open = models.BooleanField(default=True, verbose_name="Inscriptions aux commissions ouvertes")
    donations_open = models.BooleanField(default=True, verbose_name="Dons ouverts")
    president_name = models.CharField(max_length=200, default="MFENJOU ANAS CHERIF", verbose_name="Président du comité")
    president_contact = models.CharField(max_length=50, blank=True, verbose_name="Contact président")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Édition J.U.IN"
        verbose_name_plural = "Éditions J.U.IN"
        ordering = ['-edition_number']

    def __str__(self):
        return f"J.U.IN {self.edition_number}ème — {self.title}"


class JUINCommission(models.Model):
    """Commission du J.U.IN"""
    ICON_CHOICES = [
        ('fa-bullhorn', 'Communication'),
        ('fa-microphone', 'Conférences'),
        ('fa-laptop-code', 'Projets & Innovations'),
        ('fa-handshake', 'Partenariats'),
        ('fa-paint-brush', 'Design & Infographie'),
        ('fa-truck', 'Logistique'),
        ('fa-shield-alt', 'Protocole'),
        ('fa-utensils', 'Gastronomie'),
        ('fa-music', 'Animation & Divertissement'),
        ('fa-glass-cheers', 'Soirée de Gala'),
    ]

    edition = models.ForeignKey(JUINEdition, on_delete=models.CASCADE, related_name='commissions', verbose_name="Édition")
    name = models.CharField(max_length=200, verbose_name="Nom de la commission")
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug")
    code = models.CharField(max_length=30, verbose_name="Code (ex: CELLCOM-JUIN)")
    description = models.TextField(verbose_name="Description / Mission")
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fa-bullhorn', verbose_name="Icône FontAwesome")
    color = models.CharField(max_length=20, default='primary', verbose_name="Couleur Bootstrap (primary, success…)")
    chef_nom = models.CharField(max_length=200, blank=True, verbose_name="Nom du/de la Chef·fe")
    chef_contact = models.CharField(max_length=100, blank=True, verbose_name="Contact Chef·fe")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Commission J.U.IN"
        verbose_name_plural = "Commissions J.U.IN"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.code} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def approved_members(self):
        return self.applications.filter(statut='approved').order_by('commission_role')


class JUINCommissionApplication(models.Model):
    """Candidature à une commission du J.U.IN"""
    STATUT_CHOICES = [
        ('pending', '⏳ En attente'),
        ('approved', '✅ Approuvé'),
        ('rejected', '❌ Rejeté'),
    ]
    ROLE_CHOICES = [
        ('president', 'Président(e)'),
        ('vice_president', 'Vice-Président(e)'),
        ('rapporteur', 'Rapporteur(e) Principal(e)'),
        ('rapporteur_adj', 'Rapporteur(e) Adjoint(e)'),
        ('membre', 'Membre'),
    ]
    LEVEL_CHOICES = [
        ('L1', 'Licence 1'), ('L2', 'Licence 2'), ('L3', 'Licence 3'),
        ('ICT-L1', 'ICT-L1'), ('ICT-L2', 'ICT-L2'), ('ICT-L3', 'ICT-L3'),
        ('M1', 'Master 1'), ('M2', 'Master 2'), ('PhD', 'Doctorat'), ('OTHER', 'Autre'),
    ]
    SCHOOL_CHOICES = [
        ('UY1-INFO', 'UY1 — Département Informatique (COM.S.AS)'),
        ('ENSPY', 'ENSPY — École Nationale Supérieure Polytechnique'),
        ('STJEAN', 'Institut Saint-Jean'),
        ('SUPPTIC', "SUP'PTIC"),
        ('OTHER', 'Autre établissement'),
    ]

    commission = models.ForeignKey(JUINCommission, on_delete=models.CASCADE, related_name='applications', verbose_name="Commission souhaitée")
    nom_prenom = models.CharField(max_length=200, verbose_name="Nom et Prénom")
    email = models.EmailField(verbose_name="Adresse e-mail")
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    etablissement = models.CharField(max_length=20, choices=SCHOOL_CHOICES, verbose_name="Établissement")
    niveau = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Niveau d'études")
    photo = models.ImageField(upload_to='juin/applicants/', blank=True, null=True, verbose_name="Photo (portrait)")
    motivation = models.TextField(verbose_name="Message de motivation", blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='pending', verbose_name="Statut")
    commission_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='membre', verbose_name="Rôle dans la commission")
    date_postulation = models.DateTimeField(auto_now_add=True, verbose_name="Date de candidature")
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")
    motif_rejet = models.TextField(blank=True, verbose_name="Motif du rejet (si rejeté)")

    class Meta:
        verbose_name = "Candidature Commission J.U.IN"
        verbose_name_plural = "Candidatures Commissions J.U.IN"
        ordering = ['-date_postulation']

    def __str__(self):
        return f"{self.nom_prenom} → {self.commission.code} ({self.get_statut_display()})"

    def save(self, *args, **kwargs):
        # Remove unique_together workaround (done via form validation instead)
        super().save(*args, **kwargs)


class JUINActivity(models.Model):
    """Activité / Agenda du J.U.IN"""
    TYPE_CHOICES = [
        ('conference', 'Conférence / Séminaire'),
        ('hackathon', 'Hackathon / Challenge'),
        ('atelier', 'Atelier pratique'),
        ('exposition', 'Exposition de projets'),
        ('pitch', 'Concours de Pitch'),
        ('sport', 'Activité Sportive (Foot, Basket...)'),
        ('gala', 'Soirée de Gala'),
        ('ceremonie', 'Cérémonie officielle'),
        ('autre', 'Autre'),
    ]

    edition = models.ForeignKey(JUINEdition, on_delete=models.CASCADE, related_name='activities', verbose_name="Édition")
    title = models.CharField(max_length=200, verbose_name="Titre de l'activité")
    description = models.TextField(verbose_name="Description")
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='conference', verbose_name="Type")
    date_activity = models.DateTimeField(verbose_name="Date et heure")
    location = models.CharField(max_length=200, blank=True, verbose_name="Salle / Lieu")
    speaker = models.CharField(max_length=200, blank=True, verbose_name="Intervenant(s)")
    cover_image = models.ImageField(upload_to='juin/activities/', blank=True, null=True, verbose_name="Photo / Affiche")
    gallery_album = models.ForeignKey('GalleryAlbum', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='juin_activities', verbose_name="Album galerie lié")
    is_featured = models.BooleanField(default=False, verbose_name="Activité phare")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activité J.U.IN"
        verbose_name_plural = "Activités J.U.IN"
        ordering = ['date_activity', 'order']

    def __str__(self):
        return f"{self.get_activity_type_display()} — {self.title}"


class JUINCompetition(models.Model):
    """Compétition spécifique au J.U.IN (Informatique ou Sport)"""
    COMP_TYPES = [
        ('computer', '💻 Informatique (Hackathon, Pitch, Cyber...)'),
        ('sport', '⚽ Sportive (Football, Basketball, Handball...)'),
        ('gaming', '🎮 E-Sport / Gaming'),
        ('other', 'Autre'),
    ]
    edition = models.ForeignKey(JUINEdition, on_delete=models.CASCADE, related_name='competitions', verbose_name="Édition")
    name = models.CharField(max_length=200, verbose_name="Nom de la compétition")
    slug = models.SlugField(blank=True, null=True, help_text="Laissé vide, sera généré automatiquement")
    comp_type = models.CharField(max_length=20, choices=COMP_TYPES, default='computer', verbose_name="Type")
    description = models.TextField(verbose_name="Description")
    rules = models.TextField(blank=True, verbose_name="Règles / Conditions d'admission")
    image = models.ImageField(upload_to='juin/competitions/', blank=True, null=True, verbose_name="Image illustrative")
    
    max_teams = models.PositiveIntegerField(default=16, verbose_name="Nombre maximum d'équipes")
    is_open = models.BooleanField(default=True, verbose_name="Inscriptions ouvertes")
    start_date = models.DateTimeField(verbose_name="Date et heure de début", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Compétition J.U.IN"
        verbose_name_plural = "Compétitions J.U.IN"

    def __str__(self):
        return f"{self.name} — J.U.IN {self.edition.edition_number}"


class JUINTeam(models.Model):
    """Équipe ou Candidat inscrit à une compétition"""
    STATUT_CHOICES = [
        ('pending', '⏳ En attente'),
        ('approved', '✅ Validée'),
        ('rejected', '❌ Refusée'),
    ]
    competition = models.ForeignKey(JUINCompetition, on_delete=models.CASCADE, related_name='teams', verbose_name="Compétition")
    name = models.CharField(max_length=200, verbose_name="Nom de l'équipe")
    
    captain_name = models.CharField(max_length=200, verbose_name="Nom du Capitaine / Responsable")
    captain_phone = models.CharField(max_length=30, verbose_name="Téléphone (WhatsApp)")
    captain_email = models.EmailField(verbose_name="Email")
    
    members_count = models.PositiveIntegerField(default=1, verbose_name="Nombre de membres")
    members_list = models.TextField(verbose_name="Liste des membres (Noms & Prénoms)", help_text="Un par ligne")
    
    project_title = models.CharField(max_length=200, blank=True, verbose_name="Titre du projet (si informatique)")
    project_description = models.TextField(blank=True, verbose_name="Description du projet / Composition équipe")
    
    logo = models.ImageField(upload_to='juin/teams/', blank=True, null=True, verbose_name="Logo ou Photo d'équipe")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='pending', verbose_name="Statut")
    
    date_registration = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        verbose_name = "Équipe / Candidat J.U.IN"
        verbose_name_plural = "Équipes / Candidats J.U.IN"
        ordering = ['-date_registration']

    def __str__(self):
        return f"{self.name} ({self.competition.name})"


class JUINDonation(models.Model):
    """Don / Soutien à l'édition J.U.IN avec paiement Mobile Money"""
    PAYMENT_CHOICES = [
        ('mtn', 'MTN Mobile Money'),
        ('orange', 'Orange Money'),
        ('cb', 'Carte Bancaire'),
        ('especes', 'Espèces'),
        ('autre', 'Autre'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('initiated', 'Initié — en cours'),
        ('completed', 'Payé ✅'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]

    edition = models.ForeignKey(JUINEdition, on_delete=models.CASCADE, related_name='donations', verbose_name="Édition")
    nom_prenom = models.CharField(max_length=200, verbose_name="Nom du donateur")
    email = models.EmailField(blank=True, verbose_name="Email (optionnel)")
    telephone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone Mobile Money")
    montant = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Montant (FCFA)")
    type_paiement = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='mtn', verbose_name="Mode de paiement")
    message = models.CharField(max_length=300, blank=True, verbose_name="Message public (optionnel)")
    is_anonymous = models.BooleanField(default=False, verbose_name="Afficher anonymement")
    is_confirmed = models.BooleanField(default=False, verbose_name="Don confirmé/reçu")
    date_don = models.DateTimeField(auto_now_add=True, verbose_name="Date du don")
    # FreemoPay payment tracking
    freemopay_reference = models.CharField(max_length=200, blank=True, verbose_name="Référence FreemoPay")
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending',
        verbose_name="Statut paiement"
    )
    external_id = models.CharField(max_length=100, blank=True, verbose_name="ID externe (UUID)")

    class Meta:
        verbose_name = "Don J.U.IN"
        verbose_name_plural = "Dons J.U.IN"
        ordering = ['-date_don']

    def __str__(self):
        return f"{self.nom_prenom} — {self.montant} FCFA ({self.get_type_paiement_display()})"

    @property
    def display_name(self):
        return "Donateur Anonyme" if self.is_anonymous else self.nom_prenom


class JUINSponsor(models.Model):
    """Sponsors et partenaires du J.U.IN 2026"""
    TIER_CHOICES = [
        ('gold', '🥇 Sponsor Or (500 000 F+)'),
        ('silver', '🥈 Sponsor Argent (200 000 F+)'),
        ('bronze', '🥉 Sponsor Bronze (100 000 F+)'),
        ('partner', '🤝 Partenaire Technique'),
        ('institution', '🏛️ Institution / Soutien académique'),
        ('media', '📺 Partenaire Médias'),
    ]
    STATUT_CHOICES = [
        ('pending', '⏳ Demande en attente'),
        ('approved', '✅ Approuvé — visible'),
        ('rejected', '❌ Refusé'),
    ]

    edition = models.ForeignKey(
        JUINEdition, on_delete=models.CASCADE, related_name='sponsors',
        verbose_name="Édition"
    )
    company_name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise / institution")
    logo = models.ImageField(upload_to='juin/sponsors/', blank=True, null=True, verbose_name="Logo")
    website = models.URLField(blank=True, verbose_name="Site web")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze', verbose_name="Niveau de partenariat")
    
    # Contact de la demande
    contact_name = models.CharField(max_length=200, verbose_name="Nom du responsable")
    contact_email = models.EmailField(verbose_name="Email de contact")
    contact_phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    
    # Description
    description = models.TextField(blank=True, verbose_name="Description / offre de partenariat")
    contribution = models.CharField(max_length=500, blank=True, verbose_name="Contribution proposée (financière, matérielle, services...)")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='pending', verbose_name="Statut")
    is_featured = models.BooleanField(default=False, verbose_name="Mettre en avant")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    
    # Admin notes
    admin_notes = models.TextField(blank=True, verbose_name="Notes internes (admin)")
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date de la demande")
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")

    class Meta:
        verbose_name = "Sponsor / Partenaire J.U.IN"
        verbose_name_plural = "Sponsors / Partenaires J.U.IN"
        ordering = ['order', 'tier', 'company_name']

    def __str__(self):
        return f"{self.company_name} — {self.get_tier_display()} ({self.get_statut_display()})"

    @property
    def tier_color(self):
        colors = {
            'gold': '#eab308', 'silver': '#94a3b8', 'bronze': '#b45309',
            'partner': '#06b6d4', 'institution': '#8b5cf6', 'media': '#f43f5e',
        }
        return colors.get(self.tier, '#6b7280')