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
        self.api_key = getattr(settings, 'FREEMOPAY_APP_KEY', '961bfd39-e0cd-4c02-9a99-23e46d74d265')
        self.secret_key = getattr(settings, 'FREEMOPAY_SECRET_KEY', '3GNjRDgOe8vbqjIddpqE')
        self.base_url = "https://api-v2.freemopay.com"
        
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
            
            logger.info(f"[FREEMOPAY] Initiation paiement DEPOSIT: {vote_instance.transaction_id}")
            
            response = self.session.post(
                f"{self.base_url}/api/v2/payment",
                json=payment_data,
                timeout=30
            )
            
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
                    return {'success': False, 'error': data.get('message', 'Échec initiation')}
            else:
                return {'success': False, 'error': f'Erreur HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"[FREEMOPAY] Erreur process_vote: {e}")
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
                    if external_id.startswith('JUINVOTE'):
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
                    return {
                        'success': True,
                        'reference': data.get('reference'),
                        'message': data.get('message', 'Paiement initié'),
                        'instructions': data.get('instructions', 'Veuillez valider sur votre téléphone.'),
                        'status': data.get('status')
                    }
                else:
                    return {'success': False, 'error': data.get('message', 'Échec initiation')}
            else:
                return {'success': False, 'error': f'Erreur HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"[FREEMOPAY] Erreur initiate_payment: {e}")
            return {'success': False, 'error': str(e)}

    def check_payment_status(self, reference):
        try:
            response = self.session.get(
                f"{self.base_url}/api/v2/payment/{reference}",
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data.get('status', 'PENDING'),
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
