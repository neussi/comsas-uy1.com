"""
Service Propenta Pay (API V2) pour Mobile Money Cameroun (Orange Money & MTN MoMo)
Remplacement officiel de Freemopay — comsas-uy1.com
"""
import requests
import json
import uuid
import time
import hmac
import hashlib
import logging
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import Vote, JUINVote, CofestiVote, Candidate, JUINCandidate, CofestiCandidate, EventActivityApplication, Mentor, Mentee, Donation, JUINDonation

logger = logging.getLogger(__name__)


class PropentaPayAPIClient:
    """
    Client HTTP pour l'API Propenta Pay V2
    Gère l'authentification Bearer (POST /auth/token) et la signature HMAC-SHA256 (X-Signature)
    """

    _cached_token = None
    _token_expires_at = 0

    def __init__(self):
        self.client_id = getattr(settings, 'PROPENTA_CLIENT_ID', '') or os.environ.get('PROPENTA_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'PROPENTA_CLIENT_SECRET', '') or os.environ.get('PROPENTA_CLIENT_SECRET', '')
        self.base_url = getattr(settings, 'PROPENTA_BASE_URL', 'https://app.pay.propentatech.com/api/v2').rstrip('/')
        self.webhook_url = getattr(settings, 'PROPENTA_WEBHOOK_URL', 'https://www.comsas-uy1.com/webhook')
        self.withdrawal_number = getattr(settings, 'PROPENTA_WITHDRAWAL_NUMBER', '237650970526')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'COMSAS-UY1/2026 PropentaPayClient'
        })

    def get_access_token(self, force_refresh=False):
        """
        Obtient ou réutilise un jeton d'accès Bearer via POST /auth/token
        """
        now = time.time()
        if not force_refresh and PropentaPayAPIClient._cached_token and now < (PropentaPayAPIClient._token_expires_at - 10):
            return PropentaPayAPIClient._cached_token

        url = f"{self.base_url}/auth/token"
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }

        try:
            logger.info(f"[PROPENTA_PAY] Requête jeton d'accès vers {url}")
            response = self.session.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
            
            if response.status_code in (200, 201):
                data = response.json()
                token_data = data.get('data') or data
                access_token = token_data.get('accessToken')
                expires_in = int(token_data.get('expiresIn', 120))
                
                if access_token:
                    PropentaPayAPIClient._cached_token = access_token
                    PropentaPayAPIClient._token_expires_at = now + expires_in
                    logger.info(f"[PROPENTA_PAY] Jeton d'accès obtenu avec succès (expire dans {expires_in}s)")
                    return access_token

            logger.error(f"[PROPENTA_PAY] Échec obtention jeton: HTTP {response.status_code} - {response.text[:300]}")
        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Erreur réseau lors de l'authentification token: {e}")

        # Si le serveur externe est inaccessible, retourner None
        return PropentaPayAPIClient._cached_token

    def sign_request(self, method, path, body_bytes):
        """
        Calcule l'en-tête X-Signature selon la spécification HMAC-SHA256 Propenta Pay V2:
        CANONICAL = {METHOD}\n{PATH}\n{TIMESTAMP}\n{BODY_HASH}
        Signature = HMAC-SHA256(key=AppKey/clientId, message=CANONICAL)
        Header = t={timestamp},v1={signature}
        """
        ts = str(int(time.time()))
        body_hash = hashlib.sha256(body_bytes if body_bytes else b"").hexdigest()
        
        # Le path canonique doit commencer par /api/v2 s'il s'agit de la racine V2
        canonical_path = path if path.startswith('/api/v2') else f"/api/v2{path}"
        canonical = f"{method.upper()}\n{canonical_path}\n{ts}\n{body_hash}"
        
        signature = hmac.new(
            self.client_id.encode('utf-8'),
            canonical.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"t={ts},v1={signature}"

    @staticmethod
    def normalize_phone(phone):
        """
        Nettoie et formate le numéro au format international sans + (ex: 237670000000)
        """
        if not phone:
            return ""
        clean = str(phone).replace('+', '').replace(' ', '').replace('-', '').replace('.', '')
        if not clean.startswith('237') and len(clean) == 9:
            clean = f"237{clean}"
        return clean

    @staticmethod
    def detect_payment_method(phone):
        """
        Détecte automatiquement la méthode de paiement Mobile Money au Cameroun
        MTN_MOMO ou ORANGE_MONEY
        """
        norm = PropentaPayAPIClient.normalize_phone(phone)
        # Préfixes Orange Cameroun : 69X, 655X, 656X, 657X, 658X, 659X
        orange_prefixes = ('23769', '237655', '237656', '237657', '237658', '237659')
        if any(norm.startswith(p) for p in orange_prefixes):
            return "ORANGE_MONEY"
        # Préfixes MTN Cameroun : 67X, 68X, 650X, 651X, 652X, 653X, 654X
        return "MTN_MOMO"

    @staticmethod
    def get_instructions_for_phone(phone):
        """
        Instructions USSD adaptées à l'opérateur pour valider la transaction
        """
        method = PropentaPayAPIClient.detect_payment_method(phone)
        if method == "ORANGE_MONEY":
            return "Composez #150*50# ou validez le message reçu sur votre téléphone avec votre code secret Orange Money."
        return "Composez *126# ou validez l'invite USSD sur votre écran avec votre code secret MTN Mobile Money."

    def payin(self, order_id, amount, phone, method=None, webhook_url=None):
        """
        Initie un encaissement Payin (POST /payin)
        """
        norm_phone = self.normalize_phone(phone)
        pay_method = method or self.detect_payment_method(norm_phone)
        callback_url = webhook_url or self.webhook_url
        int_amount = int(amount)

        payload = {
            "country": "CM",
            "payment_type": "CM_MOBILEMONEY",
            "method": pay_method,
            "order_id": str(order_id)[:64],
            "amount": int_amount,
            "phone": norm_phone,
            "webhook_url": callback_url
        }

        body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        x_signature = self.sign_request("POST", "/payin", body_bytes)
        token = self.get_access_token()

        headers = {
            'Content-Type': 'application/json',
            'X-Signature': x_signature
        }
        if token:
            headers['Authorization'] = f"Bearer {token}"

        url = f"{self.base_url}/payin"
        logger.info(f"[PROPENTA_PAY] Initiation Payin: {order_id} | Phone: {norm_phone} | Montant: {int_amount} XAF | Méthode: {pay_method}")

        try:
            response = self.session.post(url, data=body_bytes, headers=headers, timeout=30)
            logger.info(f"[PROPENTA_PAY] Réponse HTTP Payin {response.status_code}: {response.text[:500]}")

            if response.status_code in (200, 201):
                data = response.json()
                inner_data = data.get('data') or data
                tx_ref = inner_data.get('transactionRef') or inner_data.get('reference') or f"PI-{order_id}"
                status = inner_data.get('status', 'PENDING')

                return {
                    'success': True,
                    'reference': tx_ref,
                    'status': status,
                    'externalTxId': inner_data.get('externalTxId'),
                    'message': 'Demande de paiement envoyée sur votre téléphone. Composez votre code secret.',
                    'instructions': self.get_instructions_for_phone(norm_phone),
                    'method': pay_method
                }
            else:
                err_text = response.text[:300]
                try:
                    err_json = response.json()
                    err_msg = err_json.get('message') or err_json.get('error') or err_text
                except Exception:
                    err_msg = err_text
                logger.error(f"[PROPENTA_PAY] Erreur Payin HTTP {response.status_code}: {err_msg}")
                return {'success': False, 'error': err_msg}

        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Exception Payin: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def check_status(self, transaction_ref_or_order_id):
        """
        Vérifie le statut d'une transaction (GET /transactions/{id}/status)
        """
        token = self.get_access_token()
        headers = {}
        if token:
            headers['Authorization'] = f"Bearer {token}"

        url = f"{self.base_url}/transactions/{transaction_ref_or_order_id}/status"

        try:
            response = self.session.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                inner = data.get('data') or data
                raw_status = inner.get('status', 'PENDING')
                return {
                    'success': True,
                    'status': raw_status,
                    'data': inner,
                    'raw_status': raw_status
                }
            logger.warning(f"[PROPENTA_PAY] Vérification statut HTTP {response.status_code}: {response.text[:200]}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Exception check_status: {e}")
            return {'success': False, 'error': str(e)}

    def payout(self, amount, order_id, phone=None, method=None):
        """
        Initie un décaissement Payout (POST /payout) vers le compte administrateur
        """
        target_phone = self.normalize_phone(phone or self.withdrawal_number)
        pay_method = method or self.detect_payment_method(target_phone)
        int_amount = int(amount)

        payload = {
            "country": "CM",
            "payment_type": "CM_MOBILEMONEY",
            "method": pay_method,
            "order_id": str(order_id)[:64],
            "amount": int_amount,
            "phone": target_phone,
            "webhook_url": self.webhook_url
        }

        body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        x_signature = self.sign_request("POST", "/payout", body_bytes)
        token = self.get_access_token()

        headers = {
            'Content-Type': 'application/json',
            'X-Signature': x_signature
        }
        if token:
            headers['Authorization'] = f"Bearer {token}"

        url = f"{self.base_url}/payout"
        try:
            logger.info(f"[PROPENTA_PAY] Initiation Payout {order_id} | Montant: {int_amount} XAF vers {target_phone}")
            response = self.session.post(url, data=body_bytes, headers=headers, timeout=25)
            if response.status_code in (200, 201):
                data = response.json()
                return {'success': True, 'data': data.get('data') or data}
            return {'success': False, 'error': f"HTTP {response.status_code}: {response.text[:200]}"}
        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Exception Payout: {e}")
            return {'success': False, 'error': str(e)}


class PropentaPaymentProcessor:
    """
    Processeur universel pour tous les paiements comsas-uy1.com via Propenta Pay V2
    Prend en charge :
    - Parrainage Professionnel (Parrain 5 000 FCFA / Filleul 10 000 FCFA avec Pass Soirée)
    - Activités d'événements (EventActivityApplication)
    - Concours & Votes (Miss & Master COFESTI, The Voice, J.U.IN, etc.)
    - Dons & Contributions (Donations officielles et J.U.IN)
    """

    def __init__(self):
        self.api = PropentaPayAPIClient()

    @staticmethod
    def translate_error_message(raw_msg):
        """Traduit les erreurs techniques en messages clairs et conviviaux pour l'utilisateur"""
        if not raw_msg:
            return "La transaction n'a pas pu aboutir. Veuillez vérifier votre solde Mobile Money et réessayer."
        
        msg_str = str(raw_msg)
        msg_lower = msg_str.lower()

        if any(k in msg_lower for k in ['low_balance', 'insufficient_balance', 'solde insuffisant', 'funds', 'solde bas']):
            return "Solde insuffisant sur votre compte Mobile Money. Veuillez recharger votre compte et réessayer."
        if any(k in msg_lower for k in ['invalid pin', 'wrong pin', 'pin incorrect', 'code secret', 'code pin', 'bad pin']):
            return "Code secret incorrect. Veuillez réessayer en composant votre code secret exact."
        if any(k in msg_lower for k in ['user_cancelled', 'user_rejected', 'annulé par', 'annule par', 'refusé', 'cancelled', 'canceled']):
            return "La transaction a été refusée ou annulée sur votre téléphone."
        if any(k in msg_lower for k in ['timeout', 'expired', 'expire', 'délai', 'delai', 'temps écoulé']):
            return "Le délai de confirmation a expiré. Veuillez relancer la transaction et valider promptement sur votre écran."
        if any(k in msg_lower for k in ['limit_reached', 'plafond', 'max limit', 'limite atteinte']):
            return "Le plafond autorisé sur votre compte Mobile Money est atteint."
        if any(k in msg_lower for k in ['subscriber not found', 'not registered', 'numéro non enregistré', 'compte inexistant']):
            return "Ce numéro n'est pas activé pour le service Mobile Money auprès de l'opérateur."
        if any(k in msg_lower for k in ['unavailable', 'indisponible', 'down', 'maintenance']):
            return "Le service de l'opérateur Mobile Money est momentanément indisponible. Veuillez réessayer dans quelques instants."

        return msg_str

    # -------------------------------------------------------------------------
    # 1. PARRAINAGE PROFESSIONNEL (5 000 F / 10 000 F + PASS SOIRÉE RESTO N°2)
    # -------------------------------------------------------------------------
    def process_sponsorship_payment(self, participant, phone=None):
        """
        Traite le paiement Mobile Money pour une inscription au parrainage (Parrain ou Filleul)
        """
        try:
            payer_phone = phone or participant.phone
            clean_phone = self.api.normalize_phone(payer_phone)
            amount = int(participant.amount)
            order_id = participant.transaction_id

            logger.info(f"[PROPENTA_PAY] Paiement Parrainage pour {participant.first_name} {participant.last_name} | Montant: {amount} | Phone: {clean_phone}")
            res = self.api.payin(order_id=order_id, amount=amount, phone=clean_phone)

            if res.get('success'):
                participant.payment_reference = res.get('reference', '')
                participant.payment_status = 'initiated'
                participant.save(update_fields=['payment_reference', 'payment_status'])
                return {
                    'success': True,
                    'reference': res.get('reference'),
                    'message': res.get('message', 'Une demande de paiement a été envoyée sur votre téléphone.'),
                    'instructions': res.get('instructions', self.api.get_instructions_for_phone(clean_phone)),
                    'status': res.get('status', 'PENDING')
                }
            else:
                raw_err = res.get('error', 'Échec initiation')
                return {'success': False, 'error': self.translate_error_message(raw_err)}
        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Exception process_sponsorship_payment: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def confirm_sponsorship_payment(self, participant, payment_ref=None):
        """
        Valide définitivement le paiement du parrainage, génère le Pass officiel PDF et QR code (Idempotent)
        """
        try:
            if participant.is_paid:
                return {'success': True, 'message': 'Paiement déjà validé.'}

            from .utils import generate_sponsorship_pass

            participant.is_paid = True
            participant.payment_status = 'confirmed'
            participant.paid_at = timezone.now()
            if payment_ref:
                participant.payment_reference = payment_ref
            if hasattr(participant, 'status') and participant.status == 'pending':
                participant.status = 'approved' if isinstance(participant, Mentor) else 'paid'
            participant.save()

            # Génération du Pass Soirée Resto N°2 avec QR Code officiel
            try:
                generate_sponsorship_pass(participant)
            except Exception as e:
                logger.error(f"[SPONSORSHIP PASS ERROR] Erreur génération pass: {e}")

            logger.info(f"[PROPENTA_PAY] Parrainage validé et Pass généré pour {participant.transaction_id}")
            return {'success': True, 'message': 'Paiement validé avec succès et Pass officiel généré.'}
        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Exception confirm_sponsorship_payment: {e}")
            return {'success': False, 'error': str(e)}

    # -------------------------------------------------------------------------
    # 2. ACTIVITÉS D'ÉVÉNEMENTS (EventActivityApplication)
    # -------------------------------------------------------------------------
    def process_activity_payment(self, app_instance):
        """
        Traite le paiement pour une inscription à une activité d'événement payante
        """
        try:
            clean_phone = self.api.normalize_phone(app_instance.phone)
            amount = int(app_instance.amount)
            order_id = app_instance.transaction_id

            logger.info(f"[PROPENTA_PAY] Paiement Activité: {app_instance.activity.title} | {order_id} | Phone: {clean_phone} | Montant: {amount}")
            res = self.api.payin(order_id=order_id, amount=amount, phone=clean_phone)

            if res.get('success'):
                app_instance.payment_reference = res.get('reference', '')
                app_instance.save(update_fields=['payment_reference'])
                return {
                    'success': True,
                    'reference': res.get('reference'),
                    'message': res.get('message', 'Demande de paiement envoyée sur votre téléphone.'),
                    'instructions': res.get('instructions', self.api.get_instructions_for_phone(clean_phone)),
                    'status': res.get('status', 'PENDING')
                }
            else:
                raw_err = res.get('error', 'Échec initiation')
                return {'success': False, 'error': self.translate_error_message(raw_err)}
        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Exception process_activity_payment: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def confirm_activity_payment(self, app_instance):
        """
        Valide définitivement le paiement et confirme la candidature à l'activité
        """
        try:
            if app_instance.is_paid:
                return {'success': True, 'message': 'Déjà validé'}
            app_instance.is_paid = True
            app_instance.status = 'confirmed'
            app_instance.save(update_fields=['is_paid', 'status'])
            logger.info(f"[PROPENTA_PAY] Candidature activité confirmée et payée: {app_instance.transaction_id}")
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # -------------------------------------------------------------------------
    # 3. CONCOURS & VOTES (Vote, JUINVote, CofestiVote)
    # -------------------------------------------------------------------------
    def process_vote_payment(self, vote_instance):
        """
        Traite le paiement pour un vote en ligne (Vote standard, JUINVote, CofestiVote)
        """
        try:
            clean_phone = self.api.normalize_phone(vote_instance.voter_phone)
            amount = int(vote_instance.amount)
            order_id = vote_instance.transaction_id

            logger.info(f"[PROPENTA_PAY] Paiement Vote: {order_id} | Phone: {clean_phone} | Montant: {amount}")
            res = self.api.payin(order_id=order_id, amount=amount, phone=clean_phone)

            if res.get('success'):
                vote_instance.payment_reference = res.get('reference', '')
                vote_instance.status = 'processing'
                vote_instance.save()
                return {
                    'success': True,
                    'reference': res.get('reference'),
                    'message': res.get('message', 'Demande de paiement envoyée sur votre téléphone.'),
                    'instructions': res.get('instructions', self.api.get_instructions_for_phone(clean_phone)),
                    'status': res.get('status', 'PENDING')
                }
            else:
                raw_err = res.get('error', 'Échec initiation')
                return {'success': False, 'error': self.translate_error_message(raw_err)}
        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Exception process_vote_payment: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def confirm_payment(self, vote_instance):
        """
        Confirme un vote en ligne, incrémente le compteur de voix et de recettes du candidat
        """
        try:
            if vote_instance.status == 'completed':
                return {'success': True, 'message': 'Déjà confirmé'}

            vote_instance.status = 'completed'
            vote_instance.completed_at = timezone.now()
            vote_instance.save()

            # Mise à jour des votes du candidat
            candidate = vote_instance.candidate
            candidate.votes_count += vote_instance.vote_count
            if hasattr(candidate, 'total_revenue'):
                candidate.total_revenue += vote_instance.amount
            candidate.save()

            logger.info(f"[PROPENTA_PAY] Vote confirmé pour {candidate.name} (+{vote_instance.vote_count} voix)")

            # Retrait automatique admin si configuré
            try:
                withdrawal_id = f"WD-{vote_instance.transaction_id}"
                self.api.payout(amount=vote_instance.amount, order_id=withdrawal_id)
            except Exception as e:
                logger.warning(f"[PROPENTA_PAY] Retrait automatique Payout non bloquant: {e}")

            return {'success': True}
        except Exception as e:
            logger.error(f"[PROPENTA_PAY] Erreur confirmation vote: {e}")
            return {'success': False, 'error': str(e)}

    # -------------------------------------------------------------------------
    # 4. DONS OFFICIELS & SOUTIENS (Donation, JUINDonation)
    # -------------------------------------------------------------------------
    def initiate_payment(self, amount, phone_number, description="Don COMSAS", external_id=None):
        """
        Initiation générique de paiement Mobile Money pour les formulaires de Don
        """
        if not external_id:
            external_id = f"COMSASDON-{uuid.uuid4().hex[:10].upper()}"

        clean_phone = self.api.normalize_phone(phone_number)
        res = self.api.payin(order_id=external_id, amount=amount, phone=clean_phone)

        if res.get('success'):
            return {
                'success': True,
                'reference': res.get('reference'),
                'message': res.get('message', 'Paiement initié avec succès.'),
                'instructions': res.get('instructions', self.api.get_instructions_for_phone(clean_phone)),
                'status': res.get('status', 'PENDING')
            }
        else:
            raw_err = res.get('error', 'Erreur de paiement')
            return {'success': False, 'error': self.translate_error_message(raw_err)}

    def check_payment_status(self, reference):
        """
        Vérifie le statut d'un don ou d'une transaction via l'API Propenta Pay
        """
        res = self.api.check_status(reference)
        if res.get('success'):
            raw_status = res.get('raw_status', 'PENDING')
            return {
                'success': True,
                'status': raw_status,
                'raw_reason': '',
                'reason': self.translate_error_message(res.get('error')),
                'data': res.get('data', {})
            }
        return {'success': False, 'error': res.get('error')}

    def verify_payment_status(self, instance):
        """
        Vérification universelle du statut pour polling AJAX
        """
        try:
            ref = getattr(instance, 'payment_reference', None) or getattr(instance, 'transaction_id', None) or getattr(instance, 'external_id', None)
            if not ref:
                return {'success': False, 'error': 'Référence manquante'}

            res = self.api.check_status(ref)
            if res.get('success'):
                propenta_status = res.get('raw_status', 'PENDING')
                status_map = {
                    'SUCCESS': 'completed',
                    'PAID': 'completed',
                    'COMPLETED': 'completed',
                    'FAILED': 'failed',
                    'CANCELLED': 'failed',
                    'REJECTED': 'failed',
                    'PENDING': 'processing',
                    'PROCESSING': 'processing'
                }
                internal_status = status_map.get(propenta_status, 'processing')
                return {
                    'success': True,
                    'status': internal_status,
                    'propenta_status': propenta_status,
                    'data': res.get('data')
                }
            return {'success': False, 'error': res.get('error', 'Erreur vérification')}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class PropentaWebhookHandler:
    """
    Gestionnaire officiel des Webhooks Propenta Pay V2
    URL configurée dans le tableau de bord : https://www.comsas-uy1.com/webhook
    Format documenté par Propenta :
    {
      "event": "transaction.status",
      "data": {
        "transactionRef": "PI-XXXX",
        "order_id": "SPONSORPAY-PARRAIN-...",
        "status": "SUCCESS" | "FAILED",
        "amount": 5000,
        "phone": "237...",
        "externalTxId": "..."
      }
    }
    """

    @staticmethod
    def handle_webhook(request_body):
        try:
            if isinstance(request_body, bytes):
                body_str = request_body.decode('utf-8')
            else:
                body_str = str(request_body)

            data = json.loads(body_str) if body_str else {}
            logger.info(f"[PROPENTA WEBHOOK] Données reçues: {data}")

            # Extraction des données de transaction (prise en charge format imbriqué ou plat)
            tx_data = data.get('data') if isinstance(data.get('data'), dict) else data
            order_id = tx_data.get('order_id') or tx_data.get('orderId') or tx_data.get('externalId') or data.get('order_id')
            status = (tx_data.get('status') or data.get('status') or '').upper()
            reference = tx_data.get('transactionRef') or tx_data.get('reference') or data.get('reference')

            if not order_id:
                logger.warning(f"[PROPENTA WEBHOOK] Aucun identifiant order_id trouvé dans le payload")
                return {'success': False, 'error': 'No order_id found'}

            processor = PropentaPaymentProcessor()
            is_success = status in ('SUCCESS', 'PAID', 'COMPLETED', 'SUCCESSFUL')
            is_failed = status in ('FAILED', 'FAILURE', 'ERROR', 'CANCELLED', 'CANCELED', 'REJECTED', 'EXPIRED')

            logger.info(f"[PROPENTA WEBHOOK] Traitement order_id: {order_id} | Statut: {status} | Succès: {is_success}")

            # 1. PARRAINAGE PROFESSIONNEL (SPONSORPAY-PARRAIN-* ou SPONSORPAY-FILLEUL-*)
            if order_id.startswith('SPONSORPAY'):
                participant = Mentor.objects.filter(transaction_id=order_id).first()
                if not participant:
                    participant = Mentee.objects.filter(transaction_id=order_id).first()

                if participant:
                    if is_success:
                        processor.confirm_sponsorship_payment(participant, payment_ref=reference)
                    elif is_failed:
                        participant.payment_status = 'failed'
                        participant.save(update_fields=['payment_status'])
                    return {'success': True, 'type': 'sponsorship', 'id': participant.id}
                return {'success': False, 'error': f'Participant {order_id} introuvable'}

            # 2. ACTIVITÉS D'ÉVÉNEMENTS (ACTIVITYPAY-*)
            elif order_id.startswith('ACTIVITYPAY'):
                app = EventActivityApplication.objects.filter(transaction_id=order_id).first()
                if app:
                    if is_success:
                        processor.confirm_activity_payment(app)
                    elif is_failed:
                        app.status = 'cancelled'
                        app.save(update_fields=['status'])
                    return {'success': True, 'type': 'activity_application', 'id': app.id}
                return {'success': False, 'error': f'Application {order_id} introuvable'}

            # 3. VOTES COFESTI (COFESTIVOTE-*)
            elif order_id.startswith('COFESTIVOTE'):
                vote = CofestiVote.objects.filter(transaction_id=order_id).first()
                if vote:
                    if is_success:
                        processor.confirm_payment(vote)
                    elif is_failed:
                        vote.status = 'failed'
                        vote.save(update_fields=['status'])
                    return {'success': True, 'type': 'cofesti_vote', 'id': vote.id}
                return {'success': False, 'error': f'CofestiVote {order_id} introuvable'}

            # 4. VOTES J.U.IN (JUINVOTE-*)
            elif order_id.startswith('JUINVOTE'):
                vote = JUINVote.objects.filter(transaction_id=order_id).first()
                if vote:
                    if is_success:
                        processor.confirm_payment(vote)
                    elif is_failed:
                        vote.status = 'failed'
                        vote.save(update_fields=['status'])
                    return {'success': True, 'type': 'juin_vote', 'id': vote.id}
                return {'success': False, 'error': f'JUINVote {order_id} introuvable'}

            # 5. DONS J.U.IN (JUINDON-*)
            elif order_id.startswith('JUINDON'):
                donation = JUINDonation.objects.filter(external_id=order_id).first()
                if donation:
                    if is_success:
                        donation.is_confirmed = True
                        donation.payment_status = 'completed'
                        donation.completed_at = timezone.now()
                        donation.save()
                    elif is_failed:
                        donation.payment_status = 'failed'
                        donation.save(update_fields=['payment_status'])
                    return {'success': True, 'type': 'juin_donation', 'id': donation.id}
                return {'success': False, 'error': f'JUINDonation {order_id} introuvable'}

            # 6. DONS COMSAS OFFICIELS (COMSASDON-*)
            elif order_id.startswith('COMSASDON'):
                donation = Donation.objects.filter(external_id=order_id).first()
                if donation:
                    if is_success:
                        donation.is_confirmed = True
                        donation.payment_status = 'completed'
                        donation.completed_at = timezone.now()
                        donation.save()
                    elif is_failed:
                        donation.payment_status = 'failed'
                        donation.save(update_fields=['payment_status'])
                    return {'success': True, 'type': 'donation', 'id': donation.id}
                return {'success': False, 'error': f'Donation {order_id} introuvable'}

            # 7. VOTES STANDARDS (VOTE-*)
            else:
                vote = Vote.objects.filter(transaction_id=order_id).first()
                if vote:
                    if is_success:
                        processor.confirm_payment(vote)
                    elif is_failed:
                        vote.status = 'failed'
                        vote.save(update_fields=['status'])
                    return {'success': True, 'type': 'vote', 'id': vote.id}
                return {'success': False, 'error': f'Vote {order_id} introuvable'}

        except Exception as e:
            logger.error(f"[PROPENTA WEBHOOK] Exception handle_webhook: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}


# Alias pour rétro-compatibilité totale transparente
FreemopayPaymentProcessor = PropentaPaymentProcessor
FreemopayWebhookHandler = PropentaWebhookHandler
FreemopayService = PropentaPaymentProcessor

