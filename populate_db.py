import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from django.core.files.base import ContentFile

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aaelbm2_website.settings')
django.setup()

from main.models import (
    Member, Project, Event, News, Gallery, SiteSettings,
    SponsorshipSession, Mentor, Mentee, Match,
    Contest, Candidate, Vote
)
from django.contrib.auth.models import User

def create_members():
    print("Creating Members...")
    Member.objects.all().delete()
    
    # Bureau Members
    bureau_roles = [
        ("Président", "NEUSSI NJIETCHEU Patrice Eugene"),
        ("Secrétaire Général", "DJOUKENG T. R."),
        ("Trésorier", "MBIA K. A."),
        ("Responsable Comm", "TCHAPTCHET N. S."),
        ("Commissaire aux Comptes", "FOTSING J."),
        ("Responsable Académique", "KAMGANG P."),
        ("Responsable Relations Ext.", "NGUEGANG L."),
        ("Responsable Projets", "WAFO D."),
    ]
    
    for role, name in bureau_roles:
        Member.objects.create(
            nom_prenom=name,
            date_naissance="2000-01-01",
            lieu_naissance="Yaoundé",
            promotion="2025",
            telephone="+237 600000000",
            email=f"{name.split()[0].lower()}@comsas.com",
            profession="Étudiant Master 2",
            adresse="Cité U",
            member_type='bureau',
            poste_bureau=role,
            is_active=True,
            matricule=f"25{name.split()[0][:2].upper()}{random.randint(100,999)}",
            bio="Membre dévoué du bureau exécutif, travaillant activement pour l'amélioration des conditions des étudiants et le rayonnement de l'association."
        )
        
    # Founders and Influential Members
    founders = [
        "Dr. KENNE H.", "Prof. TCHENTE", "Ing. NOUMSI", "Mme. TCHAKOUNTE", "M. FOPA"
    ]
    for name in founders:
        Member.objects.create(
            nom_prenom=name,
            date_naissance="1980-01-01",  # Valeur par défaut pour les fondateurs
            lieu_naissance="Cameroun",
            promotion="2010",
            email=f"{name.split()[-1].lower()}@comsas.com",
            member_type='founder',
            profession="Ingénieur Senior",
            is_active=True,
            matricule=f"10{name.split()[-1][:2].upper()}{random.randint(100,999)}",
            bio="Un des piliers de la création de notre grande communauté."
        )

    # Simple Members
    for i in range(15):
        Member.objects.create(
            nom_prenom=f"Membre {i+1}",
            date_naissance="2002-05-15",
            lieu_naissance="Douala",
            promotion=f"202{random.randint(4,6)}",
            telephone="+237 600000000",
            email=f"membre{i+1}@test.com",
            profession="Étudiant Licence 3",
            adresse="Ngoa-Ekélé",
            member_type='simple',
            is_active=True,
            matricule=f"22SIM{random.randint(1000,9999)}"
        )

def create_projects():
    print("Creating Projects...")
    Project.objects.all().delete()
    
    projects = [
        ("Plateforme E-Learning", "Une plateforme centralisée pour le partage de cours, TD et anciens sujets d'examens. Inclut un forum de discussion.", "ongoing"),
        ("Application Mobile Campus", "Application Android/iOS pour la navigation sur le campus, emploi du temps en temps réel et notifications.", "planning"),
        ("Site Web COM.S.AS", "Refonte complète du site web de l'association avec gestion des membres, événements et blog.", "completed"),
        ("Hackathon IA 2026", "Organisation du plus grand hackathon universitaire sur l'Intelligence Artificielle au Cameroun.", "planning"),
        ("Ateliers de Formation Python", "Série d'ateliers pratiques pour initier les étudiants à la programmation Python et Data Science.", "ongoing"),
        ("Bibliothèque Numérique", "Numérisation et mise à disposition des mémoires de fin d'études des anciens étudiants.", "suspended"),
    ]
    
    for title, desc, status in projects:
        Project.objects.create(
            title_fr=title,
            title_en=title + " (EN)",
            description_fr=desc,
            description_en=desc + " (EN)",
            status=status,
            budget_required=random.randint(100000, 2000000),
            budget_collected=random.randint(0, 500000),
            start_date=timezone.now(),
            is_featured=True
        )

