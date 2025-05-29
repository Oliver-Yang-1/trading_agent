import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import InputForm from './pages/InputForm';
import AnalysisResult from './pages/AnalysisResult';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <div className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<InputForm />} />
            <Route path="/result" element={<AnalysisResult />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App; 