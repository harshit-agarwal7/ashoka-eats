"""Message chunker for the ashoka-eats pipeline.

Groups messages into overlapping windows so that recommendations spanning
message boundaries are captured by at least one chunk.
"""

import json
import logging
from pathlib import Path

from pipeline.parser import Message

logger = logging.getLogger(__name__)


def chunk_messages(
    messages: list[Message],
    size: int = 30,
    stride: int = 15,
) -> list[list[Message]]:
    """Split messages into overlapping windows.

    Each message appears in ceil(size/stride) chunks on average, ensuring
    that context around any recommendation is preserved.

    Args:
        messages: Chronologically ordered list of messages.
        size: Number of messages per chunk.
        stride: Step between chunk start positions.

    Returns:
        List of chunks, each being a sublist of messages.
    """
    if not messages:
        return []

    chunks: list[list[Message]] = []
    start = 0
    while start < len(messages):
        chunk = messages[start : start + size]
        chunks.append(chunk)
        start += stride

    logger.info(
        "Created %d chunks from %d messages (size=%d, stride=%d)",
        len(chunks),
        len(messages),
        size,
        stride,
    )
    return chunks


def serialize_chunks(chunks: list[list[Message]], output_path: Path) -> None:
    """Serialize chunks to a JSON file for inspection or resumption.

    Args:
        chunks: The chunked message lists.
        output_path: File path to write the JSON to.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw = [
        [
            {
                "timestamp": msg.timestamp.isoformat(),
                "sender": msg.sender,
                "body": msg.body,
            }
            for msg in chunk
        ]
        for chunk in chunks
    ]
    output_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False))
    logger.info("Wrote %d chunks to %s", len(chunks), output_path)