def create_events():
    print("Creating Events...")
    Event.objects.all().delete()
    
    events = [
        ("Seminaire React JS", "Formation intensive sur React JS pour les débutants et intermédiaires. Création d'une application de A à Z."),
        ("Gala de fin d'année", "Grande soirée de gala pour célébrer la fin de l'année académique et la remise des diplômes."),
        ("Concours de Code", "Compétition de programmation compétitive (Algorithmique et Structures de Données). Prix à gagner !"),
        ("Conférence IA & Éthique", "Table ronde avec des experts sur les enjeux éthiques de l'Intelligence Artificielle."),
        ("Journée d'Intégration", "Activités ludiques et sportives pour accueillir les nouveaux étudiants de Licence 1."),
        ("Workshop Cyber-Sécurité", "Atelier pratique sur les bases de la sécurité informatique et le pentesting."),
    ]
    
    for title, desc in events:
        Event.objects.create(
            title_fr=title,
            title_en=title + " (EN)",
            description_fr=desc,
            description_en=desc + " (EN)",
            date_event=timezone.now() + timedelta(days=random.randint(10, 90)),
            location="Amphi 350",
            registration_deadline=timezone.now() + timedelta(days=10),
            is_featured=True,
            is_active=True
        )

def create_news():
    print("Creating News...")
    News.objects.all().delete()
    
    news_items = [
        ("Lancement des activités 2025", "Le club lance officiellement ses activités pour la nouvelle année académique. Découvrez le programme !"),
        ("Partenariat avec Google", "Nous sommes fiers d'annoncer un nouveau partenariat stratégique avec Google Developer Groups."),
        ("Retour sur le Hackathon", "Les gagnants du Hackathon 2025 ont été primés. Félicitations à l'équipe 'CodeNinjas' !"),
        ("Appel à candidatures Bureau", "Les élections pour le nouveau bureau exécutif sont ouvertes. Déposez votre candidature."),
        ("Nouveaux T-Shirts Disponibles", "Les t-shirts officiels du COM.S.AS sont arrivés. Passez au bureau pour récupérer le vôtre."),
        ("Interview du Président", "Retrouvez l'interview exclusive de notre président sur la vision de ce mandat."),
    ]
    
    for title, content in news_items:
        News.objects.create(
            title_fr=title,
            title_en=title + " (EN)",
            content_fr=content,
            content_en=content + " (EN)",
            publication_date=timezone.now() - timedelta(days=random.randint(1, 60)),
            is_published=True,
            is_featured=True
        )

def create_gallery():
    print("Creating Gallery...")
    Gallery.objects.all().delete()
    
    items = [
        ("Cérémonie d'ouverture", "Photos officielles de la cérémonie d'ouverture."),
        ("Workshop Python", "Séance de coding intense lors de l'atelier Python."),
        ("Remise des prix", "Les lauréats du hackathon recevant leurs récompenses."),
        ("Match de Football", "L'équipe du département lors du tournoi inter-filières."),
        ("Visite d'entreprise", "Découverte des locaux de notre partenaire technologique."),
        ("Soirée de Gala", "Moments forts de la soirée de gala."),
    ]
    
    for title, desc in items:
        Gallery.objects.create(
            title_fr=title,
            title_en=title + " (EN)",
            description_fr=desc,
            description_en=desc + " (EN)",
            media_type='image',
            is_featured=True
        )

def create_site_settings():
    print("Creating Site Settings...")
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(
        site_name="COM.S.AS",
        slogan_fr="Excellence - Innovation - Partage",
        slogan_en="Excellence - Innovation - Sharing",
        description_fr="La communauté des étudiants en informatique.",
        description_en="The computer science students community.",
        president_message_fr="Bienvenue sur notre nouveau site !",
        president_message_en="Welcome to our new website !"
    )

