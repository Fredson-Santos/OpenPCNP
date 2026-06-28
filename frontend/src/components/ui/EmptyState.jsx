import React from 'react';
import { SearchX } from 'lucide-react';

export const EmptyState = ({ icon, title, description }) => {
  const IconComponent = icon || SearchX;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '3rem 2rem',
      textAlign: 'center',
      animation: 'fadeInUp 0.4s ease-out',
    }}>
      <div style={{
        width: 56,
        height: 56,
        borderRadius: 'var(--radius-lg)',
        background: 'var(--accent-blue-bg)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '1.25rem',
        color: 'var(--accent-blue)',
      }}>
        <IconComponent size={24} />
      </div>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
        {title || 'Nenhum resultado encontrado'}
      </h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: 360 }}>
        {description || 'Tente ajustar os filtros ou o termo de busca.'}
      </p>
    </div>
  );
};
