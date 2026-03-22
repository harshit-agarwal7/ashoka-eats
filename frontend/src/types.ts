/** Mirrors pipeline/enricher.py Recommendation dataclass */
export interface Recommendation {
  id: string
  place_name: string
  city: string
  city_slug: string
  category: string
  category_slug: string
  recommender_name: string
  quotes: string[]
  confidence: number
  recommender_trust_score: number
}

/** Mirrors pipeline/enricher.py Recommender dataclass */
export interface Recommender {
  name: string
  recommendation_count: number
  trust_score: number
  top_cities: string[]
  top_categories: string[]
}

/** Mirrors pipeline/writer.py meta.json shape */
export interface Meta {
  cities: string[]
  categories: string[]
  recommenders: Recommender[]
  total_recommendations: number
  pipeline_run_at: string
  source_message_count: number
}
