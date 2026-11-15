from django.core.management.base import BaseCommand
from main.models import SponsorshipSession
from main.sponsorship_matching import run_sponsorship_matching

class Command(BaseCommand):
    help = "Exécute l'algorithme d'affectation automatique des parrains aux filleuls (max 2 filleuls par parrain, respect des paiements)."

    def add_arguments(self, parser):
        parser.add_argument('--session-id', type=int, help="ID de la session de parrainage")
        parser.add_argument('--all-statuses', action='store_true', help="Inclure les candidats non encore payés (simulation)")
        parser.add_argument('--dry-run', action='store_true', help="Simuler sans enregistrer les modifications")

    def handle(self, *args, **options):
        session_id = options.get('session_id')
        only_paid = not options.get('all_statuses', False)
        dry_run = options.get('dry_run', False)

        session = None
        if session_id:
            session = SponsorshipSession.objects.filter(pk=session_id).first()
        else:
            session = SponsorshipSession.objects.filter(is_active=True).first()

        self.stdout.write(self.style.NOTICE(f"Exécution de l'affectation automatique pour : {session} (Only Paid={only_paid}, Dry Run={dry_run})"))

        res = run_sponsorship_matching(session=session, only_paid=only_paid, dry_run=dry_run)
        if not res.get('success'):
            self.stdout.write(self.style.ERROR(f"Erreur : {res.get('error')}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Résultats :"))
        self.stdout.write(f" - Parrains disponibles : {res['mentors_available_count']}")
        self.stdout.write(f" - Filleuls traités : {res['mentees_processed_count']}")
        self.stdout.write(f" - Binômes créés : {res['matches_count']}")
        self.stdout.write(f" - Liste d'attente : {res['waiting_list_count']}")

