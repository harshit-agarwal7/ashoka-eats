import { Link } from 'react-router-dom'
import type { Recommendation } from '../types'

const CATEGORY_STYLES: Record<string, string> = {
  food: 'bg-amber-100 text-amber-800 border-amber-200',
  drinks: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  cafe: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  dessert: 'bg-pink-100 text-pink-800 border-pink-200',
  other: 'bg-stone-100 text-stone-600 border-stone-200',
}

const CATEGORY_ICONS: Record<string, string> = {
  food: '🍽',
  drinks: '🍻',
  cafe: '☕',
  dessert: '🍮',
  other: '📍',
}

function TrustDots({ score }: { score: number }) {
  const filled = Math.round(score * 5)
  return (
    <span className="flex gap-0.5" title={`Trust score: ${Math.round(score * 100)}%`}>
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className={`text-sm ${i < filled ? 'text-amber-500' : 'text-stone-200'}`}
        >
          ●
        </span>
      ))}
    </span>
  )
}

interface RecommendationCardProps {
  rec: Recommendation
}

export function RecommendationCard({ rec }: RecommendationCardProps) {
  const catStyle = CATEGORY_STYLES[rec.category] ?? CATEGORY_STYLES.other
  const catIcon = CATEGORY_ICONS[rec.category] ?? '📍'

  return (
    <article className="bg-white rounded-2xl border border-stone-100 p-5 flex flex-col gap-3 hover:shadow-md hover:border-stone-200 transition-all duration-200 group">
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold text-stone-900 leading-snug font-display flex-1">
          {rec.place_name}
        </h3>
        <span
          className={`inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full border flex-shrink-0 capitalize ${catStyle}`}
        >
          <span>{catIcon}</span>
          {rec.category}
        </span>
      </div>

      <Link
        to={`/city/${rec.city_slug}`}
        className="inline-flex w-fit"
        aria-label={`Browse ${rec.city}`}
      >
        <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-sky-50 text-sky-700 border border-sky-200 hover:bg-sky-100 transition-colors">
          📍 {rec.city}
        </span>
      </Link>

      {rec.quotes.length > 0 && (
        <blockquote className="text-stone-600 text-sm leading-relaxed italic border-l-2 border-amber-300 pl-3 py-0.5">
          "{rec.quotes[0]}"
        </blockquote>
      )}

      <div className="flex items-center justify-between mt-auto pt-2 border-t border-stone-50">
        <Link
          to={`/recommender/${encodeURIComponent(rec.recommender_name)}`}
          className="text-sm font-medium text-stone-600 hover:text-amber-700 transition-colors"
        >
          {rec.recommender_name}
        </Link>
        <TrustDots score={rec.recommender_trust_score} />
      </div>
    </article>
  )
}
