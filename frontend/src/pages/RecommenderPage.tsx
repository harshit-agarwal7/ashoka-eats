import { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { loadRecommendations, loadMeta } from '../data/loader'
import type { Recommendation, Recommender } from '../types'
import { RecommendationCard } from '../components/RecommendationCard'

export function RecommenderPage() {
  const { name } = useParams<{ name: string }>()
  const decodedName = decodeURIComponent(name ?? '')

  const [recs, setRecs] = useState<Recommendation[]>([])
  const [recommenderMeta, setRecommenderMeta] = useState<Recommender | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([loadRecommendations(), loadMeta()])
      .then(([r, m]) => {
        setRecs(r)
        const found = m.recommenders.find((rec) => rec.name === decodedName) ?? null
        setRecommenderMeta(found)
      })
      .finally(() => setLoading(false))
  }, [decodedName])

  const myRecs = useMemo(
    () => recs.filter((r) => r.recommender_name === decodedName),
    [recs, decodedName],
  )

  // Group by city
  const byCity = useMemo(() => {
    const groups: Record<string, Recommendation[]> = {}
    for (const rec of myRecs) {
      if (!groups[rec.city]) groups[rec.city] = []
      groups[rec.city].push(rec)
    }
    return groups
  }, [myRecs])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <p className="text-stone-400 animate-pulse">Loading…</p>
      </div>
    )
  }

  if (myRecs.length === 0) {
    return (
      <div className="max-w-md mx-auto text-center py-24 px-6">
        <p className="text-5xl mb-4">👤</p>
        <p className="text-stone-500 mb-4">No picks from {decodedName} yet.</p>
        <Link to="/" className="text-amber-600 hover:text-amber-700 text-sm font-medium">
          ← Back home
        </Link>
      </div>
    )
  }

  const trustPct = recommenderMeta
    ? Math.round(recommenderMeta.trust_score * 100)
    : null

  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      <Link
        to="/"
        className="text-sm text-stone-400 hover:text-stone-600 transition-colors mb-6 inline-block"
      >
        ← Home
      </Link>

      {/* Profile header */}
      <div className="bg-white rounded-2xl border border-stone-100 p-6 mb-8 flex flex-col sm:flex-row items-start sm:items-center gap-5">
        <div className="w-14 h-14 rounded-full bg-amber-100 flex items-center justify-center text-2xl font-bold text-amber-700 flex-shrink-0">
          {decodedName.charAt(0).toUpperCase()}
        </div>
        <div className="flex-1">
          <h1
            className="text-2xl font-bold text-stone-900"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            {decodedName}
          </h1>
          <div className="flex flex-wrap gap-3 mt-2 text-sm text-stone-500">
            <span>{myRecs.length} pick{myRecs.length !== 1 ? 's' : ''}</span>
            <span>·</span>
            <span>{Object.keys(byCity).length} cit{Object.keys(byCity).length !== 1 ? 'ies' : 'y'}</span>
            {trustPct !== null && (
              <>
                <span>·</span>
                <span className="text-amber-600 font-medium">{trustPct}% trust score</span>
              </>
            )}
          </div>
          {recommenderMeta && recommenderMeta.top_categories.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {recommenderMeta.top_categories.map((cat) => (
                <Link
                  key={cat}
                  to={`/category/${cat}`}
                  className="text-xs px-2.5 py-0.5 bg-amber-50 text-amber-700 rounded-full border border-amber-200 capitalize hover:bg-amber-100 transition-colors"
                >
                  {cat}
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recommendations by city */}
      <div className="space-y-10">
        {Object.entries(byCity).map(([city, cityRecs]) => (
          <section key={city}>
            <div className="flex items-center gap-3 mb-4">
              <Link
                to={`/city/${cityRecs[0].city_slug}`}
                className="text-xl font-bold text-stone-800 hover:text-amber-700 transition-colors"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                {city}
              </Link>
              <span className="text-xs text-stone-400 bg-stone-100 px-2 py-0.5 rounded-full">
                {cityRecs.length} pick{cityRecs.length !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {cityRecs.map((rec) => (
                <RecommendationCard key={rec.id} rec={rec} />
              ))}
            </div>
          </section>
        ))}
      </div>
    </main>
  )
}
