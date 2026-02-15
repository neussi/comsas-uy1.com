import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from django.core.files import File
from main.models import Archive, ArchiveComment

def create_archives():
    print("Création des archives de test...")
    
    # Création d'un fichier dummy
    dummy_path = 'dummy_archive.pdf'
    with open(dummy_path, 'w') as f:
        f.write('Contenu de test pour archive PDF.')

    titles = [
        ("Procès Verbal AG Rentrée", "PV"),
        ("Liste des groupes TP Réseaux", "OTHER"),
        ("Planning des examens S1", "OTHER"),
        ("Tutoriel Django Débutant", "OTHER"),
        ("Rapport Financier Semestriel", "PV"),
        ("Sujet Corrigé Analyse 2023", "OTHER"),
        ("Note d'information Concours", "OTHER"),
    ]
    
    levels = ['L1', 'L2', 'L3', 'M1', 'M2', 'ICT-L1']
    authors = ["Alice K.", "Bob M.", "Chloé D.", "Admin", "Anonyme"]
    comments_text = [
        "Merci pour ce partage !",
        "Est-ce que c'est bien la version finale ?",
        "Très utile, merci.",
        "Impossible de télécharger hier, mais ça marche aujourd'hui.",
        "Super doc !"
    ]

    for i in range(8):
        title_base, cat = random.choice(titles)
        title = f"{title_base} #{random.randint(100, 999)}"
        
        archive = Archive(
            title=title,
            description=f"Ceci est une description automatique pour le document {title}. Il contient des informations importantes pour les étudiants.",
            academic_year=f"202{random.randint(3, 4)}-202{random.randint(5, 6)}",
            level=random.choice(levels),
            category=cat,
            views_count=random.randint(50, 500),
            downloads_count=random.randint(10, 100),
            likes_count=random.randint(5, 50)
        )
        
        # Save file and model
        with open(dummy_path, 'rb') as f:
            archive.file.save(f'archive_test_{i}.pdf', File(f), save=True)
            
        print(f"Archive créée: {archive.title} ({archive.slug})")
        
        # Add comments
        for _ in range(random.randint(0, 4)):
            ArchiveComment.objects.create(
                archive=archive,
                author_name=random.choice(authors),
                content=random.choice(comments_text)
            )

    # Cleanup
    if os.path.exists(dummy_path):
        os.remove(dummy_path)
    
    print("Terminé ! 8 archives créées avec succès.")

if __name__ == '__main__':
    create_archives()
