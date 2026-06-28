import React from 'react';

export const Skeleton = ({ width, height = '1rem', borderRadius, className = '' }) => {
  return (
    <div
      className={`skeleton ${className}`}
      style={{
        width: width || '100%',
        height,
        borderRadius: borderRadius || 'var(--radius-sm)',
      }}
    />
  );
};

export const SkeletonCard = () => (
  <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
    <Skeleton width="40%" height="0.875rem" />
    <Skeleton width="60%" height="1.75rem" />
    <Skeleton width="30%" height="0.75rem" />
  </div>
);

export const SkeletonRow = () => (
  <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
    <Skeleton width="2rem" height="2rem" borderRadius="50%" />
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <Skeleton width="70%" height="0.875rem" />
      <Skeleton width="40%" height="0.75rem" />
    </div>
    <Skeleton width="5rem" height="0.875rem" />
  </div>
);
