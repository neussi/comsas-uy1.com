"""
Module de compatibilité Freemopay -> Propenta Pay
Tous les paiements comsas-uy1.com sont désormais traités exclusivement par Propenta Pay V2.
"""
from .propenta_service import (
    PropentaPayAPIClient,
    PropentaPaymentProcessor,
    PropentaWebhookHandler,
    FreemopayPaymentProcessor,
    FreemopayWebhookHandler,
    FreemopayService
)

__all__ = [
    'PropentaPayAPIClient',
    'PropentaPaymentProcessor',
    'PropentaWebhookHandler',
    'FreemopayPaymentProcessor',
    'FreemopayWebhookHandler',
    'FreemopayService'
]
