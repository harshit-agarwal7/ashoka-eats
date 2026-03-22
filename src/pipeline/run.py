"""CLI entry point for the ashoka-eats recommendation pipeline.

Usage:
    uv run python -m pipeline.run --chat chat/_chat.txt
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from config.settings import settings

from pipeline.chunker import chunk_messages, serialize_chunks
from pipeline.deduplicator import deduplicate
from pipeline.enricher import enrich
from pipeline.extractor import extract_from_chunks
from pipeline.parser import parse_chat
from pipeline.writer import write_output

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ashoka-eats recommendation pipeline.")
    parser.add_argument(
        "--chat",
        type=Path,
        default=Path("chat/_chat.txt"),
        help="Path to the WhatsApp chat export file (default: chat/_chat.txt)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory to write output JSON files (default: data/)",
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Skip LLM extraction and re-use existing data/raw_chunks.json",
    )
    return parser.parse_args()


async def _run(args: argparse.Namespace) -> None:
    """Orchestrate all pipeline phases.

    Args:
        args: Parsed CLI arguments.
    """
    chat_path: Path = args.chat
    data_dir: Path = args.data_dir
    chunks_path = data_dir / "raw_chunks.json"

    if not chat_path.exists():
        logger.error("Chat export not found at %s", chat_path)
        sys.exit(1)

    # Phase 1: Parse
    logger.info("Parsing chat export from %s", chat_path)
    raw_text = chat_path.read_text(encoding="utf-8")
    messages = parse_chat(raw_text)
    logger.info("Parsed %d messages", len(messages))

    # Phase 2: Chunk
    chunks = chunk_messages(messages, size=settings.chunk_size, stride=settings.chunk_stride)
    serialize_chunks(chunks, chunks_path)

    # Phase 3: Extract
    logger.info("Extracting recommendations from %d chunks via LLM...", len(chunks))
    raw_recs = await extract_from_chunks(
        chunks,
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
        concurrency=settings.llm_concurrency,
    )
    logger.info("Extracted %d raw recommendations", len(raw_recs))

    # Phase 4: Deduplicate
    merged = deduplicate(raw_recs)
    logger.info("After deduplication: %d recommendations", len(merged))

    # Phase 5: Enrich
    recommendations, recommenders = enrich(merged)

    # Phase 6: Write
    write_output(recommendations, recommenders, len(messages), data_dir)

    logger.info(
        "Pipeline complete: %d recommendations across %d cities written to %s/",
        len(recommendations),
        len({r.city for r in recommendations}),
        data_dir,
    )


def main() -> None:
    """Entry point called by the pipeline CLI script."""
    args = _parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
