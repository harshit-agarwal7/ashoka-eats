"""LLM-based recommendation extractor for the ashoka-eats pipeline.

Sends chunked WhatsApp messages to an OpenRouter LLM and extracts structured
food/drink/cafe recommendations.
"""

import asyncio
import json
import logging
from dataclasses import dataclass

import httpx

from pipeline.parser import Message

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a food recommendation extractor. Given a WhatsApp group chat excerpt, \
extract all food, drink, cafe, or restaurant recommendations made by members.

Return ONLY a valid JSON array. Each element must have exactly these fields:
- place_name: exact name of the place
- city: city where the place is located (infer from context if not stated; use canonical name)
- category: one of ["food", "drinks", "cafe", "dessert", "other"]
- recommender_name: the WhatsApp display name of the person recommending it
- quote: the most relevant sentence(s) from their message (verbatim)
- confidence: float 0.0–1.0 (how certain you are this is a genuine recommendation)

Rules:
- Do NOT include places people are asking about — only places being actively recommended.
- If a message is ambiguous, set confidence below 0.6.
- If no recommendations are present, return [].
- Return raw JSON only, no markdown fences."""


def _chunk_to_text(chunk: list[Message]) -> str:
    """Format a chunk of messages as a readable chat transcript.

    Args:
        chunk: List of Message objects.

    Returns:
        Formatted string suitable for inclusion in an LLM prompt.
    """
    lines = [
        f"[{msg.timestamp.strftime('%d/%m/%Y %H:%M')}] {msg.sender}: {msg.body}" for msg in chunk
    ]
    return "\n".join(lines)


async def _extract_chunk(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    chunk: list[Message],
    chunk_index: int,
    api_key: str,
    model: str,
    base_url: str,
) -> list["RawRecommendation"]:
    """Extract recommendations from a single chunk using the LLM.

    Args:
        client: The shared httpx async client.
        semaphore: Concurrency limiter.
        chunk: The messages to process.
        chunk_index: Index of this chunk (stored in each extraction).
        api_key: OpenRouter API key.
        model: LLM model identifier.
        base_url: Base URL for the OpenRouter API.

    Returns:
        List of RawRecommendation objects parsed from the LLM response.
    """
    transcript = _chunk_to_text(chunk)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with semaphore:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60.0,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429 and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                logger.warning("Rate limited on chunk %d, retrying in %ds", chunk_index, wait)
                await asyncio.sleep(wait)
                continue
            logger.error("HTTP error on chunk %d: %s", chunk_index, exc)
            return []
        except httpx.RequestError as exc:
            logger.error("Request error on chunk %d: %s", chunk_index, exc)
            return []

        content: str = response.json()["choices"][0]["message"]["content"]
        try:
            raw_list: list[dict[str, object]] = json.loads(content)
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            logger.warning("Could not parse LLM response for chunk %d: %s", chunk_index, exc)
            return []

        results: list[RawRecommendation] = []
        for item in raw_list:
            try:
                results.append(
                    RawRecommendation(
                        place_name=str(item["place_name"]),
                        city=str(item["city"]),
                        category=str(item.get("category", "other")),
                        recommender_name=str(item["recommender_name"]),
                        quote=str(item["quote"]),
                        confidence=float(item.get("confidence", 0.5)),  # type: ignore[arg-type]
                        chunk_index=chunk_index,
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning(
                    "Skipping malformed extraction item in chunk %d: %s", chunk_index, exc
                )

        logger.debug("Chunk %d: extracted %d recommendations", chunk_index, len(results))
        return results

    return []


async def extract_from_chunks(
    chunks: list[list[Message]],
    api_key: str,
    model: str,
    base_url: str = "https://openrouter.ai/api/v1",
    concurrency: int = 5,
) -> list["RawRecommendation"]:
    """Extract recommendations from all chunks concurrently.

    Args:
        chunks: List of message chunks to process.
        api_key: OpenRouter API key.
        model: LLM model identifier.
        base_url: Base URL for the OpenRouter API.
        concurrency: Max number of simultaneous LLM requests.

    Returns:
        Flat list of all RawRecommendation objects across all chunks.
    """
    semaphore = asyncio.Semaphore(concurrency)
    all_results: list[RawRecommendation] = []

    async with httpx.AsyncClient() as client:
        tasks = [
            _extract_chunk(client, semaphore, chunk, idx, api_key, model, base_url)
            for idx, chunk in enumerate(chunks)
        ]
        chunk_results = await asyncio.gather(*tasks)

    for recs in chunk_results:
        all_results.extend(recs)

    logger.info(
        "Extraction complete: %d total recommendations from %d chunks",
        len(all_results),
        len(chunks),
    )
    return all_results


@dataclass
class RawRecommendation:
    """A single recommendation extracted by the LLM from a chunk.

    Attributes:
        place_name: Name of the recommended place.
        city: City where the place is located.
        category: Type of place (food/drinks/cafe/dessert/other).
        recommender_name: WhatsApp display name of the recommender.
        quote: Verbatim quote from the recommender's message.
        confidence: LLM confidence score (0.0–1.0).
        chunk_index: Index of the source chunk (for dedup tracing).
    """

    place_name: str
    city: str
    category: str
    recommender_name: str
    quote: str
    confidence: float
    chunk_index: int
