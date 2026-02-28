import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from main.models import PastPresident

def create_test_president():
    print("Création d'un président de test...")
    president, created = PastPresident.objects.get_or_create(
        name="Test Président Ancien",
        mandate_start=2018,
        defaults={
            'mandate_end': 2019,
            'current_function': "Architecte Logiciel chez Microsoft",
            'bio': "<p>Ceci est une <strong>biographie de test</strong> pour vérifier que l'éditeur de texte riche s'affiche correctement.</p><ul><li>Point 1</li><li>Point 2</li></ul>",
            'is_current': False,
            'linkedin_link': 'https://linkedin.com',
        }
    )
    
    president_current, created2 = PastPresident.objects.get_or_create(
        name="Test Président Actuel",
        mandate_start=2024,
        defaults={
            'mandate_end': None,
            'current_function': "Étudiant Chercheur",
            'bio': "<p>Mot du président actuel. Bienvenue sur notre site !</p>",
            'is_current': True,
        }
    )
    
    if created or created2:
        print("✅ Présidents de test créés avec succès !")
    else:
        print("✅ Les présidents de test existent déjà.")

if __name__ == "__main__":
    create_test_president()
