"""Tests for the recommendation deduplicator."""

from pipeline.deduplicator import deduplicate
from pipeline.extractor import RawRecommendation


def _rec(
    place: str,
    city: str,
    recommender: str = "Alice",
    quote: str = "Great place!",
    confidence: float = 0.9,
    chunk_index: int = 0,
    category: str = "food",
) -> RawRecommendation:
    return RawRecommendation(
        place_name=place,
        city=city,
        category=category,
        recommender_name=recommender,
        quote=quote,
        confidence=confidence,
        chunk_index=chunk_index,
    )


def test_no_duplicates_unchanged():
    recs = [
        _rec("Bukhara", "New Delhi"),
        _rec("Toit", "Bengaluru"),
        _rec("Irani Cafe", "Mumbai"),
    ]
    result = deduplicate(recs)
    assert len(result) == 3


def test_exact_duplicate_merged():
    recs = [
        _rec("Bukhara", "New Delhi", quote="Amazing dal makhani!", confidence=0.9, chunk_index=0),
        _rec(
            "Bukhara", "New Delhi", quote="Best dal makhani ever.", confidence=0.85, chunk_index=1
        ),
    ]
    result = deduplicate(recs)
    assert len(result) == 1
    assert result[0].place_name == "Bukhara"
    assert result[0].confidence == 0.9  # keeps highest
    assert len(result[0].quotes) == 2  # both quotes merged


def test_fuzzy_duplicate_merged():
    recs = [
        _rec("Bukhara Restaurant", "New Delhi", quote="Try the lamb.", confidence=0.9),
        _rec("Bukhara", "New Delhi", quote="Dal makhani is legendary.", confidence=0.88),
    ]
    result = deduplicate(recs)
    assert len(result) == 1


def test_same_place_different_city_not_merged():
    recs = [
        _rec("Starbucks", "Mumbai"),
        _rec("Starbucks", "Delhi"),
    ]
    result = deduplicate(recs)
    assert len(result) == 2


def test_below_threshold_dropped():
    recs = [
        _rec("Bukhara", "New Delhi", confidence=0.9),
        _rec("Maybe a place?", "Unknown", confidence=0.3),
    ]
    result = deduplicate(recs)
    assert len(result) == 1
    assert result[0].place_name == "Bukhara"


def test_all_below_threshold_returns_empty():
    recs = [
        _rec("Place A", "City X", confidence=0.2),
        _rec("Place B", "City Y", confidence=0.1),
    ]
    result = deduplicate(recs)
    assert result == []


def test_empty_input_returns_empty():
    assert deduplicate([]) == []


def test_single_recommendation_passthrough():
    recs = [_rec("Bukhara", "New Delhi")]
    result = deduplicate(recs)
    assert len(result) == 1
    assert result[0].place_name == "Bukhara"
    assert result[0].quotes == ["Great place!"]


def test_merged_quotes_are_unique():
    recs = [
        _rec("Bukhara", "New Delhi", quote="Amazing!", chunk_index=0),
        _rec("Bukhara", "New Delhi", quote="Amazing!", chunk_index=1),  # same quote
        _rec("Bukhara", "New Delhi", quote="Different quote.", chunk_index=2),
    ]
    result = deduplicate(recs)
    assert len(result) == 1
    assert len(result[0].quotes) == 2  # deduped
