from django.db import migrations
import datetime
from decimal import Decimal

def populate_initial_data(apps, schema_editor):
    CofestiEdition = apps.get_model('main', 'CofestiEdition')
    CofestiCandidate = apps.get_model('main', 'CofestiCandidate')
    CofestiSportTournament = apps.get_model('main', 'CofestiSportTournament')
    CofestiPicnic = apps.get_model('main', 'CofestiPicnic')
    CofestiOrganizingMember = apps.get_model('main', 'CofestiOrganizingMember')
    Event = apps.get_model('main', 'Event')
    EventActivity = apps.get_model('main', 'EventActivity')
    SponsorshipSession = apps.get_model('main', 'SponsorshipSession')

    # 1. SponsorshipSession
    if not SponsorshipSession.objects.filter(is_active=True).exists():
        SponsorshipSession.objects.create(
            name="Session 2025/2026",
            is_active=True,
            start_date=datetime.date(2025, 10, 1),
            end_date=datetime.date(2026, 6, 30),
        )

    # 2. CofestiEdition 2026
    edition = CofestiEdition.objects.filter(year=2026).first()
    if not edition:
        edition = CofestiEdition.objects.create(
            year=2026,
            title="COFESTI 2026 — Festi-Noël du COM.S.AS",
            theme="Célébration, Excellence & Solidarité Estudiantine",
            description="Le grand festival festif et sportif de fin d'année du Département d'Informatique de l'Université de Yaoundé I.",
            start_date=datetime.date(2026, 12, 1),
            end_date=datetime.date(2026, 12, 23),
            location="Université de Yaoundé I",
            is_active=True,
            miss_master_active=True,
            miss_master_voting_open=True,
            sports_active=True,
            picnics_active=True,
            sponsorship_gala_active=True,
            vote_unit_price=100,
        )
    else:
        if not edition.is_active:
            edition.is_active = True
            edition.save()

    # 3. Tournaments
    tournaments_data = [
        ('football_m', "Tournoi Majeur de Football Masculin", Decimal('15000.00'), "Stade du Campus UY1", "5 joueurs de champ + remplaçants. Durée 2x25min. Ballon officiel fourni. Hymne officiel Before the Whistle diffusé à l'entrée des joueurs.", 1),
        ('football_f', "Tournoi Féminin de Football", Decimal('10000.00'), "Stade du Campus UY1", "Équipes de 5 joueuses. Matchs de 2x15min.", 2),
        ('basketball_m', "Tournoi 3x3 Basketball Masculin", Decimal('10000.00'), "Plateau Sportif UY1", "Règles FIBA 3x3. Équipes de 4 joueurs maximum (3 sur terrain + 1 remplaçant).", 3),
        ('basketball_f', "Tournoi 3x3 Basketball Féminin", Decimal('10000.00'), "Plateau Sportif UY1", "Règles FIBA 3x3.", 4),
        ('gaming_fifa', "Tournoi E-Sport EA Sports FC 25", Decimal('2000.00'), "Salle Multimédia COMSAS", "PlayStation 5. Matchs de 6 minutes. Phase de poules puis tableau à élimination directe.", 5),
        ('gaming_storm', "Tournoi E-Sport Naruto Shippuden UNS 4", Decimal('2000.00'), "Salle Multimédia COMSAS", "PlayStation 4 / 5. Format Versus 1v1 en 2 manches gagnantes.", 6),
        ('gaming_cod', "Tournoi E-Sport Call of Duty Mobile", Decimal('5000.00'), "Online / Espace Gaming", "Format Recherche & Destruction en équipes de 4 joueurs.", 7),
        ('strategy_chess', "Championnat d'Échecs Universitaire", Decimal('1000.00'), "Salle de Conférence L3", "Format Blitz 5min + 3sec par coup. Système suisse en 7 rondes.", 8),
    ]
    for cat, title, fee, loc, rules, order in tournaments_data:
        if not CofestiSportTournament.objects.filter(edition=edition, category=cat).exists():
            CofestiSportTournament.objects.create(
                edition=edition,
                category=cat,
                title=title,
                registration_fee=fee,
                location=loc,
                rules_summary=rules,
                is_open=True,
                order=order,
            )

    # 4. 5 Picnics
    picnics_data = [
        ("1er Pique-Nique : Lancement Festi-Noël & Projection Cinéma", "Jardin Botanique UY1", datetime.date(2026, 12, 5), datetime.date(2026, 12, 5), Decimal('3500.00'), "Ouverture officielle des réjouissances de fin d'année. Barbecue, jeux de détente et projection cinéma en plein air.", 1),
        ("2e Pique-Nique : Grillades, Karaoké & Jeux de Société", "Espace Vert Campus UY1", datetime.date(2026, 12, 9), datetime.date(2026, 12, 9), Decimal('3500.00'), "Détente conviviale, concours de chant et découverte des jeux de stratégie.", 2),
        ("3e Pique-Nique : Soirée Cinéma & Chill Geek", "Esplanade Informatique", datetime.date(2026, 12, 13), datetime.date(2026, 12, 13), Decimal('4000.00'), "Projection de blockbusters et discussion tech autour d'un grand buffet garni.", 3),
        ("4e Pique-Nique : Veillée Culturelle & Musique", "Jardin Botanique UY1", datetime.date(2026, 12, 17), datetime.date(2026, 12, 17), Decimal('4500.00'), "Contes traditionnels, performances acoustiques et douceurs de Noël.", 4),
        ("5e Pique-Nique : Grand Festin de Noël & Feu de Camp", "Campus Universitaire UY1", datetime.date(2026, 12, 21), datetime.date(2026, 12, 21), Decimal('5000.00'), "Clôture féerique des pique-niques avant la grande Soirée de Parrainage et Gala au Restaurant N°2.", 5),
    ]
    for theme, loc, pdate, cdate, price, desc, order in picnics_data:
        if not CofestiPicnic.objects.filter(edition=edition, order=order).exists():
            CofestiPicnic.objects.create(
                edition=edition,
                order=order,
                theme=theme,
                location=loc,
                picnic_date=pdate,
                cinema_date=cdate,
                price=price,
                description=desc,
                is_active=True,
            )

    # 5. Candidates
    candidates_data = [
        ('miss', 1, "Audrey Mengue", 20, "Licence 2 Informatique", "Génie Logiciel", "Passionnée par le design UI/UX et l'entrepreneuriat numérique."),
        ('miss', 2, "Brenda Kamdem", 21, "Licence 3 Informatique", "Data Science", "Dévouée à la vulgarisation des sciences auprès des jeunes filles."),
        ('miss', 3, "Cynthia Ngo", 22, "Master 1 Informatique", "Cybersécurité", "Auditrice de sécurité et engagée dans la vie associative du COM.S.AS."),
        ('master', 1, "Daniel Tchinda", 21, "Licence 3 Informatique", "Réseaux & Télécoms", "Développeur fullstack et passionné d'intelligence artificielle."),
        ('master', 2, "Eric Fotso", 22, "Master 1 Informatique", "Génie Logiciel", "Responsable projet étudiant et fervent défenseur de l'open source."),
        ('master', 3, "Franck Mbarga", 20, "Licence 2 Informatique", "Systèmes & Cloud", "Amateur d'architecture cloud et de compétitions sportives."),
        ('voice', 1, "Grace Ondoa", 19, "Licence 1 Informatique", "Informatique Générale", "Voix d'or du département, chanteuse gospel et acoustic soul."),
        ('voice', 2, "Hervé Biya", 21, "Licence 3 Informatique", "Génie Logiciel", "Auteur-compositeur et guitariste passionné de rythmes afro-jazz."),
    ]
    for ctype, num, name, age, level, spec, bio in candidates_data:
        if not CofestiCandidate.objects.filter(edition=edition, contest_type=ctype, number=num).exists():
            CofestiCandidate.objects.create(
                edition=edition,
                contest_type=ctype,
                number=num,
                name=name,
                age=age,
                level=level,
                specialty=spec,
                bio=bio,
                is_approved=True,
                votes_count=10 * num,
            )

    # 6. Committee Members (Décision 095)
    members_data = [
        ('bloc1', "Président Général COFESTI", "Patrice Neussi", "699000001", 1),
        ('bloc1', "Secrétaire Général", "Marcelle Talla", "699000002", 2),
        ('bloc1', "Trésorier Général", "Arnaud Essomba", "699000003", 3),
        ('bloc1', "Coordonnateur Général Logistique", "Stéphane Ndongo", "699000004", 4),
        ('bloc2', "Commission Sport & Tournois", "Capitaine Eric Kamdem", "699000005", 5),
        ('bloc2', "Commission Concours Miss & Master", "Vanessa Mballa", "699000006", 6),
        ('bloc2', "Commission Pique-Niques & Cinéma", "Kevin Obama", "699000007", 7),
        ('bloc2', "Commission Parrainage & Soirée Resto N°2", "Sandra Bih", "699000008", 8),
    ]
    for bloc, role, name, phone, order in members_data:
        if not CofestiOrganizingMember.objects.filter(edition=edition, name=name).exists():
            CofestiOrganizingMember.objects.create(
                edition=edition,
                order=order,
                bloc=bloc,
                role=role,
                name=name,
                phone=phone,
            )

    # 7. Activities for active events
    for ev in Event.objects.filter(is_active=True)[:3]:
        slug_atelier = f"atelier-cyber-{ev.pk}"
        if not EventActivity.objects.filter(slug=slug_atelier).exists():
            EventActivity.objects.create(
                slug=slug_atelier,
                event=ev,
                title="Atelier Cybersécurité & Reverse Engineering",
                activity_type='individual',
                description="Pratique guidée des techniques d'analyse de vulnérabilités et sécurité offensive.",
                date_activity=ev.date_event,
                location=ev.location,
                price=Decimal('0.00'),
                max_participants=40,
                rules="Venir avec son PC portable sous Linux ou machine virtuelle Kali.",
                is_active=True,
            )
        slug_foot = f"tournoi-foot-{ev.pk}"
        if not EventActivity.objects.filter(slug=slug_foot).exists():
            EventActivity.objects.create(
                slug=slug_foot,
                event=ev,
                title="Tournoi Inter-Promotions de Football",
                activity_type='team',
                min_team_size=5,
                max_team_size=8,
                description="Grande compétition de football à 5 entre les promotions du département.",
                date_activity=ev.date_event,
                location="Stade du Campus UY1",
                price=Decimal('15000.00'),
                max_participants=8,
                rules="5 joueurs de champ + 3 remplaçants maximum. Protège-tibias obligatoires.",
                is_active=True,
            )
        slug_esport = f"tournoi-esport-{ev.pk}"
        if not EventActivity.objects.filter(slug=slug_esport).exists():
            EventActivity.objects.create(
                slug=slug_esport,
                event=ev,
                title="Championnat E-Sport FC 25 & Naruto",
                activity_type='gaming',
                game_title="EA Sports FC 25 & Naruto Storm 4",
                platform="PlayStation 5",
                description="Compétition de jeux vidéo sur consoles de salon avec retransmission sur écran géant.",
                date_activity=ev.date_event,
                location="Salle Multimédia COMSAS",
                price=Decimal('2000.00'),
                max_participants=32,
                rules="Matchs de 6 minutes en 1v1. Manettes officielles fournies.",
                is_active=True,
            )

def rollback_initial_data(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_eventactivity_mentee_bio_mentee_photo_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_initial_data, rollback_initial_data),
    ]
