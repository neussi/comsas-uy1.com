import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')
django.setup()

from main.models import JUINEdition, JUINCommission, JUINActivity, JUINCompetition

def populate_juin():
    print("Populating JUIN 2026 data...")
    
    # 1. Create Edition
    edition, created = JUINEdition.objects.get_or_create(
        edition_number=20,
        defaults={
            'title': "20ème Édition — Jubilé d'Émeraude",
            'theme': "Le Numérique au Service de l'Entrepreneuriat et de l'Innovation Jeune : Catalyseur de Progrès et d'Opportunités",
            'slogan': "Coder • Innover • Entreprendre",
            'description': "Le J.U.IN 2026 est une édition historique célébrant 20 ans d'excellence informatique à l'Université de Yaoundé I.",
            'start_date': timezone.now().date() + timedelta(days=60),
            'end_date': timezone.now().date() + timedelta(days=65),
            'location': "Campus UY1 — Esplanade Extension 1, Faculté des Sciences",
            'is_active': True,
            'applications_open': True,
            'donations_open': True,
            'president_name': "MFENJOU ANAS CHERIF",
            'president_contact': "+237 600 000 000"
        }
    )
    if not created:
        edition.is_active = True
        edition.applications_open = True
        edition.donations_open = True
        edition.save()
        print(f"Updated existing edition: {edition}")
    else:
        print(f"Created new edition: {edition}")

    # 2. Create Commissions
    commissions_data = [
        ('CELLCOM-JUIN', 'Communication & Marketing', 'fa-bullhorn', 'primary', "TCHAPTCHET N. S.", "+237 611111111"),
        ('PROJ-INV', 'Projets & Innovations', 'fa-laptop-code', 'success', "WAFO D.", "+237 622222222"),
        ('LOG-JUIN', 'Logistique & Organisation', 'fa-truck', 'warning', "DJOUKENG T. R.", "+237 633333333"),
        ('PART-JUIN', 'Partenariats & Sponsoring', 'fa-handshake', 'info', "NGUEGANG L.", "+237 644444444"),
        ('GASTRO', 'Gastronomie', 'fa-utensils', 'danger', "MBIA K. A.", "+237 655555555"),
        ('PROTO', 'Protocole & Accueil', 'fa-shield-alt', 'info', "FOTSING J.", "+237 666666666"),
    ]

    for code, name, icon, color, chef, contact in commissions_data:
        comm, c_created = JUINCommission.objects.get_or_create(
            edition=edition,
            code=code,
            defaults={
                'name': name,
                'icon': icon,
                'color': color,
                'description': f"Commission en charge de {name.lower()} pour le J.U.IN 2026.",
                'chef_nom': chef,
                'chef_contact': contact,
                'order': commissions_data.index((code, name, icon, color, chef, contact))
            }
        )
        if c_created:
            print(f"Created commission: {name}")

    # 3. Create Activities
    activities_data = [
        ("Cérémonie d'Ouverture", "Lancement officiel de la 20ème édition.", 'ceremonie', 0),
        ("Hackathon 48h", "Compétition de code non-stop.", 'hackathon', 1),
        ("Conférence IA", "Intelligence Artificielle et Opportunités.", 'conference', 2),
        ("Soirée de Gala", "Clôture et remise des prix.", 'gala', 3),
    ]

    for title, desc, a_type, order in activities_data:
        act, a_created = JUINActivity.objects.get_or_create(
            edition=edition,
            title=title,
            defaults={
                'description': desc,
                'activity_type': a_type,
                'date_activity': timezone.now() + timedelta(days=60 + order),
                'location': "Amphi 350",
                'is_featured': True,
                'order': order
            }
        )
        if a_created:
            print(f"Created activity: {title}")

    # 4. Create Competitions
    competitions_data = [
        ("Hackathon J.U.IN", "Développement de solutions innovantes en 48h.", 'computer'),
        ("Tournoi de Football", "Compétition sportive inter-niveaux.", 'sport'),
    ]

    for name, desc, c_type in competitions_data:
        comp, cp_created = JUINCompetition.objects.get_or_create(
            edition=edition,
            name=name,
            defaults={
                'description': desc,
                'comp_type': c_type,
                'is_open': True,
                'max_teams': 10
            }
        )
        if cp_created:
            print(f"Created competition: {name}")

if __name__ == '__main__':
    populate_juin()
    print("JUIN 2026 population completed!")
