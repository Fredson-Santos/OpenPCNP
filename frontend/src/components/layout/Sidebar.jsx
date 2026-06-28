import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, FileSearch, TrendingUp, AlertTriangle,
  Shield, Menu, X
} from 'lucide-react';
import clsx from 'clsx';
import './Sidebar.css';

const menuItems = [
  { path: '/', label: 'Painel Geral', icon: <LayoutDashboard size={18} /> },
  { path: '/licitacoes', label: 'Licitações', icon: <FileSearch size={18} /> },
  { path: '/rankings', label: 'Rankings', icon: <TrendingUp size={18} /> },
  { path: '/alertas', label: 'Alertas', icon: <AlertTriangle size={18} /> },
];

export const Sidebar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <button
        className="sidebar-mobile-toggle"
        onClick={() => setMobileOpen(true)}
        aria-label="Abrir menu"
      >
        <Menu size={22} />
      </button>

      {mobileOpen && (
        <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />
      )}

      <aside className={clsx('sidebar', { 'sidebar--open': mobileOpen })}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo__icon">
              <Shield size={20} />
            </div>
            <div className="sidebar-logo__text">
              <span className="sidebar-logo__name">OpenPNCP</span>
              <span className="sidebar-logo__tag">Observatório</span>
            </div>
          </div>
          <button
            className="sidebar-close"
            onClick={() => setMobileOpen(false)}
            aria-label="Fechar menu"
          >
            <X size={18} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) => clsx('nav-item', { active: isActive })}
              onClick={() => setMobileOpen(false)}
            >
              <span className="nav-item__icon">{item.icon}</span>
              <span className="nav-item__label">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-footer__status">
            <span className="sidebar-footer__dot" />
            <span>Sistema operacional</span>
          </div>
          <span className="sidebar-footer__version">v3.0</span>
        </div>
      </aside>
    </>
  );
};
