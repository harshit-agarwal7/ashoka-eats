import { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { loadRecommendations } from '../data/loader'
import type { Recommendation } from '../types'
import { RecommendationCard } from '../components/RecommendationCard'

const CATEGORY_LABELS: Record<string, string> = {
  food: '🍽 Food',
  drinks: '🍻 Drinks',
  cafe: '☕ Cafes',
  dessert: '🍮 Desserts',
  other: '📍 Other',
}

export function CategoryPage() {
  const { slug } = useParams<{ slug: string }>()
  const [recs, setRecs] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [activeCity, setActiveCity] = useState('')

  useEffect(() => {
    loadRecommendations()
      .then(setRecs)
      .finally(() => setLoading(false))
  }, [])

  const catRecs = useMemo(
    () => recs.filter((r) => r.category_slug === slug || r.category === slug),
    [recs, slug],
  )

  const cities = useMemo(
    () => [...new Set(catRecs.map((r) => r.city))].sort(),
    [catRecs],
  )

  const filtered = useMemo(
    () => (activeCity ? catRecs.filter((r) => r.city === activeCity) : catRecs),
    [catRecs, activeCity],
  )

  const label = CATEGORY_LABELS[slug ?? ''] ?? slug ?? 'Category'

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <p className="text-stone-400 animate-pulse">Loading…</p>
      </div>
    )
  }

  if (catRecs.length === 0) {
    return (
      <div className="max-w-md mx-auto text-center py-24 px-6">
        <p className="text-5xl mb-4">🍽️</p>
        <p className="text-stone-500 mb-4">No picks in this category yet.</p>
        <Link to="/" className="text-amber-600 hover:text-amber-700 text-sm font-medium">
          ← Back home
        </Link>
      </div>
    )
  }

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      <Link
        to="/"
        className="text-sm text-stone-400 hover:text-stone-600 transition-colors mb-4 inline-block"
      >
        ← Home
      </Link>

      <div className="mb-8">
        <h1
          className="text-3xl md:text-4xl font-bold text-stone-900 mb-1"
          style={{ fontFamily: 'var(--font-display)' }}
        >
          {label}
        </h1>
        <p className="text-stone-400 text-sm">
          {catRecs.length} pick{catRecs.length !== 1 ? 's' : ''} across {cities.length} cit
          {cities.length !== 1 ? 'ies' : 'y'}
        </p>
      </div>

      {/* City filter chips */}
      {cities.length > 1 && (
        <div className="flex flex-wrap gap-2 mb-6">
          <button
            onClick={() => setActiveCity('')}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              activeCity === ''
                ? 'bg-amber-600 text-white border-amber-600'
                : 'bg-white text-stone-600 border-stone-200 hover:border-stone-300'
            }`}
          >
            All Cities
          </button>
          {cities.map((city) => (
            <button
              key={city}
              onClick={() => setActiveCity(city)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                activeCity === city
                  ? 'bg-amber-600 text-white border-amber-600'
                  : 'bg-white text-stone-600 border-stone-200 hover:border-stone-300'
              }`}
            >
              {city}
            </button>
          ))}
        </div>
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((rec) => (
          <RecommendationCard key={rec.id} rec={rec} />
        ))}
      </div>
    </main>
  )
}
