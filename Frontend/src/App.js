import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Comparison from './components/ComparisonTable';
import Recommendation from './components/Recommendation';
import AboutPage from './components/AboutUS'; 
import Chatbot from './components/Chatbot';

const App = () => {
  return (
    <Router>
      <Navbar /> {/* Navbar appears on all pages */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/comparison" element={<Comparison />} />
        <Route path="/recommendation" element={<Recommendation />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/chatbot" element={<Chatbot />} /> {/* Moved inside <Routes> */}
      </Routes>
    </Router>
  );
};

export default App;
