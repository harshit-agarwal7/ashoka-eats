"""Tests for the phone number sanitizer."""

from datetime import datetime

from pipeline.parser import Message
from pipeline.sanitizer import sanitize

_TS = datetime(2024, 1, 1, 12, 0, 0)


def _msg(sender: str, body: str) -> Message:
    return Message(timestamp=_TS, sender=sender, body=body)


def test_phone_sender_replaced_with_token():
    messages = [_msg("+91 98333 03828", "Great place!")]
    result = sanitize(messages)
    assert result[0].sender == "User_1"


def test_same_phone_maps_to_same_token():
    messages = [
        _msg("+91 98333 03828", "First message"),
        _msg("+91 98333 03828", "Second message"),
    ]
    result = sanitize(messages)
    assert result[0].sender == result[1].sender == "User_1"


def test_two_different_phones_get_different_tokens():
    messages = [
        _msg("+91 98333 03828", "Hello"),
        _msg("+1 800 555 1234", "World"),
    ]
    result = sanitize(messages)
    assert result[0].sender == "User_1"
    assert result[1].sender == "User_2"


def test_display_name_sender_unchanged():
    messages = [_msg("Alice", "Try Bukhara!")]
    result = sanitize(messages)
    assert result[0].sender == "Alice"


def test_phone_in_body_redacted():
    messages = [_msg("Alice", "Call me at +91 98333 03828 anytime")]
    result = sanitize(messages)
    assert "+91" not in result[0].body
    assert "[PHONE]" in result[0].body


def test_phone_sender_and_phone_in_body():
    messages = [_msg("+91 98333 03828", "My number is +91 98333 03828")]
    result = sanitize(messages)
    assert result[0].sender == "User_1"
    assert "[PHONE]" in result[0].body
    assert "+91" not in result[0].body


def test_empty_list_returns_empty():
    assert sanitize([]) == []


def test_body_and_timestamp_preserved():
    messages = [_msg("Alice", "Try Saravana Bhavan in Chennai!")]
    result = sanitize(messages)
    assert result[0].body == "Try Saravana Bhavan in Chennai!"
    assert result[0].timestamp == _TS
