import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { Home } from './pages/Home';
import { Licitacoes } from './pages/Licitacoes';
import { LicitacaoDetail } from './pages/LicitacaoDetail';
import { Rankings } from './pages/Rankings';
import { Alertas } from './pages/Alertas';

function App() {
  return (
    <Router>
      <div className="layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/licitacoes" element={<Licitacoes />} />
            <Route path="/licitacoes/:id" element={<LicitacaoDetail />} />
            <Route path="/rankings" element={<Rankings />} />
            <Route path="/alertas" element={<Alertas />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
