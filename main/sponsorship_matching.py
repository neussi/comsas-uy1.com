"""
Algorithme d'affectation automatique intelligente des Parrains et Filleuls COMS.A.S
Respecte la contrainte stricte de maximum 2 filleuls par parrain,
gère la liste d'attente, l'idempotence et les scores de compatibilité multi-critères.
"""

import re
from django.utils import timezone
from django.db import transaction
from .models import Mentor, Mentee, Match, SponsorshipSession


def clean_tokens(text):
    """Extrait une liste de mots-clés normalisés depuis un texte"""
    if not text:
        return set()
    cleaned = re.sub(r'[^\w\s]', ' ', str(text).lower())
    stop_words = {'de', 'la', 'le', 'et', 'un', 'une', 'des', 'pour', 'dans', 'en', 'avec', 'qui', 'sur', 'par', 'les', 'au', 'aux', 'mon', 'son'}
    tokens = {t.strip() for t in cleaned.split() if len(t.strip()) > 2 and t.strip() not in stop_words}
    return tokens


def calculate_compatibility_score(mentor, mentee):
    """
    Calcule le score de compatibilité (0 à 100) entre un parrain et un filleul.
    
    1. Filière & Option (30 pts max)
    2. Compétences & Aspirations techniques (35 pts max)
    3. Hiérarchie académique / Cycle d'études (20 pts max)
    4. Type de parrain souhaité & Motivations (15 pts max)
    """
    score = 0.0

    # --- 1. FILIÈRE & OPTION (30 pts) ---
    mentor_filiere = (mentor.filiere_option or '').lower().strip()
    mentee_filiere = (mentee.filiere_option or '').lower().strip()
    mentor_spec = (mentor.specialty or '').lower()
    mentee_spec = (mentee.desired_specialty or '').lower()

    if mentor_filiere and mentee_filiere and (mentor_filiere in mentee_filiere or mentee_filiere in mentor_filiere):
        score += 30.0
    elif mentor_spec and mentee_spec and (mentor_spec in mentee_spec or mentee_spec in mentor_spec):
        score += 26.0
    else:
        # Correspondance partielle par mots-clés
        m_tokens = clean_tokens(mentor_filiere + " " + mentor_spec)
        f_tokens = clean_tokens(mentee_filiere + " " + mentee_spec)
        common = m_tokens.intersection(f_tokens)
        if common:
            score += min(22.0, len(common) * 10.0)
        else:
            score += 10.0  # Base département informatique

    # --- 2. COMPÉTENCES & ASPIRATIONS (35 pts) ---
    # Récupérer les compétences du parrain avec pondération selon son niveau
    skills_scores = {}
    if mentor.skills_with_levels and isinstance(mentor.skills_with_levels, list):
        level_multipliers = {
            'expert': 1.0,
            'avancé': 0.85,
            'avance': 0.85,
            'intermédiaire': 0.65,
            'intermediaire': 0.65,
            'débutant': 0.4,
            'debutant': 0.4
        }
        for item in mentor.skills_with_levels:
            if isinstance(item, dict):
                s_name = str(item.get('skill', '')).lower().strip()
                s_lvl = str(item.get('level', 'intermédiaire')).lower().strip()
                mult = level_multipliers.get(s_lvl, 0.65)
                skills_scores[s_name] = mult
    
    # Compléter avec expertise_domains
    exp_domains = clean_tokens(mentor.expertise_domains)
    for d in exp_domains:
        if d not in skills_scores:
            skills_scores[d] = 0.7

    # Cibles du filleul
    mentee_targets = clean_tokens(
        f"{mentee.skills_to_acquire} {mentee.desired_specialty} {mentee.professional_domains} {mentee.competencies}"
    )

    skill_points = 0.0
    matched_skills = []
    for skill_name, multiplier in skills_scores.items():
        s_tokens = clean_tokens(skill_name)
        if s_tokens.intersection(mentee_targets):
            matched_skills.append(skill_name)
            skill_points += 9.0 * multiplier

    score += min(35.0, max(8.0, skill_points))

    # --- 3. CYCLE & NIVEAU D'ÉTUDES (20 pts) ---
    m_level = (mentor.level or '').upper()
    f_level = (mentee.level or '').upper()
    m_cycle = (mentor.cycle or '').lower()
    f_cycle = (mentee.cycle or '').lower()

    if m_cycle == 'professionnel' or 'ALUMNI' in m_level:
        # Professionnel / Alumni est le match idéal pour tous
        score += 20.0
    elif 'MIS' in m_level or m_cycle == 'mis':
        # Étudiants de MIS en parrains
        if 'MIS' in f_level or f_cycle == 'mis':
            score += 20.0  # Mentorat spécialisé MIS
        elif 'L' in f_level:
            score += 18.0  # Aîné MIS guidant un étudiant de Licence
        else:
            score += 15.0
    elif 'M2' in m_level or 'M1' in m_level or m_cycle == 'master':
        if 'L' in f_level or f_cycle == 'licence':
            score += 19.0
        elif 'MIS' in f_level:
            score += 17.0
        else:
            score += 14.0
    elif 'L3' in m_level:
        if f_level in ('L1', 'ICT-L1'):
            score += 18.0
        elif f_level in ('L2', 'ICT-L2'):
            score += 15.0
        else:
            score += 10.0
    else:
        score += 12.0

    # --- 4. DESCRIPTION DU TYPE DE PARRAIN SOUHAITÉ (15 pts) ---
    desired_text = clean_tokens(f"{mentee.desired_mentor_type} {mentee.bio}")
    mentor_profile = clean_tokens(f"{mentor.profession} {mentor.company} {mentor.bio} {mentor.expertise_domains}")
    
    profile_common = desired_text.intersection(mentor_profile)
    if profile_common:
        score += min(15.0, len(profile_common) * 4.0 + 4.0)
    else:
        score += 6.0

    return round(min(100.0, max(15.0, score)), 1)


