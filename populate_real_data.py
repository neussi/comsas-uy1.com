#!/usr/bin/env python
"""
Script de peuplement de la base de données avec les VRAIES données du COM.S.AS.
- Crée les superutilisateurs (comsas, patrice)
- Peuple les commissions JUIN 2026
- Peuple le Bureau Exécutif 2025-2026
- Peuple les délégués
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comsas_website.settings')

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from main.models import (
    Member, JUINEdition, JUINCommission, Delegate
)
from datetime import date

print("=" * 60)
print("  COM.S.AS — Peuplement de la base de données")
print("=" * 60)

# ═══════════════════════════════════════════════════════════
# 1. SUPERUTILISATEURS
# ═══════════════════════════════════════════════════════════
print("\n[1/4] Création des superutilisateurs...")

admins = [
    {
        'username': 'comsas',
        'email': 'comsas@facsciences-uy1.cm',
        'password': 'admin@comsas',
        'first_name': 'COM.S.AS',
        'last_name': 'Admin',
    },
    {
        'username': 'patrice',
        'email': 'patrice.neussi@facsciences-uy1.cm',
        'password': 'npeprod237',
        'first_name': 'Patrice Eugène',
        'last_name': 'NEUSSI NJIETCHEU',
    },
]

for data in admins:
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        user.set_password(data['password'])
        user.save()
        print(f"   Superutilisateur '{data['username']}' créé")
    else:
        print(f"  ℹ  Superutilisateur '{data['username']}' existe déjà")


# ═══════════════════════════════════════════════════════════
# 2. ÉDITION JUIN 2026 + COMMISSIONS
# ═══════════════════════════════════════════════════════════
print("\n[2/4] Configuration de l'édition J.U.IN 2026 et des commissions...")

edition, _ = JUINEdition.objects.get_or_create(
    edition_number=20,
    defaults={
        'title': 'Jubilé d\'Émeraude',
        'theme': 'Intelligence Artificielle et Transformation Numérique en Afrique',
        'slogan': 'Coder • Innover • Entreprendre',
        'description': (
            'La 20ème édition des Journées Universitaires de l\'Informatique (J.U.IN) '
            'marque le Jubilé d\'Émeraude du COM.S.AS. Cet événement phare réunit '
            'étudiants, chercheurs et professionnels autour de l\'innovation technologique.'
        ),
        'start_date': date(2026, 6, 1),
        'end_date': date(2026, 6, 5),
        'location': 'Campus UY1 — Faculté des Sciences',
        'is_active': True,
        'applications_open': True,
        'donations_open': True,
        'president_name': 'NEUSSI NJIETCHEU PATRICE EUGÈNE',
        'president_contact': '+237 650 970 526',
    }
)
print(f"  Édition J.U.IN 2026 (#{edition.edition_number}) prête")

# Supprimer les anciennes commissions de cette édition pour les recréer proprement
JUINCommission.objects.filter(edition=edition).delete()

commissions_data = [
    {
        'name': 'Commission Conférences et Ateliers',
        'code': 'CA-JUIN',
        'description': (
            'Chargée de l\'organisation des conférences scientifiques, des panels de discussion '
            'et des ateliers pratiques avec les intervenants, chercheurs et professionnels du domaine informatique.'
        ),
        'icon': 'fa-microphone',
        'color': 'primary',
        'order': 1,
    },
    {
        'name': 'Commission Communication et Médiatisation',
        'code': 'CELLCOM-JUIN',
        'description': (
            'Chargée de la stratégie de communication, de la diffusion des informations relatives aux JUIN, '
            'de la gestion des réseaux sociaux, ainsi que de la médiatisation de l\'événement.'
        ),
        'icon': 'fa-bullhorn',
        'color': 'info',
        'order': 2,
    },
    {
        'name': 'Commission Infographie et Design Visuel',
        'code': 'IDV-JUIN',
        'description': (
            'Chargée de la conception graphique et de l\'identité visuelle de l\'événement : affiches, flyers, '
            'bannières, supports numériques et visuels de communication.'
        ),
        'icon': 'fa-paint-brush',
        'color': 'warning',
        'order': 3,
    },
    {
        'name': 'Commission Projets et Innovations',
        'code': 'PI-JUIN',
        'description': (
            'Chargée de la coordination des concours, expositions et présentations de projets technologiques, '
            'innovants et entrepreneuriaux réalisés par les étudiants et jeunes chercheurs.'
        ),
        'icon': 'fa-laptop-code',
        'color': 'success',
        'order': 4,
    },
    {
        'name': 'Commission Mobilisation des Ressources',
        'code': 'PMR-JUIN',
        'description': (
            'Chargée de la recherche de partenaires, sponsors et financements nécessaires '
            'à la bonne organisation des JUIN.'
        ),
        'icon': 'fa-handshake',
        'color': 'primary',
        'order': 5,
    },
    {
        'name': 'Commission Logistique et Infrastructures',
        'code': 'LOG-JUIN',
        'description': (
            'Chargée de l\'organisation matérielle de l\'événement : préparation des salles, équipements '
            'techniques, installations, gestion des espaces et coordination logistique.'
        ),
        'icon': 'fa-truck',
        'color': 'secondary',
        'order': 6,
    },
    {
        'name': 'Commission Protocole et Cérémonies',
        'code': 'PROTO-JUIN',
        'description': (
            'Chargée de l\'organisation protocolaire des cérémonies officielles (ouverture et clôture), '
            'de l\'accueil des invités et du respect des règles protocolaires.'
        ),
        'icon': 'fa-shield-alt',
        'color': 'dark',
        'order': 7,
    },
    {
        'name': 'Commission Gastronomie et Restauration',
        'code': 'GASTRO-JUIN',
        'description': (
            'Chargée de la planification et de l\'organisation de la restauration pour les participants, '
            'invités et intervenants pendant toute la durée de l\'événement.'
        ),
        'icon': 'fa-utensils',
        'color': 'danger',
        'order': 8,
    },
    {
        'name': 'Commission Animation et Divertissement',
        'code': 'ANIM-JUIN',
        'description': (
            'Chargée de l\'organisation des activités culturelles, ludiques et d\'animation destinées '
            'à dynamiser l\'événement et favoriser la convivialité.'
        ),
        'icon': 'fa-music',
        'color': 'info',
        'order': 9,
    },
    {
        'name': 'Commission Soirée de Gala',
        'code': 'GALA-JUIN',
        'description': (
            'Chargée de la préparation et de l\'organisation de la soirée de gala marquant '
            'la clôture officielle des Journées Universitaires de l\'Informatique.'
        ),
        'icon': 'fa-glass-cheers',
        'color': 'warning',
        'order': 10,
    },
]

for c in commissions_data:
    comm = JUINCommission.objects.create(edition=edition, **c)
    print(f"  {comm.code} — {comm.name}")


# ═══════════════════════════════════════════════════════════
# 3. BUREAU EXÉCUTIF 2025-2026
# ═══════════════════════════════════════════════════════════
print("\n[3/4] Création du Bureau Exécutif 2025-2026...")

bureau_data = [
    {
        'nom_prenom': 'NEUSSI NJIETCHEU PATRICE EUGÈNE',
        'matricule': '21T2898',
        'niveau': 'M2',
        'telephone': '+237 650 970 526',
        'poste_bureau': 'Président',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NGUE MBONG ANDRE FITZGERALD',
        'matricule': '21T2355',
        'niveau': 'L3',
        'telephone': '+237 693 338 107',
        'poste_bureau': 'Vice-Président 1',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NJIFON NJOYA AROUNA FADIL',
        'matricule': '23U2348',
        'niveau': 'L3',
        'telephone': '+237 650 972 252',
        'poste_bureau': 'Vice-Président 2',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'DJUOMBESSY DJUOMBESSY FORTUNE ANTOINETTE',
        'matricule': '23U2814',
        'niveau': 'L3',
        'telephone': '+237 654 438 809',
        'poste_bureau': 'Trésorière',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NISHIMWE ISABELLE',
        'matricule': '23U2765',
        'niveau': 'L3',
        'telephone': '+237 694 911 368',
        'poste_bureau': 'Secrétaire',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'DJOMOU KOMBOU JENNIFER',
        'matricule': '25H2367',
        'niveau': 'L1',
        'telephone': '+237 657 576 210',
        'poste_bureau': 'Secrétaire Adjointe',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'TAGNE OLA PIERRE DUREL',
        'matricule': '25G2552',
        'niveau': 'L1',
        'telephone': '+237 694 268 699',
        'poste_bureau': 'Censeur',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NZAPA-AKE SAMUEL',
        'matricule': '24F2544',
        'niveau': 'L2',
        'telephone': '+237 655 134 632',
        'poste_bureau': 'Censeur Adjoint',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'EMAMBOU TCHUNKOUA ULRICH',
        'matricule': '24F2957',
        'niveau': 'L1',
        'telephone': '+237 651 359 307',
        'poste_bureau': 'Commissaire aux Comptes 1',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'ANDOH ESSIMBI JEAN-FRANÇOIS',
        'matricule': '23V2350',
        'niveau': 'L2',
        'telephone': '+237 698 735 802',
        'poste_bureau': 'Commissaire aux Comptes 2',
        'member_type': 'bureau',
    },
    {
        'nom_prenom': 'NDJONG CEDRIC ALLAN',
        'matricule': '23V2058',
        'niveau': 'L3',
        'telephone': '+237 683 941 228',
        'poste_bureau': 'Conseiller Technique',
        'member_type': 'conseil',
    },
]

for m in bureau_data:
    member, created = Member.objects.get_or_create(
        matricule=m['matricule'],
        defaults={
            'nom_prenom': m['nom_prenom'],
            'niveau': m['niveau'],
            'telephone': m['telephone'],
            'email': f"{m['matricule'].lower()}@facsciences-uy1.cm",
            'poste_bureau': m['poste_bureau'],
            'member_type': m['member_type'],
            'is_active': True,
            'date_naissance': date(2000, 1, 1),
            'lieu_naissance': 'Yaoundé',
        }
    )
    status = "créé" if created else "existe déjà"
    print(f"  {'' if created else 'ℹ '} {m['poste_bureau']}: {m['nom_prenom']} ({status})")


# ═══════════════════════════════════════════════════════════
# 4. DÉLÉGUÉS 2025-2026
# ═══════════════════════════════════════════════════════════
print("\n[4/4] Création des délégués...")

# Supprimer les anciens délégués pour recréer proprement
Delegate.objects.filter(year='2025-2026').delete()

delegates_data = [
    # Informatique - Licence 1
    {'name': 'EMAMBOU TCHUNKOUA ULRICH', 'level': 'L1', 'phone': '651359307', 'email': 'devguyuix@gmail.com'},
    {'name': 'NGO NTJEGA TECLAIRE MAROUELLE', 'level': 'L1', 'phone': '654232286', 'email': 'marouellengontjega@gmail.com'},
    {'name': 'SORAY DJOMOU KOMBOU JENNIFER', 'level': 'L1', 'phone': '657576210', 'email': 'jenniferkombou@gmail.com'},
    {'name': 'TAGNE OLA PIERRE DURREL', 'level': 'L1', 'phone': '692409817', 'email': 'pharaondurrel@gmail.com'},
    {'name': 'DJOUGOU WINNIE', 'level': 'L1', 'phone': '698563091', 'email': 'winnieange72@gmail.com'},
    {'name': 'SIEYOJI DIVINE IDES', 'level': 'L1', 'phone': '657651565', 'email': ''},
    {'name': 'FOGUE TUENO SUZANE MIREILLE', 'level': 'L1', 'phone': '', 'email': ''},
    {'name': 'DIMITRY NGUNGE MANYANGI', 'level': 'L1', 'phone': '671727930', 'email': 'dimitryngunge5@gmail.com'},

    # Informatique - Licence 2
    {'name': 'KEMGOU WAFACK SAMIRA', 'level': 'L2', 'phone': '682595643', 'email': 'kemgousamira10@gmail.com'},
    {'name': 'KUEMATSA TALACFO HYACINTHE', 'level': 'L2', 'phone': '670621549', 'email': 'kuematsahy@gmail.com'},
    {'name': 'MOAKO EKANGO BILL ARMEL', 'level': 'L2', 'phone': '657496928', 'email': 'armel.moako@facsciences-uy1.cm'},
    {'name': 'NYUMEA PEHA DARYL GERVAIS', 'level': 'L2', 'phone': '657987954', 'email': 'gervais.nyumea@facsciences-uy1.cm'},
    {'name': 'SAMY JACQUES LAFLEUR EBETE', 'level': 'L2', 'phone': '658461659', 'email': 'ebete.samy@facsciences-uy1.cm'},
    {'name': 'EYAMO SONG ANANGA MARIE DANIELLA', 'level': 'L2', 'phone': '659425964', 'email': 'daniellasong06@gmail.com'},

    # Informatique - Licence 3
    {'name': 'DJUOMBESSY DJUOMBESSY FORTUNE ANTOINETTE', 'level': 'L3', 'phone': '654438809', 'email': ''},
    {'name': "SI'BEFON NOUAYE DEBORA VICTOIRE", 'level': 'L3', 'phone': '', 'email': ''},
    {'name': 'NDJONG CEDRIC ALLAN', 'level': 'L3', 'phone': '683941228', 'email': ''},
    {'name': 'NAJELA MELVIS NURVI', 'level': 'L3', 'phone': '', 'email': ''},
    {'name': 'FONAYEN CHRISTIAN', 'level': 'L3', 'phone': '681144815', 'email': 'asangwa.fonayen23@facsciences-uy1.cm'},
    {'name': 'ETONDE MABONGO ULRICH EDOUARD', 'level': 'L3', 'phone': '', 'email': 'edouard.etonde@facsciences-uy1.cm'},

]

count = 0
for d in delegates_data:
    Delegate.objects.create(
        name=d['name'],
        level=d['level'],
        phone=d.get('phone', ''),
        email=d.get('email', ''),
        year='2025-2026',
    )
    count += 1

print(f"   {count} délégués créés")


# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  Peuplement terminé avec succès !")
print("=" * 60)
print(f"""
 Résumé :
  • Superutilisateurs : {User.objects.filter(is_superuser=True).count()}
  • Membres du Bureau : {Member.objects.filter(member_type='bureau').count()}
  • Commissions JUIN  : {JUINCommission.objects.filter(edition=edition).count()}
  • Délégués          : {Delegate.objects.filter(year='2025-2026').count()}

 Accès Admin :
  • comsas / admin@comsas
  • patrice / npeprod237

 Accès pgAdmin :
  • URL : http://localhost:5050
  • Email : comsas@facsciences-uy1.cm
  • Mot de passe : admin@comsas
  • Serveur DB : db:5432 / comsas_db
""")
