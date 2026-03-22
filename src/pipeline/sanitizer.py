"""PII sanitizer for WhatsApp chat messages.

Removes phone numbers and email addresses from message senders and bodies
before LLM processing.
"""

import logging
import re

from pipeline.parser import Message

logger = logging.getLogger(__name__)

# Matches international phone numbers (e.g. +91 98333 03828)
_PHONE_RE = re.compile(r"\+?\d[\d\s\-\(\)]{7,}\d")
# Matches email addresses (e.g. user@example.com)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def sanitize(messages: list[Message]) -> list[Message]:
    """Replace PII in senders and bodies before LLM processing.

    Phone-number senders are replaced with stable anonymous tokens (User_1, User_2, …)
    so the same number always maps to the same label within a run. Phone numbers found
    inside message bodies are replaced with ``[PHONE]``. Email addresses in message
    bodies are replaced with ``[EMAIL]``.

    Args:
        messages: Parsed messages from the chat export.

    Returns:
        New list of Message objects with phone numbers and emails removed.
    """
    phone_to_token: dict[str, str] = {}

    def _token(phone: str) -> str:
        if phone not in phone_to_token:
            phone_to_token[phone] = f"User_{len(phone_to_token) + 1}"
        return phone_to_token[phone]

    result: list[Message] = []
    for msg in messages:
        sender = msg.sender
        if _PHONE_RE.fullmatch(sender.strip()):
            sender = _token(sender.strip())
        body = _PHONE_RE.sub("[PHONE]", msg.body)
        body = _EMAIL_RE.sub("[EMAIL]", body)
        result.append(Message(timestamp=msg.timestamp, sender=sender, body=body))

    replaced_count = len(phone_to_token)
    if replaced_count:
        logger.info(
            "Sanitized %d messages: replaced %d unique phone number sender(s)",
            len(messages),
            replaced_count,
        )
    return result
