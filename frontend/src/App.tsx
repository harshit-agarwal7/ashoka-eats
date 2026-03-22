import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Nav } from './components/Nav'
import { Home } from './pages/Home'
import { CityPage } from './pages/CityPage'
import { RecommenderPage } from './pages/RecommenderPage'
import { CategoryPage } from './pages/CategoryPage'
import { LeaderboardPage } from './pages/LeaderboardPage'
import { About } from './pages/About'

function NotFound() {
  return (
    <div className="max-w-md mx-auto text-center py-24 px-6">
      <p className="text-6xl mb-4">🍽️</p>
      <h1 className="text-2xl font-bold text-stone-800 mb-2">Page not found</h1>
      <p className="text-stone-400 mb-6">The page you're looking for doesn't exist.</p>
      <a
        href="/"
        className="inline-block px-5 py-2.5 bg-amber-600 text-white rounded-xl text-sm font-medium hover:bg-amber-700 transition-colors"
      >
        Back to home
      </a>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-stone-50">
        <Nav />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/city/:slug" element={<CityPage />} />
          <Route path="/recommender/:name" element={<RecommenderPage />} />
          <Route path="/category/:slug" element={<CategoryPage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        <footer className="mt-16 border-t border-stone-100 py-8 text-center text-xs text-stone-400">
          <p>Ashoka Eats · Alumni food picks · Data from WhatsApp group chat</p>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
