import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import RestaurantFinder from "./app/page"
import RestaurantDetail from "./pages/restaurant-detail"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RestaurantFinder />} />
        <Route path="/restaurant/:id" element={<RestaurantDetail />} />
      </Routes>
    </Router>
  )
}

export default App