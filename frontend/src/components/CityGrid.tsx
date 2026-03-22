import type { Recommendation } from '../types'

const CITY_EMOJIS: Record<string, string> = {
  'new-delhi': '🏛️',
  delhi: '🏛️',
  mumbai: '🌊',
  bengaluru: '🌿',
  bangalore: '🌿',
  kolkata: '🎭',
  chennai: '🌅',
  hyderabad: '💎',
  pune: '⛰️',
  jaipur: '🏰',
  goa: '🏖️',
  ahmedabad: '🕌',
  surat: '💫',
  lucknow: '🌹',
  chandigarh: '🌳',
  kochi: '🚢',
}

interface CityGridProps {
  cities: string[]
  recommendations: Recommendation[]
  onCityClick: (slug: string) => void
}

export function CityGrid({ cities, recommendations, onCityClick }: CityGridProps) {
  const countByCity: Record<string, number> = {}
  for (const rec of recommendations) {
    countByCity[rec.city] = (countByCity[rec.city] ?? 0) + 1
  }

  if (cities.length === 0) {
    return <p className="text-stone-400 text-center py-12">No cities yet.</p>
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {cities.map((city) => {
        const slug = city.toLowerCase().replace(/\s+/g, '-')
        const emoji = CITY_EMOJIS[slug] ?? '🍽️'
        const count = countByCity[city] ?? 0

        return (
          <button
            key={city}
            onClick={() => onCityClick(slug)}
            className="flex flex-col items-center gap-2 bg-white rounded-2xl border border-stone-100 p-6 hover:border-amber-300 hover:shadow-md transition-all duration-200 group cursor-pointer"
          >
            <span className="text-4xl">{emoji}</span>
            <span className="font-semibold text-stone-800 group-hover:text-amber-700 transition-colors text-sm text-center leading-tight">
              {city}
            </span>
            <span className="text-xs text-stone-400 bg-stone-50 px-2 py-0.5 rounded-full">
              {count} pick{count !== 1 ? 's' : ''}
            </span>
          </button>
        )
      })}
    </div>
  )
}
