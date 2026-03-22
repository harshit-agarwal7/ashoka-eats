"""Tests for the message chunker."""

from datetime import datetime

from pipeline.chunker import chunk_messages
from pipeline.parser import Message


def _make_messages(n: int) -> list[Message]:
    """Create n dummy messages."""
    return [
        Message(
            timestamp=datetime(2024, 1, 1, i // 60, i % 60, 0),
            sender=f"User{i}",
            body=f"Message {i}",
        )
        for i in range(n)
    ]


def test_fewer_messages_than_window_returns_one_chunk():
    messages = _make_messages(10)
    chunks = chunk_messages(messages, size=30, stride=15)
    assert len(chunks) == 1
    assert chunks[0] == messages


def test_exact_window_size_produces_overlapping_chunks():
    # 30 messages, size=30, stride=15 → [0:30] and [15:30]
    messages = _make_messages(30)
    chunks = chunk_messages(messages, size=30, stride=15)
    assert len(chunks) == 2
    assert chunks[0] == messages[0:30]
    assert chunks[1] == messages[15:30]


def test_three_windows_with_overlap():
    messages = _make_messages(40)
    # size=30, stride=15 → [0:30], [15:40], [30:40]
    chunks = chunk_messages(messages, size=30, stride=15)
    assert len(chunks) == 3
    assert chunks[0] == messages[0:30]
    assert chunks[1] == messages[15:40]
    assert chunks[2] == messages[30:40]


def test_overlap_ensures_message_appears_in_multiple_chunks():
    messages = _make_messages(45)
    chunks = chunk_messages(messages, size=30, stride=15)
    # message at index 20 should appear in chunk 0 (0:30) and chunk 1 (15:45)
    msg = messages[20]
    assert msg in chunks[0]
    assert msg in chunks[1]


def test_empty_messages_returns_empty():
    chunks = chunk_messages([], size=30, stride=15)
    assert chunks == []


def test_single_message_returns_one_chunk():
    messages = _make_messages(1)
    chunks = chunk_messages(messages, size=30, stride=15)
    assert len(chunks) == 1
    assert chunks[0] == messages


def test_stride_equals_size_no_overlap():
    messages = _make_messages(60)
    chunks = chunk_messages(messages, size=30, stride=30)
    assert len(chunks) == 2
    assert chunks[0] == messages[0:30]
    assert chunks[1] == messages[30:60]


def test_chunk_count_with_many_messages():
    messages = _make_messages(100)
    # stride=15 → starts at 0,15,30,...,90,99(ish) — every start < len
    chunks = chunk_messages(messages, size=30, stride=15)
    starts = list(range(0, 100, 15))
    assert len(chunks) == len(starts)
