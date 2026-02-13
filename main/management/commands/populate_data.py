import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import (
    Professor, Classroom, Delegate, BlogArticle, RequestDocument, 
    Member, Contest, Candidate, Vote
)
from django.utils.text import slugify
from django.core.files.base import ContentFile
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database...')

        # Utility to get image content
        def get_image_content(filename):
            try:
                with open(f"static/images/{filename}", "rb") as f:
                    return ContentFile(f.read(), name=filename)
            except FileNotFoundError:
                return None
        
        # 1. Professors
        self.stdout.write('Creating Professors...')
        prof_titles = ['Pr', 'Dr', 'Mc']
        prof_names = [
            'Atsa Etoundi', 'Mvogo Ngono', 'Nlong II', 'Tapamo', 
            'Tindo', 'Fotsin', 'Melather', 'Kolyang', 'Moungo', 'Zoueu'
        ]
        specialties = ['Génie Logiciel', 'Intelligence Artificielle', 'Réseaux', 'Cryptographie', 'Systèmes Distribués']
        
        for i, name in enumerate(prof_names):
            prof, created = Professor.objects.get_or_create(
                name=f"{name}",
                defaults={
                    'grade': random.choice(prof_titles),
                    'specialty': random.choice(specialties),
                    'office_description': f"Bâtiment Principal, Porte {100+i}",
                    'email': f"{name.lower().replace(' ', '')}@uy1.cm",
                    'is_active': True,
                    'profile_photo': get_image_content("uy1.png")
                }
            )
            if not created and not prof.profile_photo:
                prof.profile_photo = get_image_content("uy1.png")
                prof.save()

        # 2. Classrooms
        self.stdout.write('Creating Classrooms...')
        classrooms = ['S001', 'S002', 'Amphi 350', 'Amphi 1001', 'Labo Info 1', 'Labo Réseaux']
        for room in classrooms:
            Classroom.objects.get_or_create(
                name=room,
                defaults={
                    'capacity': random.randint(30, 1000),
                    'location_description': "Nouveau Bloc Pédagogique, Rez-de-chaussée",
                    'is_lab': 'Labo' in room
                }
            )

        # 3. Delegates
        self.stdout.write('Creating Delegates...')
        levels = ['L1', 'L2', 'L3', 'M1', 'M2', 'INT-L1', 'INT-L2', 'INT-L3']
        for level in levels:
            delegate, created = Delegate.objects.get_or_create(
                level=level,
                defaults={
                    'name': f"Délégué {level}",
                    'phone': "+237600000000",
                    'email': f"delegate.{level.lower()}@comsas.com",
                    'year': "2025-2026",
                    'motto': "Servir et non se servir",
                    'photo': get_image_content("comsas.png")
                }
            )
            if not created and not delegate.photo:
                delegate.photo = get_image_content("comsas.png")
                delegate.save()

        # 4. Request Documents
        # 4. Request Documents
        self.stdout.write('Creating Documents...')
        RequestDocument.objects.all().delete() # Clean existing to fix missing files
        docs = [
            ('Demande de Stage Académique', 'word'),
            ('Demande de Relevé de Notes', 'pdf'),
            ('Demande de Rectification de Note', 'word'),
            ('Autorisation d\'absence', 'pdf'),
            ('Charte de l\'étudiant', 'pdf')
        ]
        for title, dtype in docs:
            RequestDocument.objects.get_or_create(
                title=title,
                defaults={
                    'description': "Modèle officiel à télécharger et remplir. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    'doc_type': dtype,
                    'downloads_count': random.randint(10, 500),
                    'file': ContentFile(b"Contenu de test pour le document.", name=f"{slugify(title)}.{dtype}")
                }
            )

        # 5. Blog Articles
        self.stdout.write('Creating Blog Articles...')
        # Create a dummy author first
        author, _ = Member.objects.get_or_create(
            nom_prenom="Redaction COMSAS",
            defaults={
                'email': 'redaction@comsas.com', 
                'matricule': 'CM001',
                'date_naissance': timezone.now() - timedelta(days=365*20), # 20 ans
                'lieu_naissance': 'Yaoundé',
                'telephone': '+237600000000'
            }
        )
        
        articles = [
            ("Comment réussir sa soutenance ?", "conseil"),
            ("Les meilleures entreprises pour un stage au Cameroun", "stage"),
            ("Tuto: Déployer Django sur VPS", "tuto"),
            ("Retour sur la semaine de l'informatique", "vie"),
            ("Bourse d'excellence: Comment postuler ?", "master")
        ]
        
        for title, cat in articles:
            # Use slugify to ensure clean slugs
            slug_base = slugify(title)
            article, created = BlogArticle.objects.get_or_create(
                title=title,
                defaults={
                    'slug': slug_base,
                    'content': "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>",
                    'category': cat,
                    'author': author,
                    'is_published': True,
                    'published_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                    'views_count': random.randint(50, 5000),
                    'likes_count': random.randint(10, 500),
                    'image': get_image_content("comsas.png")
                }
            )
            if not created:
                article.likes_count = random.randint(10, 500)
                if not article.image:
                    article.image = get_image_content("comsas.png")
                article.save()

        # 6. Competitions
        self.stdout.write('Creating Competitions...')
        contest, created = Contest.objects.get_or_create(
            slug='miss-master-2026',
            defaults={
                'title': "Miss & Master COMSAS 2026",
                'description': "Élisez les ambassadeurs de l'élégance et de l'intelligence.",
                'start_date': timezone.now() - timedelta(days=2),
                'end_date': timezone.now() + timedelta(days=5),
                'is_active': True
            }
        )
        
        if created or contest.candidates.count() == 0:
            candidates = ["Sophie Mballa", "Jean Dupont", "Marie Nguemo", "Patrick Tchuente"]
            for c_name in candidates:
                cand, created = Candidate.objects.get_or_create(
                    contest=contest,
                    name=c_name,
                    defaults={
                        'description': "Passionné(e) par la tech et la mode.",
                        'status': 'approved',
                        'votes_count': random.randint(5, 50),
                        'photo': get_image_content("comsas.png")
                    }
                )
                if not created and not cand.photo:
                    cand.photo = get_image_content("comsas.png")
                    cand.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
