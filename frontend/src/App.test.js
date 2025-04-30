import { render, screen } from '@testing-library/react';
import App from './App';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Mock the Supabase client
jest.mock('@supabase/supabase-js', () => ({
  createClient: jest.fn(() => ({
    auth: {
      getSession: jest.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: jest.fn(() => ({ 
        data: { 
          subscription: { 
            unsubscribe: jest.fn() 
          } 
        } 
      }))
    }
  }))
}));

test('renders login page when not authenticated', () => {
  render(
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  );
  
  // Since we're mocking an unauthenticated state, we should see the login page
  const linkElement = screen.getByText(/Sign in to your account/i);
  expect(linkElement).toBeInTheDocument();
});
