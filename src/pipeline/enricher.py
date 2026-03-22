"""Enricher for the ashoka-eats pipeline.

Computes derived fields: IDs, slugs, city normalization, trust scores,
and recommender statistics.
"""

import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field

from pipeline.deduplicator import MergedRecommendation

logger = logging.getLogger(__name__)

# City name normalization: alias → canonical
_CITY_ALIASES: dict[str, str] = {
    "bombay": "Mumbai",
    "bangalore": "Bengaluru",
    "calcutta": "Kolkata",
    "madras": "Chennai",
    "poona": "Pune",
}


@dataclass
class Recommendation:
    """An enriched, publication-ready recommendation.

    Attributes:
        id: URL-safe slug (place-city).
        place_name: Name of the recommended place.
        city: Canonical city name.
        city_slug: URL-safe city slug.
        category: Category (food/drinks/cafe/dessert/other).
        category_slug: URL-safe category slug.
        recommender_name: Display name of the recommender.
        quotes: All unique quotes collected across merged duplicates.
        confidence: Highest confidence score.
        recommender_trust_score: Normalized 0–1 trust score.
    """

    id: str
    place_name: str
    city: str
    city_slug: str
    category: str
    category_slug: str
    recommender_name: str
    quotes: list[str]
    confidence: float
    recommender_trust_score: float


@dataclass
class Recommender:
    """Statistics about a single contributor.

    Attributes:
        name: Display name.
        recommendation_count: Total recommendations made.
        trust_score: Normalized 0–1 trust score.
        top_cities: Most-recommended cities (descending frequency).
        top_categories: Most-recommended categories (descending frequency).
    """

    name: str
    recommendation_count: int
    trust_score: float
    top_cities: list[str] = field(default_factory=list)
    top_categories: list[str] = field(default_factory=list)


def _slugify(text: str) -> str:
    """Convert text to a URL-safe lowercase slug.

    Args:
        text: Input string.

    Returns:
        Slug with only alphanumeric characters and hyphens.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _normalize_city(city: str) -> str:
    """Return the canonical city name, resolving known aliases.

    Args:
        city: Raw city name from LLM extraction.

    Returns:
        Canonical city name.
    """
    return _CITY_ALIASES.get(city.lower().strip(), city.strip())


def _trust_score(count: int, max_count: int) -> float:
    """Compute a normalized trust score using log scaling.

    Args:
        count: Number of recommendations by this person.
        max_count: Maximum count across all recommenders.

    Returns:
        Score in [0, 1].
    """
    if max_count <= 1:
        return 1.0 if count >= 1 else 0.0
    return math.log(1 + count) / math.log(1 + max_count)


def enrich(
    merged: list[MergedRecommendation],
) -> tuple[list[Recommendation], list[Recommender]]:
    """Enrich merged recommendations with derived fields and compute recommender stats.

    Args:
        merged: Deduplicated recommendations from the deduplicator.

    Returns:
        Tuple of (enriched recommendations, sorted recommender list).
    """
    if not merged:
        return [], []

    # Count recommendations per recommender
    counts: Counter[str] = Counter(r.recommender_name for r in merged)
    max_count = max(counts.values())

    # Per-recommender city and category tracking
    cities_by_rec: dict[str, list[str]] = {name: [] for name in counts}
    cats_by_rec: dict[str, list[str]] = {name: [] for name in counts}

    recommendations: list[Recommendation] = []
    for rec in merged:
        canonical_city = _normalize_city(rec.city)
        trust = _trust_score(counts[rec.recommender_name], max_count)
        city_slug = _slugify(canonical_city)
        category_slug = _slugify(rec.category)
        rec_id = f"{_slugify(rec.place_name)}-{city_slug}"

        cities_by_rec[rec.recommender_name].append(canonical_city)
        cats_by_rec[rec.recommender_name].append(rec.category)

        recommendations.append(
            Recommendation(
                id=rec_id,
                place_name=rec.place_name,
                city=canonical_city,
                city_slug=city_slug,
                category=rec.category,
                category_slug=category_slug,
                recommender_name=rec.recommender_name,
                quotes=rec.quotes,
                confidence=rec.confidence,
                recommender_trust_score=trust,
            )
        )

    # Build recommender list
    recommenders: list[Recommender] = []
    for name, count in counts.items():
        top_cities = [city for city, _ in Counter(cities_by_rec[name]).most_common()]
        top_cats = [cat for cat, _ in Counter(cats_by_rec[name]).most_common()]
        recommenders.append(
            Recommender(
                name=name,
                recommendation_count=count,
                trust_score=_trust_score(count, max_count),
                top_cities=top_cities,
                top_categories=top_cats,
            )
        )

    recommenders.sort(key=lambda r: r.recommendation_count, reverse=True)
    logger.info(
        "Enriched %d recommendations, %d recommenders", len(recommendations), len(recommenders)
    )
    return recommendations, recommenders
