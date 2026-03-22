"""WhatsApp chat export parser.

Parses raw WhatsApp .txt exports into structured Message objects.
Handles both multi-line messages and system messages.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Matches: DD/MM/YY, HH:MM am/pm - Sender: body  (Android WhatsApp export format)
_LINE_RE = re.compile(r"^(\d{1,2}/\d{2}/\d{2}),\s(\d{1,2}:\d{2}\s[ap]m)\s-\s([^:]+):\s(.*)$")

_SKIP_BODIES = {"<Media omitted>", "This message was deleted", "null"}


@dataclass
class Message:
    """A single parsed WhatsApp message.

    Attributes:
        timestamp: When the message was sent.
        sender: Display name of the sender.
        body: Full text content of the message (multi-line joined with newlines).
    """

    timestamp: datetime
    sender: str
    body: str


def parse_chat(raw: str) -> list[Message]:
    """Parse a raw WhatsApp chat export string into a list of Messages.

    Handles:
    - Multi-line messages (continuation lines have no timestamp prefix).
    - System messages (e.g. "Alice created group...") — skipped.
    - Media omitted placeholders — skipped.

    Args:
        raw: The full text content of the WhatsApp export file.

    Returns:
        List of Message objects in chronological order.
    """
    messages: list[Message] = []
    pending: Message | None = None

    for line in raw.splitlines():
        match = _LINE_RE.match(line)
        if match:
            # Flush previous pending message
            if pending is not None:
                _maybe_append(messages, pending)

            date_str, time_str, sender, body = match.groups()
            try:
                timestamp = datetime.strptime(f"{date_str} {time_str}".upper(), "%d/%m/%y %I:%M %p")
            except ValueError:
                logger.warning("Could not parse timestamp from line: %r", line)
                pending = None
                continue

            pending = Message(timestamp=timestamp, sender=sender.strip(), body=body)
        elif pending is not None and line.strip():
            # Continuation of a multi-line message
            pending = Message(
                timestamp=pending.timestamp,
                sender=pending.sender,
                body=f"{pending.body}\n{line}",
            )

    # Flush the last message
    if pending is not None:
        _maybe_append(messages, pending)

    logger.info("Parsed %d messages from chat export", len(messages))
    return messages


def _maybe_append(messages: list[Message], msg: Message) -> None:
    """Append a message if it should not be skipped.

    Args:
        messages: The list to append to.
        msg: The candidate message.
    """
    if msg.body.strip() in _SKIP_BODIES:
        return
    messages.append(msg)
