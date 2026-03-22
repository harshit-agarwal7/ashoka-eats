import { Link, NavLink } from 'react-router-dom'

export function Nav() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm font-medium transition-colors ${
      isActive ? 'text-amber-700' : 'text-stone-500 hover:text-stone-800'
    }`

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-sm border-b border-stone-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-6">
        <Link
          to="/"
          className="font-display text-xl font-semibold text-stone-900 hover:text-amber-700 transition-colors flex-shrink-0"
          style={{ fontFamily: 'var(--font-display)' }}
        >
          🍽 Ashoka Eats
        </Link>

        <nav className="flex items-center gap-5">
          <NavLink to="/" end className={linkClass}>
            Home
          </NavLink>
          <NavLink to="/leaderboard" className={linkClass}>
            Leaderboard
          </NavLink>
          <NavLink to="/about" className={linkClass}>
            About
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
