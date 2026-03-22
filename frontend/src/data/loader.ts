import type { Meta, Recommendation } from '../types'

let recommendationsCache: Recommendation[] | null = null
let metaCache: Meta | null = null

export async function loadRecommendations(): Promise<Recommendation[]> {
  if (recommendationsCache) return recommendationsCache
  const res = await fetch('/data/recommendations.json')
  if (!res.ok) throw new Error(`Failed to load recommendations: ${res.status}`)
  recommendationsCache = (await res.json()) as Recommendation[]
  return recommendationsCache
}

export async function loadMeta(): Promise<Meta> {
  if (metaCache) return metaCache
  const res = await fetch('/data/meta.json')
  if (!res.ok) throw new Error(`Failed to load meta: ${res.status}`)
  metaCache = (await res.json()) as Meta
  return metaCache
}
