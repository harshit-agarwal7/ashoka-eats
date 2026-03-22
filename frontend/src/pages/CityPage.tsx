import { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { loadMeta, loadRecommendations } from '../data/loader'
import type { Meta, Recommendation } from '../types'
import { RecommendationCard } from '../components/RecommendationCard'
import { FilterBar } from '../components/FilterBar'

export function CityPage() {
  const { slug } = useParams<{ slug: string }>()
  const [recs, setRecs] = useState<Recommendation[]>([])
  const [meta, setMeta] = useState<Meta | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeCategory, setActiveCategory] = useState('')
  const [sortBy, setSortBy] = useState('trust')

  useEffect(() => {
    Promise.all([loadRecommendations(), loadMeta()])
      .then(([r, m]) => {
        setRecs(r)
        setMeta(m)
      })
      .finally(() => setLoading(false))
  }, [])

  const cityRecs = useMemo(
    () => recs.filter((r) => r.city_slug === slug),
    [recs, slug],
  )

  const cityName = cityRecs[0]?.city ?? slug?.replace(/-/g, ' ') ?? 'City'

  const categories = useMemo(
    () => [...new Set(cityRecs.map((r) => r.category))].sort(),
    [cityRecs],
  )

  const filtered = useMemo(() => {
    let result = activeCategory
      ? cityRecs.filter((r) => r.category === activeCategory)
      : cityRecs
    if (sortBy === 'trust') {
      result = [...result].sort((a, b) => b.recommender_trust_score - a.recommender_trust_score)
    } else {
      result = [...result].sort((a, b) => a.place_name.localeCompare(b.place_name))
    }
    return result
  }, [cityRecs, activeCategory, sortBy])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <p className="text-stone-400 animate-pulse">Loading…</p>
      </div>
    )
  }

  if (cityRecs.length === 0) {
    return (
      <div className="max-w-md mx-auto text-center py-24 px-6">
        <p className="text-5xl mb-4">🗺️</p>
        <p className="text-stone-500 mb-4">No picks for this city yet.</p>
        <Link to="/" className="text-amber-600 hover:text-amber-700 text-sm font-medium">
          ← Back home
        </Link>
      </div>
    )
  }

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      <div className="mb-8">
        <Link to="/" className="text-sm text-stone-400 hover:text-stone-600 transition-colors mb-4 inline-block">
          ← Home
        </Link>
        <h1
          className="text-3xl md:text-4xl font-bold text-stone-900 mb-1"
          style={{ fontFamily: 'var(--font-display)' }}
        >
          {cityName}
        </h1>
        <p className="text-stone-400 text-sm">
          {cityRecs.length} pick{cityRecs.length !== 1 ? 's' : ''} from alumni
          {meta && ` · ${meta.recommenders.length} contributors`}
        </p>
      </div>

      <div className="mb-6">
        <FilterBar
          categories={categories}
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
          sortBy={sortBy}
          onSortChange={setSortBy}
        />
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-stone-400">No picks in this category for {cityName}.</p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((rec) => (
            <RecommendationCard key={rec.id} rec={rec} />
          ))}
        </div>
      )}
    </main>
  )
}
