"""
Service Freemopay pour Mobile Money Afrique
Version Production — comsas-uy1.com
"""
import requests
import json
import uuid
import base64
import logging
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import Vote, Candidate

logger = logging.getLogger(__name__)

class FreemopayPaymentProcessor:
    """
    Intégration production avec l'API Freemopay v2
    Système de dépôt suivi d'un retrait automatique
    """
    
    def __init__(self):
        # Configuration Freemopay Production
        self.api_key = getattr(settings, 'FREEMOPAY_APP_KEY', '69997c27-8def-464a-8934-5d9ed0a85709')
        self.secret_key = getattr(settings, 'FREEMOPAY_SECRET_KEY', '1DwoptA4kDjApej9OeWp')
        self.base_url = getattr(settings, 'FREEMOPAY_BASE_URL', 'https://api-v2.freemopay.com')
        
        # Votre numéro personnel pour les retraits automatiques
        self.personal_withdrawal_number = getattr(settings, 'FREEMOPAY_WITHDRAWAL_NUMBER', '237650970526')
        
        # Commission Freemopay (3%)
        self.freemopay_commission = 0.03
        
        # Configuration des authentifications
        self.auth_string = base64.b64encode(f"{self.api_key}:{self.secret_key}".encode()).decode()
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.auth_string}'
        })

    def calculate_amounts(self, gross_amount):
        """Calcule les montants après commission Freemopay"""
        freemopay_fee = gross_amount * self.freemopay_commission
        net_amount = gross_amount - freemopay_fee
        return {
            'gross_amount': gross_amount,
            'freemopay_fee': freemopay_fee,
            'net_amount': net_amount
        }

    def process_vote_payment(self, vote_instance):
        """Traite le paiement pour un vote via Freemopay (DEPOSIT)"""
        try:
            payer_phone = vote_instance.voter_phone.replace('+', '').replace(' ', '')
            if not payer_phone.startswith('237') and len(payer_phone) == 9:
                payer_phone = f"237{payer_phone}"
                
            payment_data = {
                "payer": payer_phone,
                "amount": str(int(vote_instance.amount)),
                "externalId": str(vote_instance.transaction_id),
                "description": f"Vote {vote_instance.candidate.name} - {vote_instance.vote_count} voix",
                "callback": self._get_webhook_url()
            }
            
            logger.info(f"[FREEMOPAY] Initiation paiement DEPOSIT: {vote_instance.transaction_id} | Phone: {payer_phone} | Montant: {payment_data['amount']}")
            
            response = self.session.post(
                f"{self.base_url}/api/v2/payment",
                json=payment_data,
                timeout=30
            )
            
            logger.info(f"[FREEMOPAY] Réponse HTTP: {response.status_code} | Body: {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') in ['SUCCESS', 'CREATED']:
                    vote_instance.payment_reference = data.get('reference', '')
                    vote_instance.status = 'processing'
                    vote_instance.save()
                    return {
                        'success': True,
                        'reference': data.get('reference'),
                        'message': data.get('message', 'Paiement initié'),
                        'status': data.get('status')
                    }
                else:
                    logger.error(f"[FREEMOPAY] Statut inattendu: {data.get('status')} | Message: {data.get('message')}")
                    return {'success': False, 'error': data.get('message', 'Échec initiation')}
            else:
                logger.error(f"[FREEMOPAY] Erreur HTTP {response.status_code}: {response.text[:300]}")
                return {'success': False, 'error': f'Erreur HTTP {response.status_code}: {response.text[:200]}'}
                
        except Exception as e:
            logger.error(f"[FREEMOPAY] Exception process_vote: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def process_activity_payment(self, app_instance):
        """Traite le paiement pour une inscription à une activité d'événement payante"""
        try:
            payer_phone = app_instance.phone.replace('+', '').replace(' ', '')
            if not payer_phone.startswith('237') and len(payer_phone) == 9:
                payer_phone = f"237{payer_phone}"
                
            payment_data = {
                "payer": payer_phone,
                "amount": str(int(app_instance.amount)),
                "externalId": str(app_instance.transaction_id),
                "description": f"Inscription {app_instance.activity.title} - {app_instance.full_name}",
                "callback": self._get_webhook_url()
            }
            
            logger.info(f"[FREEMOPAY] Initiation paiement Activité: {app_instance.transaction_id} | Phone: {payer_phone} | Montant: {payment_data['amount']}")
            
            response = self.session.post(
                f"{self.base_url}/api/v2/payment",
                json=payment_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') in ['SUCCESS', 'CREATED']:
                    app_instance.payment_reference = data.get('reference', '')
                    app_instance.save(update_fields=['payment_reference'])
                    return {
                        'success': True,
                        'reference': data.get('reference'),
                        'message': data.get('message', 'Paiement initié avec succès. Composez votre code PIN.'),
                        'status': data.get('status')
                    }
                else:
                    return {'success': False, 'error': data.get('message', 'Échec initiation')}
            else:
                return {'success': False, 'error': f'Erreur HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"[FREEMOPAY] Exception process_activity_payment: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def confirm_activity_payment(self, app_instance):
        """Valide définitivement le paiement et confirme la candidature"""
        try:
            if app_instance.is_paid:
                return {'success': True, 'message': 'Déjà validé'}
            app_instance.is_paid = True
            app_instance.status = 'confirmed'
            app_instance.save(update_fields=['is_paid', 'status'])
            logger.info(f"[FREEMOPAY] Candidature confirmée et payée: {app_instance.transaction_id}")
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def process_sponsorship_payment(self, participant, phone_override=None):
        """Traite le paiement Freemopay Mobile Money pour une inscription au parrainage (Parrain ou Filleul)"""
        try:
            raw_phone = phone_override or participant.phone
            payer_phone = raw_phone.replace('+', '').replace(' ', '')
            if not payer_phone.startswith('237') and len(payer_phone) == 9:
                payer_phone = f"237{payer_phone}"
                
            is_mentor = hasattr(participant, 'profession')
            role_label = "Parrain" if is_mentor else "Filleul"
            
            payment_data = {
                "payer": payer_phone,
                "amount": str(int(participant.amount)),
                "externalId": str(participant.transaction_id),
                "description": f"Pass Soirée Parrainage {role_label} - {participant.first_name} {participant.last_name}",
                "callback": self._get_webhook_url()
            }
            
            logger.info(f"[FREEMOPAY] Initiation paiement Parrainage: {participant.transaction_id} | Phone: {payer_phone} | Montant: {payment_data['amount']}")
            
            response = self.session.post(
                f"{self.base_url}/api/v2/payment",
                json=payment_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') in ['SUCCESS', 'CREATED']:
                    participant.payment_reference = data.get('reference', '')
                    participant.payment_status = 'initiated'
                    participant.save(update_fields=['payment_reference', 'payment_status'])
                    return {
                        'success': True,
                        'reference': data.get('reference'),
                        'message': data.get('message', 'Demande de paiement envoyée sur votre téléphone. Composez votre code PIN.'),
                        'status': data.get('status')
                    }
                else:
                    return {'success': False, 'error': data.get('message', 'Échec de connexion')}
            else:
                return {'success': False, 'error': f'Erreur HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"[FREEMOPAY] Exception process_sponsorship_payment: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def confirm_sponsorship_payment(self, participant, payment_ref=None):
        """Valide définitivement le paiement du parrainage, génère le pass PDF officiel et le QR code (Idempotent)"""
        try:
            if participant.is_paid:
                return {'success': True, 'message': 'Paiement déjà validé'}
                
            from .utils import generate_sponsorship_pass
            
            participant.is_paid = True
            participant.payment_status = 'confirmed'
            participant.paid_at = timezone.now()
            if payment_ref:
                participant.payment_reference = payment_ref
            if hasattr(participant, 'status') and participant.status == 'pending':
                participant.status = 'approved' if hasattr(participant, 'profession') else 'paid'
            participant.save()
            
            # Générer le pass soirée avec QR code
            try:
                generate_sponsorship_pass(participant)
            except Exception as e:
                logger.error(f"[SPONSORSHIP PASS ERROR] {e}")
                
            return {'success': True, 'message': 'Paiement validé avec succès et Pass généré.'}
        except Exception as e:
            logger.error(f"[FREEMOPAY] Exception confirm_sponsorship_payment: {e}")
            return {'success': False, 'error': str(e)}

    def initiate_automatic_withdrawal(self, vote_instance):
        """Initie automatiquement un retrait vers le compte administrateur"""
        try:
            amounts = self.calculate_amounts(float(vote_instance.amount))
            withdrawal_amount = amounts['net_amount']
            
            # Montant minimum 100 FCFA
            if withdrawal_amount < 100:
                withdrawal_amount = 100
            
            withdrawal_external_id = f"WD-{vote_instance.transaction_id}"
            
            withdrawal_data = {
                "amount": int(withdrawal_amount),
                "receiver": str(self.personal_withdrawal_number),
                "callback": self._get_webhook_url(),
                "externalId": withdrawal_external_id
            }
            
            logger.info(f"[FREEMOPAY] Retrait automatique: {withdrawal_external_id}")
            
            response = self.session.post(
                f"{self.base_url}/api/v2/payment/direct-withdraw",
                json=withdrawal_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'SUCCESS':
                    vote_instance.withdrawal_reference = data.get('reference', '')
                    vote_instance.save()
                    return {'success': True, 'reference': data.get('reference')}
            return {'success': False, 'error': 'Échec retrait'}
                    
        except Exception as e:
            logger.error(f"[FREEMOPAY] Erreur retrait: {e}")
            return {'success': False, 'error': str(e)}

    def verify_payment_status(self, vote_instance):
        """Vérifie le statut d'un paiement via l'API"""
        try:
            if not vote_instance.payment_reference:
                return {'success': False, 'error': 'Référence manquante'}
            
            response = self.session.get(
                f"{self.base_url}/api/v2/payment/{vote_instance.payment_reference}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                freemopay_status = data.get('status', 'PENDING')
                
                status_map = {'SUCCESS': 'completed', 'FAILED': 'failed', 'CREATED': 'processing'}
                internal_status = status_map.get(freemopay_status, 'processing')
                
                return {
                    'success': True,
                    'status': internal_status,
                    'freemopay_status': freemopay_status
                }
            return {'success': False, 'error': 'Erreur vérification'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def confirm_payment(self, vote_instance):
        """Confirme un paiement et déclenche le retrait"""
        try:
            if vote_instance.status == 'completed':
                return {'success': True, 'message': 'Déjà confirmé'}

            vote_instance.status = 'completed'
            vote_instance.completed_at = timezone.now()
            vote_instance.save()
            
            # Mise à jour du candidat
            candidate = vote_instance.candidate
            candidate.votes_count += vote_instance.vote_count
            candidate.total_revenue += vote_instance.amount
            candidate.save()
            
            logger.info(f"[FREEMOPAY] Vote confirmé pour {candidate.name}")
            
            # Retrait auto
            self.initiate_automatic_withdrawal(vote_instance)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_webhook_url(self):
        site_url = getattr(settings, 'SITE_URL', 'https://comsas-uy1.com')
        return f"{site_url}/api/payments/webhook/freemopay/"


class FreemopayWebhookHandler:
    """Gestionnaire des webhooks Freemopay"""
    
    @staticmethod
    def handle_webhook(request_body):
        try:
            data = json.loads(request_body)
            logger.info(f"[FREEMOPAY WEBHOOK] Data: {data}")
            
            status = data.get('status')
            reference = data.get('reference')
            external_id = data.get('externalId')
            transaction_type = data.get('transactionType')
            
            if not external_id:
                return {'success': False, 'error': 'No externalId'}

            # Dépôt (Vote ou Don)
            if transaction_type == 'DEPOSIT':
                try:
                    if external_id.startswith('SPONSORPAY'):
                        from .models import Mentor, Mentee
                        from .utils import generate_sponsorship_pass
                        participant = Mentor.objects.filter(transaction_id=external_id).first()
                        if not participant:
                            participant = Mentee.objects.filter(transaction_id=external_id).first()
                        if participant:
                            if status in ('SUCCESS', 'COMPLETED', 'PAID', 'SUCCESSFUL'):
                                if not participant.is_paid:
                                    participant.is_paid = True
                                    participant.payment_status = 'confirmed'
                                    participant.paid_at = timezone.now()
                                    if hasattr(participant, 'status') and participant.status == 'pending':
                                        participant.status = 'approved' if isinstance(participant, Mentor) else 'paid'
                                    participant.save()
                                    try:
                                        generate_sponsorship_pass(participant)
                                    except Exception as e:
                                        logger.error(f"[SPONSORSHIP PASS ERROR] {e}")
                            elif status in ('FAILED', 'FAILURE', 'ERROR', 'EXPIRED'):
                                participant.payment_status = 'failed'
                                participant.save(update_fields=['payment_status'])
                        return {'success': True}
                    elif external_id.startswith('ACTIVITYPAY'):
                        from .models import EventActivityApplication
                        app = EventActivityApplication.objects.get(transaction_id=external_id)
                        if status in ('SUCCESS', 'COMPLETED', 'PAID', 'SUCCESSFUL'):
                            processor = FreemopayPaymentProcessor()
                            processor.confirm_activity_payment(app)
                        elif status in ('FAILED', 'FAILURE', 'ERROR', 'EXPIRED'):
                            app.status = 'cancelled'
                            app.save(update_fields=['status'])
                        return {'success': True}
                    elif external_id.startswith('COFESTIVOTE'):
                        from .models import CofestiVote
                        vote = CofestiVote.objects.get(transaction_id=external_id)
                        if status == 'SUCCESS':
                            processor = FreemopayPaymentProcessor()
                            processor.confirm_payment(vote)
                        elif status == 'FAILED':
                            vote.status = 'failed'
                            vote.save()
                        return {'success': True}
                    elif external_id.startswith('JUINVOTE'):
                        from .models import JUINVote
                        vote = JUINVote.objects.get(transaction_id=external_id)
                        if status == 'SUCCESS':
                            processor = FreemopayPaymentProcessor()
                            processor.confirm_payment(vote)
                        elif status == 'FAILED':
                            vote.status = 'failed'
                            vote.save()
                        return {'success': True}
                    elif external_id.startswith('JUINDON'):
                        from .models import JUINDonation
                        donation = JUINDonation.objects.get(external_id=external_id)
                        if status in ('SUCCESS', 'COMPLETED', 'PAID', 'SUCCESSFUL'):
                            donation.is_confirmed = True
                            donation.payment_status = 'completed'
                            donation.save()
                        elif status in ('FAILED', 'FAILURE', 'ERROR', 'EXPIRED'):
                            donation.payment_status = 'failed'
                            donation.save()
                        return {'success': True}
                    elif external_id.startswith('COMSASDON'):
                        from .models import Donation
                        donation = Donation.objects.get(external_id=external_id)
                        if status in ('SUCCESS', 'COMPLETED', 'PAID', 'SUCCESSFUL'):
                            donation.is_confirmed = True
                            donation.payment_status = 'completed'
                            donation.completed_at = timezone.now()
                            donation.save()
                        elif status in ('FAILED', 'FAILURE', 'ERROR', 'EXPIRED'):
                            donation.payment_status = 'failed'
                            donation.save()
                        return {'success': True}
                    else:
                        vote = Vote.objects.get(transaction_id=external_id)
                        if status == 'SUCCESS':
                            processor = FreemopayPaymentProcessor()
                            processor.confirm_payment(vote)
                        elif status == 'FAILED':
                            vote.status = 'failed'
                            vote.save()
                        return {'success': True}
                except Exception as e:
                    return {'success': False, 'error': f'Objet non trouvé ou erreur: {str(e)}'}
        except Exception as e:
            logger.error(f"[FREEMOPAY WEBHOOK] Error: {e}")
            return {'success': False, 'error': str(e)}

# Maintenance de la compatibilité avec l'ancien code si nécessaire
class FreemopayService(FreemopayPaymentProcessor):
    def initiate_payment(self, amount, phone_number, description="Paiement", external_id=None):
        """Initie un paiement général (Dons, Sponsors)"""
        if not external_id:
            import uuid
            external_id = str(uuid.uuid4())
            
        try:
            payer_phone = phone_number.replace('+', '').replace(' ', '')
            if not payer_phone.startswith('237') and len(payer_phone) == 9:
                payer_phone = f"237{payer_phone}"

            payment_data = {
                "payer": payer_phone,
                "amount": str(int(amount)),
                "externalId": external_id,
                "description": description,
                "callback": self._get_webhook_url()
            }
            
            logger.info(f"[FREEMOPAY] Initiation paiement GÉNÉRAL: {external_id}")
            
            response = self.session.post(
                f"{self.base_url}/api/v2/payment",
                json=payment_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') in ['SUCCESS', 'CREATED', 'PAID']:
                    # Instructions adaptées à l'opérateur camerounais
                    instructions = 'Veuillez valider le débit sur votre téléphone portable.'
                    if any(payer_phone.startswith(p) for p in ['23767', '23768', '237650', '237651', '237652', '237653', '237654']):
                        instructions = "Composez *126# ou validez l'invite USSD reçue sur votre téléphone avec votre code secret MTN."
                    elif any(payer_phone.startswith(p) for p in ['23769', '237655', '237656', '237657', '237658', '237659']):
                        instructions = "Composez #150*50# ou validez le message reçu sur votre téléphone avec votre code secret Orange."

                    return {
                        'success': True,
                        'reference': data.get('reference'),
                        'message': data.get('message', 'Paiement initié'),
                        'instructions': instructions,
                        'status': data.get('status')
                    }
                else:
                    return {'success': False, 'error': data.get('message', 'Échec initiation')}
            else:
                try:
                    err_json = response.json()
                    err_msg = err_json.get('message') or err_json.get('error') or f'Erreur HTTP {response.status_code}'
                    if isinstance(err_msg, dict):
                        err_msg = err_msg.get('fr') or err_msg.get('en') or str(err_msg)
                except Exception:
                    err_msg = f'Erreur HTTP {response.status_code}'
                return {'success': False, 'error': err_msg}
                
        except Exception as e:
            logger.error(f"[FREEMOPAY] Erreur initiate_payment: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def translate_error_message(raw_msg):
        """Traduit les erreurs techniques Freemopay et opérateurs en messages conviviaux pour l'utilisateur"""
        if not raw_msg:
            return "La transaction n'a pas pu aboutir. Veuillez vérifier votre compte et réessayer."
        
        msg_str = str(raw_msg)
        msg_lower = msg_str.lower()

        # Solde insuffisant
        if any(k in msg_lower for k in [
            'low_balance', 'insufficient_balance', 'solde insuffisant', 
            'funds', 'solde de votre compte', 'solde bas', 'solde faible'
        ]):
            return "Solde insuffisant sur votre compte Mobile Money. Veuillez recharger votre compte ou choisir un montant inférieur."

        # Code PIN faux
        if any(k in msg_lower for k in [
            'invalid pin', 'wrong pin', 'pin incorrect', 'code secret', 'code pin', 'bad pin', 'mot de passe incorrect'
        ]):
            return "Code PIN secret incorrect. Veuillez réessayer en composant votre code secret exact."

        # Annulation / Rejet
        if any(k in msg_lower for k in [
            'user_cancelled', 'user_rejected', 'annulé par', 'annule par', 
            'transaction_cancelled', 'refusé', 'refuse', 'cancelled', 'canceled', 'rejected'
        ]):
            return "La transaction a été refusée ou annulée sur votre téléphone."

        # Délai dépassé / Timeout
        if any(k in msg_lower for k in [
            'timeout', 'expired', 'expire', 'délai', 'delai', 'temps écoulé', 'temps ecoule'
        ]):
            return "Le délai de confirmation a expiré. Veuillez relancer le don et valider promptement l'invite USSD sur votre écran."

        # Plafond atteint
        if any(k in msg_lower for k in [
            'limit_reached', 'plafond', 'max limit', 'limite atteinte', 'quota'
        ]):
            return "Le plafond journalier ou mensuel autorisé sur votre compte Mobile Money est atteint."

        # Numéro invalide ou non enregistré
        if any(k in msg_lower for k in [
            'subscriber not found', 'subscriber_not_found', 'not registered', 
            'numéro non enregistré', 'numero non enregistre', 'compte inexistant', 'not allowed'
        ]):
            return "Ce numéro n'est pas activé pour le service Mobile Money auprès de l'opérateur."

        # Indisponibilité opérateur
        if any(k in msg_lower for k in [
            'unavailable', 'indisponible', 'down', 'maintenance', 'temporarily'
        ]):
            return "Le service de l'opérateur (MTN / Orange) est momentanément indisponible. Veuillez réessayer dans quelques minutes."

        return msg_str

    def check_payment_status(self, reference):
        try:
            response = self.session.get(
                f"{self.base_url}/api/v2/payment/{reference}",
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                raw_status = data.get('status', 'PENDING')
                raw_reason = data.get('reason') or data.get('message') or ''
                return {
                    'success': True,
                    'status': raw_status,
                    'raw_reason': raw_reason,
                    'reason': self.translate_error_message(raw_reason),
                    'data': data
                }
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_webhook_url(self):
        """Retourne l'URL du webhook de production"""
        return self._get_parent_webhook_url()

    def _get_parent_webhook_url(self):
        site_url = getattr(settings, 'SITE_URL', 'https://www.comsas-uy1.com')
        return f"{site_url}/api/payments/webhook/freemopay/"
