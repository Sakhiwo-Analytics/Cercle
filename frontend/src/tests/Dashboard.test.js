import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import { AuthProvider } from '../contexts/AuthContext';
import { supabase } from '../supabaseClient';

// Mock the Supabase client
jest.mock('../supabaseClient', () => ({
  supabase: {
    from: jest.fn().mockReturnThis(),
    select: jest.fn().mockReturnThis(),
    eq: jest.fn().mockReturnThis(),
    order: jest.fn().mockReturnThis(),
    limit: jest.fn().mockReturnThis()
  }
}));

// Mock the useAuth hook
jest.mock('../contexts/AuthContext', () => {
  const originalModule = jest.requireActual('../contexts/AuthContext');
  return {
    ...originalModule,
    useAuth: jest.fn(() => ({
      user: { id: 'user-123', email: 'test@example.com', user_metadata: { full_name: 'Test User' } },
      loading: false,
      getUserProfile: jest.fn().mockResolvedValue({
        id: 'user-123',
        full_name: 'Test User',
        role: 'student',
        institution: 'Test University'
      })
    }))
  };
});

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Mock Supabase responses
    // Projects
    supabase.from.mockImplementation((table) => {
      if (table === 'projects') {
        return {
          select: jest.fn().mockReturnThis(),
          eq: jest.fn().mockReturnThis(),
          order: jest.fn().mockReturnThis(),
          limit: jest.fn().mockResolvedValue({
            data: [
              { id: 'proj-1', title: 'Research Paper', description: 'AI Ethics Research', created_at: '2023-04-15T10:00:00Z' },
              { id: 'proj-2', title: 'Thesis Draft', description: 'Chapter 1-3', created_at: '2023-04-10T09:30:00Z' }
            ],
            error: null
          })
        };
      }
      
      // Research queries
      if (table === 'research_queries') {
        return {
          select: jest.fn().mockReturnThis(),
          eq: jest.fn().mockReturnThis(),
          order: jest.fn().mockReturnThis(),
          limit: jest.fn().mockResolvedValue({
            data: [
              { id: 'query-1', query_text: 'Impact of AI on education', created_at: '2023-04-18T14:20:00Z' },
              { id: 'query-2', query_text: 'Machine learning in healthcare', created_at: '2023-04-17T11:15:00Z' }
            ],
            error: null
          })
        };
      }
      
      // Documents
      if (table === 'documents') {
        return {
          select: jest.fn().mockReturnThis(),
          eq: jest.fn().mockReturnThis(),
          order: jest.fn().mockReturnThis(),
          limit: jest.fn().mockResolvedValue({
            data: [
              { id: 'doc-1', title: 'Literature Review', updated_at: '2023-04-19T16:45:00Z' },
              { id: 'doc-2', title: 'Methodology Section', updated_at: '2023-04-16T13:10:00Z' }
            ],
            error: null
          })
        };
      }
      
      return {
        select: jest.fn().mockReturnThis(),
        eq: jest.fn().mockReturnThis(),
        order: jest.fn().mockReturnThis(),
        limit: jest.fn().mockResolvedValue({ data: [], error: null })
      };
    });
  });

  test('renders dashboard with user information', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );
    
    // Wait for user profile to load
    await waitFor(() => {
      expect(screen.getByText(/welcome,\s*test user/i)).toBeInTheDocument();
    });
    
    // Check for institution
    await waitFor(() => {
      expect(screen.getByText(/test university/i)).toBeInTheDocument();
    });
  });

  test('displays recent projects', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );
    
    // Check for projects section
    await waitFor(() => {
      expect(screen.getByText(/recent projects/i)).toBeInTheDocument();
    });
    
    // Check for project items
    await waitFor(() => {
      expect(screen.getByText(/research paper/i)).toBeInTheDocument();
      expect(screen.getByText(/thesis draft/i)).toBeInTheDocument();
    });
  });

  test('displays recent research queries', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );
    
    // Check for research section
    await waitFor(() => {
      expect(screen.getByText(/recent research/i)).toBeInTheDocument();
    });
    
    // Check for research query items
    await waitFor(() => {
      expect(screen.getByText(/impact of ai on education/i)).toBeInTheDocument();
      expect(screen.getByText(/machine learning in healthcare/i)).toBeInTheDocument();
    });
  });

  test('displays recent documents', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );
    
    // Check for documents section
    await waitFor(() => {
      expect(screen.getByText(/recent documents/i)).toBeInTheDocument();
    });
    
    // Check for document items
    await waitFor(() => {
      expect(screen.getByText(/literature review/i)).toBeInTheDocument();
      expect(screen.getByText(/methodology section/i)).toBeInTheDocument();
    });
  });

  test('handles error states gracefully', async () => {
    // Mock an error response for projects
    supabase.from.mockImplementationOnce((table) => {
      if (table === 'projects') {
        return {
          select: jest.fn().mockReturnThis(),
          eq: jest.fn().mockReturnThis(),
          order: jest.fn().mockReturnThis(),
          limit: jest.fn().mockResolvedValue({
            data: null,
            error: { message: 'Error fetching projects' }
          })
        };
      }
      return {
        select: jest.fn().mockReturnThis(),
        eq: jest.fn().mockReturnThis(),
        order: jest.fn().mockReturnThis(),
        limit: jest.fn().mockResolvedValue({ data: [], error: null })
      };
    });

    render(
      <BrowserRouter>
        <AuthProvider>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );
    
    // Should show error message or fallback UI
    await waitFor(() => {
      expect(screen.getByText(/no recent projects/i)).toBeInTheDocument();
    });
  });
});
