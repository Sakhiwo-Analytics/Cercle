import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../pages/Login';
import { AuthProvider } from '../contexts/AuthContext';

// Mock the useAuth hook
jest.mock('../contexts/AuthContext', () => {
  const originalModule = jest.requireActual('../contexts/AuthContext');
  return {
    ...originalModule,
    useAuth: jest.fn(() => ({
      signIn: jest.fn().mockImplementation((email, password) => {
        if (email === 'test@example.com' && password === 'password123') {
          return { data: { user: { id: '123' } }, error: null };
        } else {
          return { data: null, error: { message: 'Invalid login credentials' } };
        }
      }),
      loading: false
    }))
  };
});

// Mock the react-router-dom's useNavigate
jest.mock('react-router-dom', () => {
  const originalModule = jest.requireActual('react-router-dom');
  return {
    ...originalModule,
    useNavigate: jest.fn(() => jest.fn())
  };
});

describe('Login Component', () => {
  const renderLoginComponent = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  test('renders login form with email and password fields', () => {
    renderLoginComponent();
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('shows validation errors for empty fields', async () => {
    renderLoginComponent();
    
    const signInButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(signInButton);
    
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  test('shows error message for invalid credentials', async () => {
    renderLoginComponent();
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const signInButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(signInButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid login credentials/i)).toBeInTheDocument();
    });
  });

  test('successfully logs in with valid credentials', async () => {
    const { useAuth } = require('../contexts/AuthContext');
    const { useNavigate } = require('react-router-dom');
    
    renderLoginComponent();
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const signInButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(signInButton);
    
    await waitFor(() => {
      expect(useAuth().signIn).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(useNavigate()).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('has a link to the signup page', () => {
    renderLoginComponent();
    
    const signupLink = screen.getByText(/don't have an account/i).closest('a');
    expect(signupLink).toHaveAttribute('href', '/signup');
  });
});
