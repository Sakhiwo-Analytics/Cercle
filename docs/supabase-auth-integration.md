# Supabase Authentication Integration Guide

This document provides detailed instructions for setting up and integrating Supabase Authentication in the Cercle application.

## Table of Contents

1. [Supabase Project Setup](#supabase-project-setup)
2. [Authentication Configuration](#authentication-configuration)
3. [Frontend Integration](#frontend-integration)
4. [Backend Integration](#backend-integration)
5. [Row Level Security (RLS)](#row-level-security)
6. [Testing Authentication Flow](#testing-authentication-flow)
7. [Troubleshooting](#troubleshooting)

## Supabase Project Setup

1. Create a Supabase project at [https://app.supabase.io](https://app.supabase.io)
2. Once your project is created, navigate to the project dashboard
3. Retrieve your project URL and anon key from the API settings section
4. Add these credentials to your environment files:
   - Frontend: `.env` file in the `frontend` directory
   - Node.js Backend: `.env` file in the `backend/node-services` directory
   - Python Backend: `.env` file in the `backend/python-services` directory

## Authentication Configuration

### Enable Authentication Methods

1. Navigate to Authentication > Settings in your Supabase dashboard
2. Enable the following authentication methods:
   - Email with password
   - Google OAuth (optional)
   - GitHub OAuth (optional)

### Configure Email Templates

1. Go to Authentication > Email Templates
2. Customize the following templates:
   - Confirmation email
   - Invitation email
   - Magic link email
   - Reset password email

### Set Up Redirect URLs

1. Go to Authentication > URL Configuration
2. Add the following redirect URLs:
   - For local development: `http://localhost:3000/auth/callback`
   - For deployed environments:
     - `https://dev.cercle.app/auth/callback`
     - `https://test.cercle.app/auth/callback`
     - `https://staging.cercle.app/auth/callback`

## Frontend Integration

The frontend integration uses the Supabase JavaScript client to handle authentication flows.

### AuthContext Setup

The `AuthContext.js` file provides a React context for managing authentication state:

```jsx
// src/contexts/AuthContext.js
import React, { createContext, useState, useEffect, useContext } from 'react';
import { supabase } from '../supabaseClient';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check active sessions and sets the user
    const getSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user || null);
      setLoading(false);
    };

    getSession();

    // Listen for changes on auth state
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user || null);
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  // Login with email and password
  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    return { data, error };
  };

  // Signup with email and password
  const signUp = async (email, password, fullName) => {
    const { data, error } = await supabase.auth.signUp({ 
      email, 
      password, 
      options: { 
        data: { full_name: fullName } 
      } 
    });
    return { data, error };
  };

  // Logout
  const signOut = async () => {
    const { error } = await supabase.auth.signOut();
    return { error };
  };

  // Reset password
  const resetPassword = async (email) => {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email);
    return { data, error };
  };

  // Update password
  const updatePassword = async (newPassword) => {
    const { data, error } = await supabase.auth.updateUser({ password: newPassword });
    return { data, error };
  };

  const value = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
```

### Protected Routes

The `ProtectedRoute.js` component ensures that only authenticated users can access certain routes:

```jsx
// src/components/ProtectedRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
}

export default ProtectedRoute;
```

## Backend Integration

### Node.js Backend

The Node.js backend uses the Supabase client to verify JWT tokens and interact with the database:

```javascript
// Middleware to verify Supabase JWT
const verifyToken = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const { data, error } = await supabase.auth.getUser(token);
    
    if (error) {
      return res.status(401).json({ error: 'Invalid token' });
    }
    
    req.user = data.user;
    next();
  } catch (error) {
    return res.status(500).json({ error: 'Failed to authenticate token' });
  }
};
```

### Python Backend

The Python FastAPI backend uses the Supabase Python client for authentication:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
        user = response.user
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

## Row Level Security (RLS)

Supabase uses PostgreSQL's Row Level Security to control access to table rows:

### Example RLS Policy for Projects Table

```sql
-- Enable RLS on the projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Create policy for users to see only their own projects
CREATE POLICY "Users can view their own projects" 
ON projects FOR SELECT 
USING (auth.uid() = user_id);

-- Create policy for users to insert their own projects
CREATE POLICY "Users can insert their own projects" 
ON projects FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Create policy for users to update their own projects
CREATE POLICY "Users can update their own projects" 
ON projects FOR UPDATE 
USING (auth.uid() = user_id);

-- Create policy for users to delete their own projects
CREATE POLICY "Users can delete their own projects" 
ON projects FOR DELETE 
USING (auth.uid() = user_id);
```

## Testing Authentication Flow

1. Start the application in development mode
2. Navigate to the signup page and create a new account
3. Verify that you receive a confirmation email (if enabled)
4. Log in with your credentials
5. Test protected routes to ensure they're only accessible when authenticated
6. Test logout functionality
7. Verify that you're redirected to the login page after logout

## Troubleshooting

### Common Issues

1. **JWT Token Verification Fails**
   - Check that you're using the correct Supabase URL and anon key
   - Ensure the token is being properly passed in the Authorization header

2. **CORS Errors**
   - Add your frontend URL to the allowed origins in Supabase dashboard

3. **Email Confirmation Not Working**
   - Check spam folder
   - Verify email templates are configured correctly
   - Ensure redirect URLs are properly set up

4. **RLS Policies Not Working**
   - Verify that RLS is enabled on the table
   - Check that the policy conditions match your data model
   - Test policies directly in the Supabase SQL editor

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [Supabase documentation](https://supabase.io/docs)
2. Search the [Supabase GitHub issues](https://github.com/supabase/supabase/issues)
3. Join the [Supabase Discord community](https://discord.supabase.com)
