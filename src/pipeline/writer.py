"""Output writer for the ashoka-eats pipeline.

Serializes enriched recommendations and metadata to JSON files consumed
by the React frontend.
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from pipeline.enricher import Recommendation, Recommender

logger = logging.getLogger(__name__)


def _rec_to_dict(rec: Recommendation) -> dict[str, object]:
    return {
        "id": rec.id,
        "place_name": rec.place_name,
        "city": rec.city,
        "city_slug": rec.city_slug,
        "category": rec.category,
        "category_slug": rec.category_slug,
        "recommender_name": rec.recommender_name,
        "quotes": rec.quotes,
        "confidence": round(rec.confidence, 4),
        "recommender_trust_score": round(rec.recommender_trust_score, 4),
    }


def _recommender_to_dict(r: Recommender) -> dict[str, object]:
    return {
        "name": r.name,
        "recommendation_count": r.recommendation_count,
        "trust_score": round(r.trust_score, 4),
        "top_cities": r.top_cities[:5],
        "top_categories": r.top_categories[:3],
    }


def write_output(
    recommendations: list[Recommendation],
    recommenders: list[Recommender],
    source_message_count: int,
    output_dir: Path,
) -> None:
    """Write recommendations.json and meta.json to output_dir.

    Args:
        recommendations: Enriched recommendations from the enricher.
        recommenders: Sorted recommender list from the enricher.
        source_message_count: Number of messages parsed from the chat export.
        output_dir: Directory to write output files into (created if absent).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    recs_path = output_dir / "recommendations.json"
    recs_data = [_rec_to_dict(r) for r in recommendations]
    recs_path.write_text(json.dumps(recs_data, indent=2, ensure_ascii=False))
    logger.info("Wrote %d recommendations to %s", len(recommendations), recs_path)

    cities = sorted({r.city for r in recommendations})
    categories = sorted({r.category for r in recommendations})

    meta: dict[str, object] = {
        "cities": cities,
        "categories": categories,
        "recommenders": [_recommender_to_dict(r) for r in recommenders],
        "total_recommendations": len(recommendations),
        "pipeline_run_at": datetime.now(UTC).isoformat(),
        "source_message_count": source_message_count,
    }
    meta_path = output_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    logger.info("Wrote meta to %s", meta_path)