def create_sponsorship():
    print("Creating Sponsorship Data...")
    SponsorshipSession.objects.all().delete()
    
    # 1. Create Session
    session = SponsorshipSession.objects.create(
        name="Parrainage 2024-2025",
        start_date=timezone.now() - timedelta(days=30),
        end_date=timezone.now() + timedelta(days=90),
        is_active=True
    )
    
    # 2. Create Mentors (L3, M1, M2)
    mentors_data = [
        ("NANA P.", "L3", "GL"),
        ("FOTSO A.", "M1", "RESEAU"),
        ("KAMGA B.", "M2", "DS"),
        ("ABENA C.", "L3", "GL"), # Changed TI to GL for simplicity/matching
        ("EBOGO D.", "M1", "SECU"),
    ]
    
    mentors = []
    for last_name, level, spec in mentors_data:
        m = Mentor.objects.create(
            session=session,
            first_name="Parrain",
            last_name=last_name,
            email=f"mentor_{last_name.split()[0].lower()}@comsas.com",
            phone="+237 699887766",
            level=level,
            specialty=spec,
            expertise_domains="web_dev, python, cloud_devops",
            max_mentees=2
        )
        mentors.append(m)
        
    # 3. Create Mentees (L1, L2)
    mentees_data = [
        ("TCHOUAMO L.", "L1", "GL"), # Should match GL
        ("NOAH M.", "L1", "RESEAU"),     # Should match RESEAU
        ("BILO'O N.", "L1", "DS"),   # Should match DS
        ("MENGUE O.", "L2", "DS"),   # Should match DS
        ("ZANG P.", "L1", "GL"),     # Should match GL
        ("ETOUNDI Q.", "L2", "SECU"), # Should match SECU
    ]
    
    mentees = []
    for last_name, level, pref in mentees_data:
        m = Mentee.objects.create(
            session=session,
            first_name="Filleul",
            last_name=last_name,
            email=f"mentee_{last_name.split()[0].lower()}@comsas.com",
            phone="+237 655443322",
            level=level,
            desired_specialty=pref,
            competencies="c_cpp, html_css",
            professional_domains="software_eng, web_dev"
        )
        mentees.append(m)
        
    # 4. Create Matches (Manual matching for demo)
    # Match GL with GL
    Match.objects.create(session=session, mentor=mentors[0], mentee=mentees[0], is_active=True) # NANA (GL) - TCHOUAMO (GL)
    Match.objects.create(session=session, mentor=mentors[0], mentee=mentees[4], is_active=True) # NANA (GL) - ZANG (GL)
    # Match SR with SR
    # Note: Mentor index 1 "FOTSO A." is M1/SR, Mentee index 1 "NOAH M." is L1/RESEAU
    # Check specialty codes in creating Mentors/Mentees above. 
    # Mentor creation used "SR" but SPECIALTY_CHOICES uses 'RESEAU' for Reseau.
    # Ah, the tuple was ("FOTSO A.", "M1", "SR"), needs to match 'RESEAU' key if using choices?
    # Actually, if I look at models.py, SPECIALTY_CHOICES keys are 'DS', 'RESEAU', 'SECU', 'GL'.
    # So I should use those keys. 'SR' is not a valid key?
    # Let me check valid keys in my update below.

    Match.objects.create(session=session, mentor=mentors[1], mentee=mentees[1], is_active=True) # FOTSO (RESEAU) - NOAH (RESEAU)

