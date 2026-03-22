"""Tests for the WhatsApp chat parser."""

from datetime import datetime

from pipeline.parser import Message, parse_chat

SIMPLE_CHAT = """\
[01/03/2024, 10:00:00] Alice: Hello everyone!
[01/03/2024, 10:01:00] Bob: Hey Alice!
[01/03/2024, 10:02:00] Charlie: Good morning
"""

MULTILINE_CHAT = """\
[01/03/2024, 10:00:00] Alice: You should try Bukhara in Delhi,
it's absolutely amazing for dal makhani.
Seriously one of the best I've had.
[01/03/2024, 10:01:00] Bob: Noted!
"""

MEDIA_OMITTED_CHAT = """\
[01/03/2024, 10:00:00] Alice: <Media omitted>
[01/03/2024, 10:01:00] Bob: Check this place out!
"""

SYSTEM_MESSAGE_CHAT = """\
[01/03/2024, 10:00:00] Alice created group "Ashoka Eats"
[01/03/2024, 10:01:00] Bob: Hello!
"""

EMPTY_CHAT = ""


def test_simple_messages():
    messages = parse_chat(SIMPLE_CHAT)
    assert len(messages) == 3
    assert messages[0].sender == "Alice"
    assert messages[0].body == "Hello everyone!"
    assert messages[1].sender == "Bob"
    assert messages[2].sender == "Charlie"


def test_timestamps_parsed():
    messages = parse_chat(SIMPLE_CHAT)
    assert messages[0].timestamp == datetime(2024, 3, 1, 10, 0, 0)
    assert messages[1].timestamp == datetime(2024, 3, 1, 10, 1, 0)


def test_multiline_message_joined():
    messages = parse_chat(MULTILINE_CHAT)
    assert len(messages) == 2
    assert "amazing for dal makhani" in messages[0].body
    assert "Seriously one of the best" in messages[0].body
    assert messages[0].sender == "Alice"


def test_media_omitted_skipped():
    messages = parse_chat(MEDIA_OMITTED_CHAT)
    assert len(messages) == 1
    assert messages[0].sender == "Bob"


def test_system_messages_skipped():
    messages = parse_chat(SYSTEM_MESSAGE_CHAT)
    assert len(messages) == 1
    assert messages[0].sender == "Bob"


def test_empty_chat_returns_empty_list():
    messages = parse_chat(EMPTY_CHAT)
    assert messages == []


def test_message_dataclass_fields():
    messages = parse_chat(SIMPLE_CHAT)
    msg = messages[0]
    assert isinstance(msg, Message)
    assert hasattr(msg, "timestamp")
    assert hasattr(msg, "sender")
    assert hasattr(msg, "body")


def test_chat_with_ios_format():
    """iOS exports use [DD/MM/YYYY, HH:MM:SS] format — same as tested above."""
    ios_chat = "[15/06/2023, 14:30:45] Priya: Try Saravana Bhavan in Chennai!\n"
    messages = parse_chat(ios_chat)
    assert len(messages) == 1
    assert messages[0].sender == "Priya"
    assert messages[0].timestamp == datetime(2023, 6, 15, 14, 30, 45)
