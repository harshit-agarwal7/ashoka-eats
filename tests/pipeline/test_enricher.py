"""Tests for the enricher module."""



from pipeline.deduplicator import MergedRecommendation
from pipeline.enricher import Recommendation, enrich


def _merged(
    place: str,
    city: str,
    recommender: str = "Alice",
    quotes: list[str] | None = None,
    confidence: float = 0.9,
    category: str = "food",
) -> MergedRecommendation:
    return MergedRecommendation(
        place_name=place,
        city=city,
        category=category,
        recommender_name=recommender,
        quotes=quotes or ["Great place!"],
        confidence=confidence,
    )


def test_slug_generation():
    recs, _ = enrich([_merged("Bukhara Restaurant", "New Delhi")])
    assert recs[0].id == "bukhara-restaurant-new-delhi"
    assert recs[0].city_slug == "new-delhi"
    assert recs[0].category_slug == "food"


def test_city_normalization_bombay_to_mumbai():
    recs, _ = enrich([_merged("Britannia & Co.", "Bombay")])
    assert recs[0].city == "Mumbai"
    assert recs[0].city_slug == "mumbai"


def test_city_normalization_bangalore_to_bengaluru():
    recs, _ = enrich([_merged("Toit", "Bangalore")])
    assert recs[0].city == "Bengaluru"


def test_city_normalization_calcutta_to_kolkata():
    recs, _ = enrich([_merged("Peter Cat", "Calcutta")])
    assert recs[0].city == "Kolkata"


def test_unknown_city_unchanged():
    recs, _ = enrich([_merged("Some Place", "Jaipur")])
    assert recs[0].city == "Jaipur"


def test_recommendation_fields_present():
    recs, _ = enrich([_merged("Bukhara", "New Delhi", quotes=["Dal makhani is life."])])
    rec = recs[0]
    assert isinstance(rec, Recommendation)
    assert rec.place_name == "Bukhara"
    assert rec.city == "New Delhi"
    assert rec.quotes == ["Dal makhani is life."]
    assert 0.0 <= rec.recommender_trust_score <= 1.0


def test_trust_score_increases_with_count():
    # Alice recommends 3 places, Bob recommends 1 — Alice should have higher trust
    merged = [
        _merged("Place A", "Mumbai", recommender="Alice"),
        _merged("Place B", "Mumbai", recommender="Alice"),
        _merged("Place C", "Delhi", recommender="Alice"),
        _merged("Place D", "Delhi", recommender="Bob"),
    ]
    recs, meta_recs = enrich(merged)
    alice_score = next(r.recommender_trust_score for r in recs if r.recommender_name == "Alice")
    bob_score = next(r.recommender_trust_score for r in recs if r.recommender_name == "Bob")
    assert alice_score > bob_score


def test_recommender_meta_count():
    merged = [
        _merged("Place A", "Mumbai", recommender="Alice"),
        _merged("Place B", "Delhi", recommender="Alice"),
        _merged("Place C", "Delhi", recommender="Bob"),
    ]
    _, recommenders = enrich(merged)
    alice = next(r for r in recommenders if r.name == "Alice")
    bob = next(r for r in recommenders if r.name == "Bob")
    assert alice.recommendation_count == 2
    assert bob.recommendation_count == 1


def test_recommender_top_cities():
    merged = [
        _merged("P1", "Mumbai", recommender="Alice"),
        _merged("P2", "Mumbai", recommender="Alice"),
        _merged("P3", "Delhi", recommender="Alice"),
    ]
    _, recommenders = enrich(merged)
    alice = next(r for r in recommenders if r.name == "Alice")
    assert alice.top_cities[0] == "Mumbai"  # most frequent first


def test_recommender_sorted_by_count_descending():
    merged = [
        _merged("P1", "Mumbai", recommender="Charlie"),
        _merged("P2", "Delhi", recommender="Alice"),
        _merged("P3", "Delhi", recommender="Alice"),
        _merged("P4", "Pune", recommender="Bob"),
        _merged("P5", "Pune", recommender="Bob"),
        _merged("P6", "Pune", recommender="Bob"),
    ]
    _, recommenders = enrich(merged)
    counts = [r.recommendation_count for r in recommenders]
    assert counts == sorted(counts, reverse=True)


def test_empty_input():
    recs, recommenders = enrich([])
    assert recs == []
    assert recommenders == []
