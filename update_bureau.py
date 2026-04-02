import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comsas_website.settings")
django.setup()

from main.models import Member

def update_bureau():
    # 1. Downgrade existing bureau members to 'simple' to avoid duplicates
    Member.objects.filter(member_type='bureau').update(member_type='simple', poste_bureau='')

    bureau_data = [
        {'name': 'NEUSSI NJIETCHEU PATRICE EUGENE', 'matricule': '21T2898', 'niveau': 'M2', 'telephone': '650970526', 'poste': 'Président'},
        {'name': 'NJIFON NJOYA AROUNA FADIL', 'matricule': '23U2348', 'niveau': 'ICT-L3', 'telephone': '650972252', 'poste': 'Vice-Président 1'},
        {'name': 'NGUE MBONG ANDRE FITZGERALD', 'matricule': '21T2355', 'niveau': 'L3', 'telephone': '693338107', 'poste': 'Vice-Président 2'},
        {'name': 'NISHIMWE ISABELLE', 'matricule': '', 'niveau': 'L3', 'telephone': '694911368', 'poste': 'Secrétaire'},
        {'name': 'DJOMOU KOMBOU JENNIFER', 'matricule': '25H2367', 'niveau': 'L1', 'telephone': '657576210', 'poste': 'Secrétaire Adjoint'},
        {'name': 'MBAKOP TCHOUPA MERVEILLES GLORIA', 'matricule': '', 'niveau': 'L2', 'telephone': '658560293', 'poste': 'Trésorier'},
        {'name': 'TAGNE OLA PIERRE DUREL', 'matricule': '', 'niveau': 'L1', 'telephone': '694266899', 'poste': 'Censeur'},
        {'name': 'CHOUDSA TADBERIA FREDDY', 'matricule': '', 'niveau': 'ICT-L2', 'telephone': '694089990', 'poste': 'Censeur Adjoint'},
        {'name': 'ANDOH ESSIMBI JEAN-FRANÇOIS', 'matricule': '', 'niveau': 'L2', 'telephone': '698735802', 'poste': 'Commissaire aux Comptes 1'},
        {'name': 'EMAMBOU TCHUNKOUA ULRICH', 'matricule': '', 'niveau': 'L1', 'telephone': '651359307', 'poste': 'Commissaire aux Comptes 2'},
        {'name': 'NDANGA WANDJI STEEV HARRY', 'matricule': '', 'niveau': 'ICT-L1', 'telephone': '691209620', 'poste': 'Conseiller Technique'},
    ]

    for data in bureau_data:
        # Search by phone
        member = Member.objects.filter(telephone__icontains=data['telephone']).first()
        
        # Search by exact name
        if not member:
            member = Member.objects.filter(nom_prenom__iexact=data['name']).first()
        
        # Search by part of name
        if not member:
            first_name_part = data['name'].split()[0]
            member = Member.objects.filter(nom_prenom__icontains=first_name_part).first()
            
        if not member:
            print(f"Creating new member: {data['name']}")
            member = Member(
                nom_prenom=data['name'],
                email=f"{data['name'].replace(' ', '.').lower()}@example.com",
                date_naissance='2000-01-01',
            )
        else:
            print(f"Updating existing member: {member.nom_prenom} -> {data['name']}")
        
        member.nom_prenom = data['name']
        if data['matricule']:
            member.matricule = data['matricule']
        member.niveau = data['niveau']
        member.telephone = data['telephone']
        member.poste_bureau = data['poste']
        member.member_type = 'bureau'
        member.is_active = True
        member.portfolio_enabled = True
        member.save()

    print("✅ Bureau Exécutif mis à jour avec succès!")

if __name__ == '__main__':
    update_bureau()
