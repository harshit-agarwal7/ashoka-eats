interface FilterBarProps {
  categories: string[]
  activeCategory: string
  onCategoryChange: (cat: string) => void
  sortBy: string
  onSortChange: (sort: string) => void
}

export function FilterBar({
  categories,
  activeCategory,
  onCategoryChange,
  sortBy,
  onSortChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap gap-3 items-center">
      <div className="flex flex-wrap gap-2 flex-1">
        <button
          onClick={() => onCategoryChange('')}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors border ${
            activeCategory === ''
              ? 'bg-amber-600 text-white border-amber-600'
              : 'bg-white text-stone-600 border-stone-200 hover:border-stone-300 hover:bg-stone-50'
          }`}
        >
          All
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => onCategoryChange(cat)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium capitalize transition-colors border ${
              activeCategory === cat
                ? 'bg-amber-600 text-white border-amber-600'
                : 'bg-white text-stone-600 border-stone-200 hover:border-stone-300 hover:bg-stone-50'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <select
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value)}
        className="text-sm border border-stone-200 rounded-lg px-3 py-1.5 text-stone-600 bg-white focus:outline-none focus:ring-2 focus:ring-amber-300 cursor-pointer"
      >
        <option value="trust">Sort by Trust</option>
        <option value="alpha">Alphabetical</option>
      </select>
    </div>
  )
}
