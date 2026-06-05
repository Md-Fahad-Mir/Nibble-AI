"""Push delivery seam (Firebase Cloud Messaging).

With no FCM_SERVER_KEY configured, pushes are logged (dev). A real FCM/APNs
integration plugs in here without touching the notification service.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def send_push(*, tokens, title, body, data=None) -> bool:
    key = settings.FCM_SERVER_KEY
    if not key:
        logger.info("PUSH (mock) tokens=%s | %s — %s", list(tokens), title, body)
        return True
    # TODO(integration): call FCM with `key`, `tokens`, and the payload.
    logger.info("PUSH (fcm) tokens=%s | %s", list(tokens), title)
    return True