def create_voting():
    print("Creating Voting Data...")
    Contest.objects.all().delete()
    
    # 1. Active Contest
    active_contest = Contest.objects.create(
        title="Meilleur Projet Info 2025",
        slug="meilleur-projet-2025",
        description="Votez pour le projet le plus innovant de l'année. Les étudiants on travaillé dur !",
        start_date=timezone.now() - timedelta(days=5),
        end_date=timezone.now() + timedelta(days=10),
        is_active=True,
        allow_public_candidates=True
    )
    
    # Candidates for Active Contest
    candidates_active = [
        ("Projet Alpha", "Une IA qui prédit les pannes de courant au Cameroun."),
        ("Projet Beta", "Application de covoiturage pour étudiants UY1."),
        ("Projet Gamma", "Système de vote sécurisé basé sur la Blockchain."),
        ("Projet Delta", "Réseau social académique pour l'entraide."),
    ]
    
    for name, desc in candidates_active:
        c = Candidate.objects.create(
            contest=active_contest,
            name=name,
            description=desc,
            status='approved',
            votes_count=0 # Reset to 0, let loop count them
        )
        # Create some random votes
        for _ in range(random.randint(5, 15)):
             v_email = f"u{random.randint(1000,9999)}@comsas.com"
             v_mat = f"MAT{random.randint(1000,9999)}"
             Vote.objects.create(
                 contest=active_contest,
                 candidate=c,
                 ip_address=f"192.168.1.{random.randint(1,255)}",
                 voter_email=v_email,
                 voter_matricule=v_mat
             )
             c.votes_count += 1
             c.save()
        
    # 2. Past Contest
    past_contest = Contest.objects.create(
        title="Miss & Master COMSAS 2024",
        slug="miss-master-2024",
        description="L'élégance et l'intelligence à l'honneur. Revivez les résultats.",
        start_date=timezone.now() - timedelta(days=365),
        end_date=timezone.now() - timedelta(days=360),
        is_active=False, # Inactive/Past
        allow_public_candidates=False
    )
    
    # Candidates for Past Contest
    candidates_past = [
        ("Candidat X", "Gagnant Master 2024"),
        ("Candidat Y", "Gagnante Miss 2024"),
    ]
    
    for name, desc in candidates_past:
        Candidate.objects.create(
            contest=past_contest,
            name=name,
            description=desc,
            status='approved',
            votes_count=random.randint(200, 500)
        )

if __name__ == '__main__':
    # Update Mentor Data specialties to match choices keys
    # ('DS', 'Data Science'), ('RESEAU', 'Réseau et Système'), ('SECU', 'Sécurité Informatique'), ('GL', 'Génie Logiciel')
    
    # Redefine create_sponsorship locally here to patch the data
    def create_sponsorship_fixed():
        print("Creating Sponsorship Data...")
        SponsorshipSession.objects.all().delete()
        
        # 1. Create Session
        session = SponsorshipSession.objects.create(
            name="Parrainage 2024-2025",
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() + timedelta(days=90),
            is_active=True
        )
        
        # 2. Create Mentors (L3, M1, M2)
        # Use CORRECT KEYS: GL, RESEAU, DS, SECU
        mentors_data = [
            ("NANA P.", "L3", "GL"),
            ("FOTSO A.", "M1", "RESEAU"),
            ("KAMGA B.", "M2", "DS"),
            ("ABENA C.", "L3", "DS"), # Changed TI to DS as TI is not in choices? Check Mentee choices too.
            ("EBOGO D.", "M1", "SECU"),
        ]
        
        mentors = []
        for last_name, level, spec in mentors_data:
            m = Mentor.objects.create(
                session=session,
                first_name="Parrain",
                last_name=last_name,
                email=f"mentor_{last_name.split()[0].lower()}@comsas.com",
                phone="+237 699887766",
                level=level,
                specialty=spec,
                expertise_domains="Développement Web, Python, Cloud",
                max_mentees=2
            )
            mentors.append(m)
            
        # 3. Create Mentees (L1, L2)
        mentees_data = [
            ("TCHOUAMO L.", "L1", "GL"), 
            ("NOAH M.", "L1", "RESEAU"),     
            ("BILO'O N.", "L1", "DS"),   
            ("MENGUE O.", "L2", "DS"), # Changed TI to DS
            ("ZANG P.", "L1", "GL"),     
            ("ETOUNDI Q.", "L2", "SECU"), 
        ]
        
        mentees = []
        for last_name, level, pref in mentees_data:
            m = Mentee.objects.create(
                session=session,
                first_name="Filleul",
                last_name=last_name,
                email=f"mentee_{last_name.split()[0].lower()}@comsas.com",
                phone="+237 655443322",
                level=level,
                desired_specialty=pref,
                competencies="C, HTML/CSS",
                professional_domain_1="Ingénieur Logiciel"
            )
            mentees.append(m)
            
        # 4. Create Matches
        Match.objects.create(session=session, mentor=mentors[0], mentee=mentees[0], is_active=True)
        Match.objects.create(session=session, mentor=mentors[0], mentee=mentees[4], is_active=True)
        Match.objects.create(session=session, mentor=mentors[1], mentee=mentees[1], is_active=True)

    create_members()
    create_projects()
    create_events()
    create_news()
    create_gallery()
    create_site_settings()
    create_sponsorship_fixed()
    create_voting()
    print("Database populated successfully!")
