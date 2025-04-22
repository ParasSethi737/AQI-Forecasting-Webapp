import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Forecast from './pages/Forecast';
import History from './pages/History';
import Analytics from './pages/Analytics';
import Contact from './pages/Contact';
import CurrentConditions from './pages/CurrentConditions'; 
import LandingPage from './pages/Landing';

function App() {
  return (
    <Router>
      <div className="App">
        <div className="ContentContainer">
          <NavBar />
          <main>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/current" element={<CurrentConditions />} />
              <Route path="/forecast" element={<Forecast />} />
              <Route path="/history" element={<History />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/contact" element={<Contact />} />
            </Routes>
          </main>
        </div>

        <footer>
          <p>&copy; 2025 Paras Sethi</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
