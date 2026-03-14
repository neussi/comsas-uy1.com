"""
Service Freemopay pour Mobile Money Afrique
Authentification Basic Auth — comsas-uy1.com
"""
import requests
import logging
from typing import Tuple
from django.conf import settings
import uuid

logger = logging.getLogger(__name__)


class FreemopayService:
    """Service Freemopay pour les paiements Mobile Money en Afrique"""

    def __init__(self):
        self.app_key = getattr(settings, 'FREEMOPAY_APP_KEY', '')
        self.secret_key = getattr(settings, 'FREEMOPAY_SECRET_KEY', '')
        self.base_url = getattr(settings, 'FREEMOPAY_BASE_URL', 'https://api-v2.freemopay.com')
        logger.info("[FREEMOPAY] Service initialisé")

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> Tuple[bool, dict]:
        """Effectue une requête HTTP vers l'API Freemopay avec Basic Auth UNIQUEMENT"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'COMSAS-Django/1.0'
        }
        auth = (self.app_key, self.secret_key)

        try:
            logger.info(f"[FREEMOPAY] API: {method} {url}")
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers, auth=auth, timeout=30)
            elif method == 'GET':
                response = requests.get(url, headers=headers, auth=auth, timeout=30)
            else:
                return False, {"error": "Méthode non supportée"}

            logger.info(f"[FREEMOPAY] Response: {response.status_code} - {response.text[:500]}")

            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                logger.warning(f"[FREEMOPAY] Rate limit atteint. Retry-After: {retry_after}s")
                return False, {
                    "error": "Trop de requêtes. Veuillez réessayer dans quelques minutes.",
                    "retry_after": retry_after
                }

            if response.status_code in (200, 201, 202):
                return True, response.json()
            else:
                error_data = response.json() if response.content else {"error": f"HTTP {response.status_code}"}
                logger.error(f"[FREEMOPAY] Erreur API: {response.status_code} - {error_data}")
                return False, error_data

        except requests.exceptions.Timeout:
            logger.error("[FREEMOPAY] Timeout lors de l'appel à l'API Freemopay")
            return False, {"error": "Timeout de connexion. Veuillez réessayer."}
        except requests.exceptions.ConnectionError:
            logger.error("[FREEMOPAY] Erreur de connexion à l'API Freemopay")
            return False, {"error": "Erreur de connexion. Vérifiez votre connexion internet."}
        except Exception as e:
            logger.error(f"[FREEMOPAY] Erreur inattendue: {str(e)}")
            return False, {"error": f"Erreur technique: {str(e)}"}

    def initiate_payment(self, amount, phone_number, description="Paiement COMSAS", external_id=None, country_code='CM'):
        """Initier un paiement Mobile Money"""
        try:
            if external_id is None:
                external_id = str(uuid.uuid4())

            clean_phone = self._clean_phone_number(phone_number, country_code)

            payment_data = {
                "payer": clean_phone,
                "amount": str(int(amount)),
                "externalId": str(external_id),
                "description": description,
                "callback": self._get_webhook_url()
            }

            logger.info(f"[FREEMOPAY] Initiation paiement: {external_id}, phone={clean_phone}, amount={amount}")
            success, data = self._make_request('POST', '/api/v2/payment', payment_data)

            if success:
                if data.get('status') in ['SUCCESS', 'CREATED', 'PENDING', 'INITIATED']:
                    return {
                        'success': True,
                        'reference': data.get('reference'),
                        'message': data.get('message', 'Paiement initié avec succès'),
                        'instructions': self._get_payment_instructions(clean_phone),
                        'status': data.get('status')
                    }
                else:
                    return {'success': False, 'error': data.get('message', "Erreur lors de l'initiation")}
            else:
                return {'success': False, 'error': data.get('error', 'Erreur de communication API')}

        except Exception as e:
            logger.error(f"[FREEMOPAY] Erreur initiate_payment: {e}")
            return {'success': False, 'error': str(e)}

    def verify_payment_status(self, payment_reference):
        """Vérifier le statut d'un paiement"""
        try:
            if not payment_reference:
                return {'success': False, 'error': 'Référence manquante'}

            logger.info(f"[FREEMOPAY] Vérification: {payment_reference}")
            success, data = self._make_request('GET', f"/api/v2/payment/{payment_reference}")

            if success:
                freemopay_status = data.get('status', 'PENDING')
                status_mapping = {
                    'SUCCESS': 'completed', 'COMPLETED': 'completed', 'PAID': 'completed', 'SUCCESSFUL': 'completed',
                    'FAILED': 'failed', 'FAILURE': 'failed', 'ERROR': 'failed', 'EXPIRED': 'failed',
                    'CANCELLED': 'cancelled', 'CANCELED': 'cancelled', 'REJECTED': 'failed',
                    'PENDING': 'pending', 'CREATED': 'pending', 'INITIATED': 'pending'
                }
                internal_status = status_mapping.get(freemopay_status.upper(), 'pending')
                return {
                    'success': True,
                    'status': internal_status,
                    'freemopay_status': freemopay_status,
                    'message': data.get('message', ''),
                    'amount': data.get('amount'),
                    'data': data
                }
            else:
                return {'success': False, 'error': data.get('error', 'Erreur de communication API')}

        except Exception as e:
            logger.error(f"[FREEMOPAY] Erreur vérification: {e}")
            return {'success': False, 'error': str(e)}

    def _clean_phone_number(self, phone_number, country_code='CM'):
        """Nettoyer et formater le numéro"""
        if not phone_number:
            return phone_number
        clean = str(phone_number).replace('+', '').replace(' ', '').replace('-', '')
        country_prefixes = {
            'CM': '237', 'SN': '221', 'CI': '225', 'ML': '223', 'BF': '226',
        }
        prefix = country_prefixes.get(country_code, '237')
        if clean.startswith(prefix):
            return clean
        return prefix + clean

    def _get_webhook_url(self):
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{base_url}/api/payments/webhook/freemopay/"

    def _get_payment_instructions(self, phone_number):
        if any(x in phone_number[3:5] for x in ['65', '69', '67']):
            return "Composez #150*50# ou attendez le message Orange Money pour confirmer."
        elif any(x in phone_number[3:5] for x in ['68', '64', '67']):
            return "Composez *126# ou attendez le message MTN Mobile Money pour confirmer."
        else:
            return "Suivez les instructions reçues par SMS pour confirmer votre paiement."
