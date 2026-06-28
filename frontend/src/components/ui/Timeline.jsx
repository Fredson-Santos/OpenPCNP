import React from 'react';
import './Timeline.css';

export const Timeline = ({ items }) => {
  if (!items || items.length === 0) return null;

  return (
    <div className="timeline">
      {items.map((item, index) => (
        <div key={item.id || index} className="timeline__item">
          <div className="timeline__marker">
            <div className={`timeline__dot ${index === 0 ? 'timeline__dot--active' : ''}`} />
            {index < items.length - 1 && <div className="timeline__line" />}
          </div>
          <div className="timeline__content">
            <div className="timeline__header">
              <span className="timeline__date">
                {new Date(item.data).toLocaleDateString('pt-BR', {
                  day: '2-digit', month: 'short', year: 'numeric',
                })}
              </span>
              {item.status && (
                <span className="timeline__status">{item.status}</span>
              )}
            </div>
            <p className="timeline__description">{item.descricao}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
