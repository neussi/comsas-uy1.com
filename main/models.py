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
        verbose_name = "Élément de galerie"
        verbose_name_plural = "Galerie"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title_fr

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
        ('INT-L1', 'INT-L1'),
        ('INT-L2', 'INT-L2'),
        ('INT-L3', 'INT-L3'),
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