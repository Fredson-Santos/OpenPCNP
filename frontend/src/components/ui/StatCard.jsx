import React from 'react';
import './StatCard.css';

export const StatCard = ({ icon, label, value, detail, accentColor = 'blue' }) => {
  return (
    <div className={`stat-card stat-card--${accentColor}`}>
      <div className="stat-card__icon">
        {icon}
      </div>
      <div className="stat-card__body">
        <span className="stat-card__label">{label}</span>
        <span className="stat-card__value">{value}</span>
        {detail && <span className="stat-card__detail">{detail}</span>}
      </div>
    </div>
  );
};
