import { useState, useEffect, useRef } from 'react'
import Fuse from 'fuse.js'
import type { Recommendation } from '../types'

interface SearchBoxProps {
  recommendations: Recommendation[]
  onResults: (results: Recommendation[] | null) => void
}

export function SearchBox({ recommendations, onResults }: SearchBoxProps) {
  const [query, setQuery] = useState('')
  const fuseRef = useRef<Fuse<Recommendation> | null>(null)

  useEffect(() => {
    fuseRef.current = new Fuse(recommendations, {
      keys: ['place_name', 'city', 'recommender_name', 'quotes'],
      threshold: 0.35,
      includeScore: true,
    })
  }, [recommendations])

  function handleChange(q: string) {
    setQuery(q)
    if (!q.trim()) {
      onResults(null)
      return
    }
    const results = fuseRef.current?.search(q).map((r) => r.item) ?? []
    onResults(results)
  }

  return (
    <div className="relative">
      <span className="absolute left-4 top-1/2 -translate-y-1/2 text-stone-400 pointer-events-none">
        🔍
      </span>
      <input
        type="search"
        value={query}
        onChange={(e) => handleChange(e.target.value)}
        placeholder="Search places, cities, people…"
        className="w-full px-4 py-3.5 pl-11 rounded-xl border border-stone-200 bg-white text-stone-800 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-amber-300 shadow-sm text-sm"
      />
      {query && (
        <button
          onClick={() => handleChange('')}
          className="absolute right-4 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600 transition-colors"
          aria-label="Clear search"
        >
          ✕
        </button>
      )}
    </div>
  )
}
