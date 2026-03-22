import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { loadMeta } from '../data/loader'
import type { Meta } from '../types'
import { Leaderboard } from '../components/Leaderboard'

export function LeaderboardPage() {
  const [meta, setMeta] = useState<Meta | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMeta()
      .then(setMeta)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <p className="text-stone-400 animate-pulse">Loading…</p>
      </div>
    )
  }

  if (!meta) {
    return (
      <div className="max-w-md mx-auto text-center py-24 px-6">
        <p className="text-stone-500">No contributor data available.</p>
      </div>
    )
  }

  return (
    <main className="max-w-2xl mx-auto px-4 sm:px-6 py-10">
      <Link
        to="/"
        className="text-sm text-stone-400 hover:text-stone-600 transition-colors mb-6 inline-block"
      >
        ← Home
      </Link>

      <div className="mb-8">
        <h1
          className="text-3xl md:text-4xl font-bold text-stone-900 mb-2"
          style={{ fontFamily: 'var(--font-display)' }}
        >
          Top Contributors
        </h1>
        <p className="text-stone-400 text-sm">
          The alumni who power Ashoka Eats. Click any name to see their picks.
        </p>
      </div>

      <div className="bg-gradient-to-b from-amber-50 to-transparent rounded-2xl p-4 mb-6 flex gap-6 text-center border border-amber-100">
        <div className="flex-1">
          <p className="text-2xl font-bold text-amber-600" style={{ fontFamily: 'var(--font-display)' }}>
            {meta.recommenders.length}
          </p>
          <p className="text-xs text-stone-400 uppercase tracking-wide">Contributors</p>
        </div>
        <div className="w-px bg-amber-200" />
        <div className="flex-1">
          <p className="text-2xl font-bold text-amber-600" style={{ fontFamily: 'var(--font-display)' }}>
            {meta.total_recommendations}
          </p>
          <p className="text-xs text-stone-400 uppercase tracking-wide">Total Picks</p>
        </div>
        <div className="w-px bg-amber-200" />
        <div className="flex-1">
          <p className="text-2xl font-bold text-amber-600" style={{ fontFamily: 'var(--font-display)' }}>
            {meta.cities.length}
          </p>
          <p className="text-xs text-stone-400 uppercase tracking-wide">Cities Covered</p>
        </div>
      </div>

      <Leaderboard recommenders={meta.recommenders} />
    </main>
  )
}
