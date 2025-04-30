# Setting Up Supabase Authentication for Cercle

This guide explains how to set up and configure Supabase Authentication for the Cercle project, which replaces the previously planned Auth0 integration.

## 1. Enable Supabase Authentication

1. Log in to your [Supabase Dashboard](https://app.supabase.com)
2. Select your Cercle project
3. Navigate to the "Authentication" section in the left sidebar
4. Under "Providers", enable the authentication methods you want to use:
   - Email (recommended)
   - Social providers like Google, GitHub, etc. (optional)

## 2. Configure Email Templates

1. In the Authentication section, go to "Email Templates"
2. Customize the following templates to match your branding:
   - Confirmation Email
   - Invite Email
   - Magic Link Email
   - Reset Password Email

## 3. Configure Authentication Settings

1. Go to "URL Configuration"
   - Set the Site URL to your frontend URL (e.g., `https://app.cercle.com`)
   - Add any additional redirect URLs for local development

2. Go to "Email Templates"
   - Customize the sender name and email address

## 4. Database Schema and Migrations

Run the migration scripts to set up your database schema:

```bash
cd backend/node-services
node src/utils/db-migrate.js
```

This will create the following tables with appropriate Row Level Security (RLS) policies:

1. **users** - Extends Supabase auth.users with additional profile information
2. **files** - For file storage and management
3. **file_shares** - For sharing files between users
4. **projects** - For project management
5. **research_queries** - For research query history and results
6. **documents** - For writing assistant documents
7. **document_versions** - For document version history
8. **writing_suggestions** - For AI-generated writing suggestions

## 5. Frontend Integration

### Supabase Client Setup

Create a `supabaseClient.js` file to initialize the Supabase client:

```javascript
// src/supabaseClient.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### Authentication Context

Create an `AuthContext.js` file to manage authentication state:

```javascript
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

Create a `ProtectedRoute.js` component to secure routes:

```javascript
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

## 6. Role-Based Access Control

### Role Management in Database

Roles are stored in the `users` table in the `role` column. The default role is 'student'.

```sql
-- Example query to get a user's role
SELECT role FROM users WHERE id = auth.uid();

-- Example query to update a user's role
UPDATE users SET role = 'researcher' WHERE id = [user_id];
```

### Setting User Roles During Registration

When a user signs up, their role is automatically set to 'student' by default through the trigger function:

```javascript
// In the frontend, you can pass additional user metadata during signup
const signUp = async (email, password, fullName, role = 'student') => {
  const { data, error } = await supabase.auth.signUp({ 
    email, 
    password, 
    options: { 
      data: { 
        full_name: fullName,
        role: role 
      } 
    } 
  });
  return { data, error };
};
```

### Checking User Roles in Frontend

```javascript
// Using the AuthContext
const { user } = useAuth();
const userRole = user?.user_metadata?.role || 'student';

// Or directly from the database
const getUserRole = async () => {
  const { data, error } = await supabase
    .from('users')
    .select('role')
    .eq('id', user.id)
    .single();
    
  if (error) throw error;
  return data.role;
};
```

### Role-Based UI Components

```javascript
// Example of a role-based component
function RoleBasedComponent() {
  const { user } = useAuth();
  const userRole = user?.user_metadata?.role || 'student';
  
  return (
    <div>
      {userRole === 'admin' && <AdminPanel />}
      {userRole === 'researcher' && <ResearcherTools />}
      {userRole === 'student' && <StudentDashboard />}
    </div>
  );
}
```

## 7. Testing Authentication

1. Create a test user account
2. Verify email confirmation flow
3. Test login and logout
4. Test password reset
5. Verify role-based access control

## 8. Troubleshooting

- **JWT Token Issues**: Check the JWT expiration and refresh token configuration
- **CORS Errors**: Verify your site URL and redirect URLs in Supabase settings
- **Email Delivery**: Check spam folders and email delivery settings
- **Role-Based Access**: Verify user metadata is being set correctly

## Benefits of Supabase Authentication

- **Unified Platform**: Authentication, database, and storage all in one service
- **Simplified Security**: Built-in Row Level Security (RLS) for database and storage
- **Reduced External Dependencies**: No need for a separate auth service
- **Streamlined Development**: Consistent API patterns across services
