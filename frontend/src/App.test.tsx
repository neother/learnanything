import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import { AuthProvider } from './contexts/AuthContext';

test('renders app without crashing', () => {
  render(
    <AuthProvider>
      <App />
    </AuthProvider>
  );

  // Check that the main app content is rendered
  // App shows onboarding welcome screen first - there are multiple instances
  const welcomeTexts = screen.getAllByText(/Welcome to Smart Navigator/i);
  expect(welcomeTexts.length).toBeGreaterThan(0);
  expect(welcomeTexts[0]).toBeInTheDocument();
});