def run_sponsorship_matching(session=None, max_per_mentor=2, only_paid=True, dry_run=False):
    """
    Exécute l'algorithme d'affectation automatique.
    
    Règles :
    - Un parrain a AU PLUS 2 filleuls (ou max_per_mentor)
    - Affecte uniquement les inscrits qui ont payé (si only_paid=True)
    - Gère la liste d'attente s'il y a plus de filleuls que de parrains disponibles
    - Relançable sans dupliquer les affectations existantes
    """
    if not session:
        session = SponsorshipSession.objects.filter(is_active=True).first()
        if not session:
            session = SponsorshipSession.objects.order_by('-start_date').first()

    if not session:
        return {
            'success': False,
            'error': "Aucune session de parrainage active trouvée."
        }

    # 1. Sélection des Parrains éligibles
    mentor_qs = Mentor.objects.filter(session=session)
    if only_paid:
        mentor_qs = mentor_qs.filter(is_paid=True)
    else:
        mentor_qs = mentor_qs.filter(status__in=['pending', 'approved'])

    # 2. Sélection des Filleuls éligibles et non encore assignés
    mentee_qs = Mentee.objects.filter(session=session)
    if only_paid:
        mentee_qs = mentee_qs.filter(is_paid=True)

    # Exclure les filleuls qui ont déjà un Match actif
    already_matched_ids = Match.objects.filter(session=session, is_active=True).values_list('mentee_id', flat=True)
    unmatched_mentees = list(mentee_qs.exclude(id__in=already_matched_ids))

    # Calcul de la capacité restante par parrain
    available_mentors = []
    mentor_capacities = {}

    for mentor in mentor_qs:
        current_active = Match.objects.filter(mentor=mentor, is_active=True).count()
        cap = max(0, min(mentor.max_mentees or max_per_mentor, max_per_mentor) - current_active)
        if cap > 0:
            available_mentors.append(mentor)
            mentor_capacities[mentor.id] = cap

    # 3. Calcul de tous les couples possibles avec leur score
    candidate_pairs = []
    for mentee in unmatched_mentees:
        for mentor in available_mentors:
            score = calculate_compatibility_score(mentor, mentee)
            candidate_pairs.append({
                'mentor': mentor,
                'mentee': mentee,
                'score': score
            })

    # Tri par score décroissant (les binômes les plus compatibles d'abord)
    candidate_pairs.sort(key=lambda x: x['score'], reverse=True)

    matches_to_create = []
    assigned_mentees = set()

    for pair in candidate_pairs:
        mentor = pair['mentor']
        mentee = pair['mentee']
        score = pair['score']

        if mentee.id in assigned_mentees:
            continue
        if mentor_capacities.get(mentor.id, 0) <= 0:
            continue

        # Assigner
        matches_to_create.append({
            'mentor': mentor,
            'mentee': mentee,
            'score': score
        })
        assigned_mentees.add(mentee.id)
        mentor_capacities[mentor.id] -= 1

    # Filleuls restant sans parrain disponible -> Liste d'attente
    waiting_mentees = [m for m in unmatched_mentees if m.id not in assigned_mentees]

    if not dry_run:
        with transaction.atomic():
            created_instances = []
            for item in matches_to_create:
                match_obj, created = Match.objects.update_or_create(
                    mentor=item['mentor'],
                    mentee=item['mentee'],
                    defaults={
                        'session': session,
                        'compatibility_score': item['score'],
                        'is_active': True,
                        'is_confirmed_by_admin': True,
                        'match_notes': f"Affectation automatique intelligente (Score de compatibilité : {item['score']}%)",
                        'notified_at': timezone.now()
                    }
                )
                # Mettre à jour le statut du filleul
                item['mentee'].status = 'matched'
                item['mentee'].save(update_fields=['status'])

                # Mettre à jour le statut du parrain
                item['mentor'].status = 'approved'
                item['mentor'].save(update_fields=['status'])

                created_instances.append(match_obj)

            # Placer les restants en liste d'attente
            for wm in waiting_mentees:
                if wm.status != 'matched':
                    wm.status = 'waiting_list'
                    wm.save(update_fields=['status'])

    return {
        'success': True,
        'session': session.name,
        'mentors_available_count': len(available_mentors),
        'mentees_processed_count': len(unmatched_mentees),
        'matches_count': len(matches_to_create),
        'waiting_list_count': len(waiting_mentees),
        'matches': matches_to_create,
        'waiting_mentees': waiting_mentees,
        'dry_run': dry_run
    }

