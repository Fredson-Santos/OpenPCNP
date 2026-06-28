import React from 'react';
import './Tabs.css';

export const Tabs = ({ tabs, activeTab, onTabChange }) => {
  return (
    <div className="tabs">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={`tabs__item ${activeTab === tab.key ? 'tabs__item--active' : ''}`}
          onClick={() => onTabChange(tab.key)}
        >
          {tab.icon && <span className="tabs__icon">{tab.icon}</span>}
          <span>{tab.label}</span>
          {tab.count !== undefined && (
            <span className="tabs__count">{tab.count}</span>
          )}
        </button>
      ))}
    </div>
  );
};
