"""Tests for the pipeline CLI run module."""

import argparse
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from pipeline.parser import Message
from pipeline.run import _run


def _make_messages(n: int) -> list[Message]:
    return [
        Message(timestamp=datetime(2024, 1, 1, 10, i % 60), sender="Alice", body=f"msg {i}")
        for i in range(n)
    ]


def _default_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "chat": Path("chat/_chat.txt"),
        "data_dir": Path("data"),
        "skip_extraction": False,
        "limit": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_pipeline(tmp_path):
    """Patch all pipeline phases so tests don't need real files or LLM calls."""
    messages_100 = _make_messages(100)
    with (
        patch("pipeline.run.parse_chat", return_value=messages_100) as mock_parse,
        patch("pipeline.run.sanitize", side_effect=lambda msgs: msgs) as mock_sanitize,
        patch("pipeline.run.chunk_messages", return_value=[]) as mock_chunk,
        patch("pipeline.run.serialize_chunks"),
        patch("pipeline.run.extract_from_chunks", new=AsyncMock(return_value=[])),
        patch("pipeline.run.deduplicate", return_value=[]),
        patch("pipeline.run.enrich", return_value=([], {})),
        patch("pipeline.run.write_output"),
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.read_text", return_value="fake chat content"),
    ):
        yield {
            "parse_chat": mock_parse,
            "sanitize": mock_sanitize,
            "chunk_messages": mock_chunk,
        }


@pytest.mark.asyncio
async def test_limit_slices_messages(mock_pipeline, tmp_path):
    """--limit N should pass only the first N messages to chunk_messages."""
    args = _default_args(chat=tmp_path / "_chat.txt", data_dir=tmp_path, limit=50)
    await _run(args)

    called_messages = mock_pipeline["chunk_messages"].call_args[0][0]
    assert len(called_messages) == 50


@pytest.mark.asyncio
async def test_no_limit_passes_all_messages(mock_pipeline, tmp_path):
    """Without --limit, all parsed messages should reach chunk_messages."""
    args = _default_args(chat=tmp_path / "_chat.txt", data_dir=tmp_path, limit=None)
    await _run(args)

    called_messages = mock_pipeline["chunk_messages"].call_args[0][0]
    assert len(called_messages) == 100


@pytest.mark.asyncio
async def test_limit_larger_than_messages(mock_pipeline, tmp_path):
    """--limit larger than message count should not raise; all messages pass through."""
    args = _default_args(chat=tmp_path / "_chat.txt", data_dir=tmp_path, limit=999)
    await _run(args)

    called_messages = mock_pipeline["chunk_messages"].call_args[0][0]
    assert len(called_messages) == 100
