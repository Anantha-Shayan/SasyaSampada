import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import { LanguageProvider } from './context/LanguageContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Advisory from './pages/Advisory';
import Weather from './pages/Weather';
import Chat from './pages/Chat';
import Market from './pages/Market';
import PestDetection from './pages/PestDetection';
import SoilCardUpload from './pages/SoilCardUpload';
import RecommendationResults from './pages/RecommendationResults';


function App() {
  return (
    <LanguageProvider>
      <UserProvider>
        <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="advisory" element={<Advisory />} />
              <Route path="weather" element={<Weather />} />
              <Route path="market" element={<Market />} />
              <Route path="pest" element={<PestDetection />} />
            </Route>
            <Route path="/soil-card-upload" element={<SoilCardUpload />} />
            <Route path="/recommendation-results" element={<RecommendationResults />} />
          </Routes>
          </div>
        </Router>
      </UserProvider>
    </LanguageProvider>
  );
}

export default App;
