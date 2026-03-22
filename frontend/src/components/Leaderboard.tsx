import { useNavigate } from 'react-router-dom'
import type { Recommender } from '../types'

interface LeaderboardProps {
  recommenders: Recommender[]
  onSelect?: (name: string) => void
}

const MEDALS = ['🥇', '🥈', '🥉']

function TrustBar({ score }: { score: number }) {
  return (
    <div className="w-24 h-1.5 bg-stone-100 rounded-full overflow-hidden">
      <div
        className="h-full bg-amber-400 rounded-full"
        style={{ width: `${Math.round(score * 100)}%` }}
      />
    </div>
  )
}

export function Leaderboard({ recommenders, onSelect }: LeaderboardProps) {
  const navigate = useNavigate()

  function handleClick(name: string) {
    if (onSelect) {
      onSelect(name)
    } else {
      navigate(`/recommender/${encodeURIComponent(name)}`)
    }
  }

  if (recommenders.length === 0) {
    return (
      <p className="text-stone-400 text-center py-12">No contributors yet.</p>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {recommenders.map((rec, i) => (
        <button
          key={rec.name}
          className="flex items-center gap-4 bg-white rounded-xl border border-stone-100 px-4 py-3.5 hover:border-amber-200 hover:shadow-sm transition-all text-left w-full group"
          onClick={() => handleClick(rec.name)}
        >
          <span className="text-xl w-8 text-center flex-shrink-0">
            {i < 3 ? (
              MEDALS[i]
            ) : (
              <span className="text-stone-400 font-mono text-sm">#{i + 1}</span>
            )}
          </span>

          <div className="flex-1 min-w-0">
            <p className="font-semibold text-stone-800 group-hover:text-amber-700 transition-colors truncate">
              {rec.name}
            </p>
            {rec.top_cities.length > 0 && (
              <p className="text-xs text-stone-400 truncate">
                {rec.top_cities.slice(0, 3).join(' · ')}
              </p>
            )}
          </div>

          <div className="flex flex-col items-end gap-1 flex-shrink-0">
            <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-0.5 rounded-full">
              {rec.recommendation_count} picks
            </span>
            <TrustBar score={rec.trust_score} />
          </div>
        </button>
      ))}
    </div>
  )
}
