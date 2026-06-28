import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import { describe, it, expect } from 'vitest';

describe('App component', () => {
  it('renders the Sidebar with Home link', () => {
    render(<App />);
    const linkElements = screen.getAllByText(/Painel Geral/i);
    expect(linkElements.length).toBeGreaterThan(0);
  });
});
