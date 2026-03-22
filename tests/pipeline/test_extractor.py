"""Tests for the LLM extractor (mocking HTTP layer)."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.extractor import RawRecommendation, extract_from_chunks
from pipeline.parser import Message


def _make_chunk(messages: list[tuple[str, str]]) -> list[Message]:
    return [
        Message(timestamp=datetime(2024, 1, 1, 0, i, 0), sender=sender, body=body)
        for i, (sender, body) in enumerate(messages)
    ]


MOCK_LLM_RESPONSE_ONE = [
    {
        "place_name": "Bukhara",
        "city": "New Delhi",
        "category": "food",
        "recommender_name": "Priya",
        "quote": "Bukhara's dal makhani is life changing!",
        "confidence": 0.95,
    }
]

MOCK_LLM_RESPONSE_EMPTY: list[dict[str, object]] = []

MOCK_LLM_RESPONSE_MULTIPLE = [
    {
        "place_name": "Toit",
        "city": "Bengaluru",
        "category": "drinks",
        "recommender_name": "Rohan",
        "quote": "Best craft beer in the city.",
        "confidence": 0.88,
    },
    {
        "place_name": "Third Wave Coffee",
        "city": "Bengaluru",
        "category": "cafe",
        "recommender_name": "Ananya",
        "quote": "Amazing cold brew, must visit.",
        "confidence": 0.72,
    },
]


def _mock_response(payload: list[dict[str, object]]) -> MagicMock:
    """Build a mock httpx.Response that returns the given payload as JSON."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json = MagicMock(
        return_value={"choices": [{"message": {"content": json.dumps(payload)}}]}
    )
    return response


@pytest.fixture
def chunk_one():
    return _make_chunk([("Priya", "You should try Bukhara in Delhi!")])


@pytest.fixture
def chunk_empty():
    return _make_chunk([("Bob", "Hey, how's everyone doing?")])


@pytest.fixture
def chunk_multiple():
    return _make_chunk(
        [
            ("Rohan", "Toit in Bengaluru has the best craft beer."),
            ("Ananya", "Third Wave Coffee is my go-to for cold brew."),
        ]
    )


@pytest.mark.asyncio
async def test_extracts_single_recommendation(chunk_one: list[Message]):
    mock_response = _mock_response(MOCK_LLM_RESPONSE_ONE)

    with patch("pipeline.extractor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        results = await extract_from_chunks([chunk_one], api_key="test-key", model="test-model")

    assert len(results) == 1
    rec = results[0]
    assert isinstance(rec, RawRecommendation)
    assert rec.place_name == "Bukhara"
    assert rec.city == "New Delhi"
    assert rec.category == "food"
    assert rec.recommender_name == "Priya"
    assert rec.confidence == 0.95
    assert rec.chunk_index == 0


@pytest.mark.asyncio
async def test_empty_response_yields_no_recommendations(chunk_empty: list[Message]):
    mock_response = _mock_response(MOCK_LLM_RESPONSE_EMPTY)

    with patch("pipeline.extractor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        results = await extract_from_chunks([chunk_empty], api_key="test-key", model="test-model")

    assert results == []


@pytest.mark.asyncio
async def test_extracts_multiple_recommendations(chunk_multiple: list[Message]):
    mock_response = _mock_response(MOCK_LLM_RESPONSE_MULTIPLE)

    with patch("pipeline.extractor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        results = await extract_from_chunks(
            [chunk_multiple], api_key="test-key", model="test-model"
        )

    assert len(results) == 2
    assert results[0].place_name == "Toit"
    assert results[1].place_name == "Third Wave Coffee"


@pytest.mark.asyncio
async def test_chunk_index_set_correctly():
    chunks = [
        _make_chunk([("Alice", "Try Bukhara in Delhi")]),
        _make_chunk([("Bob", "Go to Toit in Bengaluru")]),
    ]

    responses = [
        _mock_response(MOCK_LLM_RESPONSE_ONE),
        _mock_response(
            [
                {
                    "place_name": "Toit",
                    "city": "Bengaluru",
                    "category": "drinks",
                    "recommender_name": "Bob",
                    "quote": "Go to Toit.",
                    "confidence": 0.8,
                }
            ]
        ),
    ]

    with patch("pipeline.extractor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=responses)
        mock_client_cls.return_value = mock_client

        results = await extract_from_chunks(chunks, api_key="test-key", model="test-model")

    chunk_indices = {r.place_name: r.chunk_index for r in results}
    assert chunk_indices["Bukhara"] == 0
    assert chunk_indices["Toit"] == 1


@pytest.mark.asyncio
async def test_malformed_json_from_llm_skips_chunk(chunk_one: list[Message]):
    """If LLM returns non-JSON, that chunk is skipped gracefully."""
    bad_response = MagicMock()
    bad_response.raise_for_status = MagicMock()
    bad_response.json = MagicMock(
        return_value={"choices": [{"message": {"content": "not valid json ["}}]}
    )

    with patch("pipeline.extractor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=bad_response)
        mock_client_cls.return_value = mock_client

        results = await extract_from_chunks([chunk_one], api_key="test-key", model="test-model")

    assert results == []
