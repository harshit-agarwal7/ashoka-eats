"""Deduplicator for raw LLM extractions.

Merges recommendations that refer to the same place in the same city,
keeping the highest-confidence extraction and combining unique quotes.
Drops any extraction below a minimum confidence threshold.
"""

import logging
from dataclasses import dataclass, field

from rapidfuzz import fuzz

from pipeline.extractor import RawRecommendation

logger = logging.getLogger(__name__)

_CONFIDENCE_THRESHOLD = 0.5
_FUZZY_MATCH_THRESHOLD = 80.0  # rapidfuzz score 0–100


@dataclass
class MergedRecommendation:
    """A deduplicated recommendation with merged quotes.

    Attributes:
        place_name: Canonical name (from highest-confidence extraction).
        city: Canonical city name.
        category: Category of the place.
        recommender_name: Name of the primary recommender.
        quotes: All unique quotes collected from merged duplicates.
        confidence: Highest confidence score across merged extractions.
    """

    place_name: str
    city: str
    category: str
    recommender_name: str
    quotes: list[str] = field(default_factory=list)
    confidence: float = 0.0


def _normalize(text: str) -> str:
    """Lowercase and strip text for comparison."""
    return text.lower().strip()


def _is_duplicate(a: MergedRecommendation, b: RawRecommendation) -> bool:
    """Check whether b is a near-duplicate of existing merged rec a.

    Args:
        a: Already-merged recommendation.
        b: Candidate to check against a.

    Returns:
        True if place names are fuzzy-similar and cities match.
    """
    if _normalize(a.city) != _normalize(b.city):
        return False
    score = fuzz.WRatio(_normalize(a.place_name), _normalize(b.place_name))
    return float(score) >= _FUZZY_MATCH_THRESHOLD


def deduplicate(recs: list[RawRecommendation]) -> list[MergedRecommendation]:
    """Merge near-duplicate recommendations and drop low-confidence ones.

    Args:
        recs: Raw extractions from the LLM, potentially with duplicates.

    Returns:
        Deduplicated list of MergedRecommendation objects.
    """
    # Filter below threshold first
    above_threshold = [r for r in recs if r.confidence >= _CONFIDENCE_THRESHOLD]
    dropped = len(recs) - len(above_threshold)
    if dropped:
        logger.info(
            "Dropped %d extractions below confidence threshold %.2f", dropped, _CONFIDENCE_THRESHOLD
        )

    # Sort descending by confidence so the best extraction seeds each group
    sorted_recs = sorted(above_threshold, key=lambda r: r.confidence, reverse=True)

    merged: list[MergedRecommendation] = []
    for rec in sorted_recs:
        placed = False
        for existing in merged:
            if _is_duplicate(existing, rec):
                # Merge: update confidence if higher, add unique quote
                if rec.confidence > existing.confidence:
                    existing.confidence = rec.confidence
                    existing.place_name = rec.place_name  # use better-matched name
                if rec.quote not in existing.quotes:
                    existing.quotes.append(rec.quote)
                placed = True
                break
        if not placed:
            merged.append(
                MergedRecommendation(
                    place_name=rec.place_name,
                    city=rec.city,
                    category=rec.category,
                    recommender_name=rec.recommender_name,
                    quotes=[rec.quote],
                    confidence=rec.confidence,
                )
            )

    logger.info(
        "Deduplication: %d raw → %d merged recommendations", len(above_threshold), len(merged)
    )
    return merged
