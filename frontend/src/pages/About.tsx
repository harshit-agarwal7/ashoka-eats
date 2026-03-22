import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { loadMeta } from '../data/loader'
import type { Meta } from '../types'

export function About() {
  const [meta, setMeta] = useState<Meta | null>(null)

  useEffect(() => {
    loadMeta().then(setMeta).catch(() => null)
  }, [])

  const runDate = meta?.pipeline_run_at
    ? new Date(meta.pipeline_run_at).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      })
    : null

  return (
    <main className="max-w-2xl mx-auto px-4 sm:px-6 py-10">
      <Link
        to="/"
        className="text-sm text-stone-400 hover:text-stone-600 transition-colors mb-6 inline-block"
      >
        ← Home
      </Link>

      <h1
        className="text-3xl md:text-4xl font-bold text-stone-900 mb-8"
        style={{ fontFamily: 'var(--font-display)' }}
      >
        About Ashoka Eats
      </h1>

      <div className="space-y-8 text-stone-600 leading-relaxed">
        <section>
          <h2
            className="text-xl font-semibold text-stone-800 mb-3"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            What is this?
          </h2>
          <p>
            Ashoka Eats is a curated collection of food, drink, and cafe recommendations shared by
            Ashoka University alumni in a WhatsApp group chat. Over time, the group amassed hundreds
            of genuine, first-hand recommendations across cities all over India.
          </p>
          <p className="mt-3">
            This site makes those picks searchable and browsable — so the next time you're
            travelling, you can find something trusted by someone you know.
          </p>
        </section>

        <section>
          <h2
            className="text-xl font-semibold text-stone-800 mb-3"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            How it works
          </h2>
          <ol className="list-none space-y-3">
            {[
              ['📱', 'Source', 'Recommendations collected from the alumni WhatsApp group chat export.'],
              ['🤖', 'Extraction', 'An LLM (via OpenRouter) reads each conversation window and extracts structured picks: place, city, category, and the recommender\'s exact words.'],
              ['🔁', 'Deduplication', 'Near-duplicate mentions of the same place are merged, keeping all unique quotes.'],
              ['⭐', 'Trust scores', 'Contributors who recommend more places earn a higher trust score, shown as dots on each card.'],
              ['🌐', 'Published', 'Everything is compiled into a static website — no server, no tracking, no accounts needed.'],
            ].map(([icon, label, desc]) => (
              <li key={label} className="flex gap-3">
                <span className="text-xl flex-shrink-0 mt-0.5">{icon}</span>
                <div>
                  <span className="font-semibold text-stone-700">{label}: </span>
                  {desc}
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section>
          <h2
            className="text-xl font-semibold text-stone-800 mb-3"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Privacy
          </h2>
          <p>
            Recommender names are displayed as they appeared in the chat (first name or display
            name). No contact information, photos, or other personal data is stored or published.
            The source WhatsApp export is never made public.
          </p>
        </section>

        {meta && (
          <section className="pt-4 border-t border-stone-100">
            <h2
              className="text-xl font-semibold text-stone-800 mb-3"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              Data snapshot
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
              {[
                ['Picks', meta.total_recommendations],
                ['Cities', meta.cities.length],
                ['Contributors', meta.recommenders.length],
                ['Messages parsed', meta.source_message_count],
              ].map(([label, value]) => (
                <div key={String(label)} className="bg-stone-50 rounded-xl p-4">
                  <p
                    className="text-2xl font-bold text-amber-600"
                    style={{ fontFamily: 'var(--font-display)' }}
                  >
                    {value}
                  </p>
                  <p className="text-xs text-stone-400 mt-1">{label}</p>
                </div>
              ))}
            </div>
            {runDate && (
              <p className="text-xs text-stone-400 mt-4 text-center">
                Last updated: {runDate}
              </p>
            )}
          </section>
        )}
      </div>
    </main>
  )
}
