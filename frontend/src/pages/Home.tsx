import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { loadMeta, loadRecommendations } from '../data/loader'
import type { Meta, Recommendation } from '../types'
import { CityGrid } from '../components/CityGrid'
import { SearchBox } from '../components/SearchBox'
import { RecommendationCard } from '../components/RecommendationCard'

export function Home() {
  const [meta, setMeta] = useState<Meta | null>(null)
  const [recs, setRecs] = useState<Recommendation[]>([])
  const [searchResults, setSearchResults] = useState<Recommendation[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([loadMeta(), loadRecommendations()])
      .then(([m, r]) => {
        setMeta(m)
        setRecs(r)
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : 'Failed to load data'
        setError(message)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-stone-400 flex flex-col items-center gap-3">
          <span className="text-4xl animate-pulse">🍽️</span>
          <p className="text-sm">Loading picks…</p>
        </div>
      </div>
    )
  }

  if (error || !meta) {
    return (
      <div className="max-w-md mx-auto text-center py-24 px-6">
        <p className="text-5xl mb-4">😕</p>
        <p className="text-stone-500">
          {error ?? 'No data available. Run the pipeline to generate recommendations.'}
        </p>
      </div>
    )
  }

  return (
    <main>
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-amber-50 via-orange-50 to-stone-50 border-b border-stone-100">
        {/* Dot pattern overlay */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: 'radial-gradient(circle, #92400e 1px, transparent 1px)',
            backgroundSize: '28px 28px',
          }}
        />

        <div className="relative max-w-3xl mx-auto px-6 py-16 md:py-24 text-center">
          <p className="text-amber-600 font-semibold text-xs tracking-[0.2em] uppercase mb-4">
            Ashoka University Alumni
          </p>
          <h1
            className="text-5xl md:text-7xl font-bold text-stone-900 mb-4 leading-tight"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Ashoka Eats
          </h1>
          <p className="text-stone-500 text-lg md:text-xl mb-3">
            Alumni-curated food picks across India
          </p>
          <p className="text-stone-400 text-sm mb-10">
            Crowdsourced from the group chat, so you can trust it.
          </p>

          {/* Stats row */}
          <div className="flex justify-center items-center gap-8 mb-10">
            <div>
              <p
                className="text-3xl font-bold text-amber-600"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                {meta.total_recommendations}
              </p>
              <p className="text-xs text-stone-400 uppercase tracking-wider mt-0.5">Picks</p>
            </div>
            <div className="h-8 w-px bg-stone-200" />
            <div>
              <p
                className="text-3xl font-bold text-amber-600"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                {meta.cities.length}
              </p>
              <p className="text-xs text-stone-400 uppercase tracking-wider mt-0.5">Cities</p>
            </div>
            <div className="h-8 w-px bg-stone-200" />
            <div>
              <p
                className="text-3xl font-bold text-amber-600"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                {meta.recommenders.length}
              </p>
              <p className="text-xs text-stone-400 uppercase tracking-wider mt-0.5">
                Contributors
              </p>
            </div>
          </div>

          <div className="max-w-lg mx-auto">
            <SearchBox recommendations={recs} onResults={setSearchResults} />
          </div>
        </div>
      </section>

      {/* Search results */}
      {searchResults !== null && (
        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
          <p className="text-sm text-stone-400 mb-5">
            {searchResults.length === 0
              ? 'No matches found'
              : `${searchResults.length} result${searchResults.length !== 1 ? 's' : ''}`}
          </p>
          {searchResults.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-4xl mb-3">🔍</p>
              <p className="text-stone-400">Try searching for a place, city, or person.</p>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map((rec) => (
                <RecommendationCard key={rec.id} rec={rec} />
              ))}
            </div>
          )}
        </section>
      )}

      {/* City browse */}
      {searchResults === null && (
        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12">
          <h2
            className="text-2xl font-bold text-stone-800 mb-6"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Browse by City
          </h2>
          <CityGrid
            cities={meta.cities}
            recommendations={recs}
            onCityClick={(slug) => navigate(`/city/${slug}`)}
          />
        </section>
      )}

      {/* Category shortcuts */}
      {searchResults === null && meta.categories.length > 0 && (
        <section className="max-w-6xl mx-auto px-4 sm:px-6 pb-12">
          <h2
            className="text-2xl font-bold text-stone-800 mb-6"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Browse by Category
          </h2>
          <div className="flex flex-wrap gap-3">
            {meta.categories.map((cat) => (
              <button
                key={cat}
                onClick={() => navigate(`/category/${cat}`)}
                className="px-5 py-2.5 bg-white border border-stone-200 rounded-xl text-sm font-medium capitalize text-stone-700 hover:border-amber-300 hover:text-amber-700 hover:shadow-sm transition-all"
              >
                {cat}
              </button>
            ))}
          </div>
        </section>
      )}
    </main>
  )
}
