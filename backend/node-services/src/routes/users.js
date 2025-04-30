const express = require('express');
const router = express.Router();
const { createClient } = require('@supabase/supabase-js');
const { AuthenticationError, AuthorizationError, DatabaseError, NotFoundError } = require('../utils/errors');
const Sentry = require('@sentry/node');

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// Middleware to check user roles
const checkRole = (allowedRoles) => {
  return (req, res, next) => {
    const userRole = req.auth.claims['https://cercle.app/role'] || 'student';
    
    if (allowedRoles.includes(userRole)) {
      next();
    } else {
      res.status(403).json({ error: 'Insufficient permissions' });
    }
  };
};

// Get user profile
router.get('/profile', async (req, res) => {
  try {
    const userId = req.auth.sub;
    
    // Get user from Supabase Auth
    const { data: { user }, error: authError } = await supabase.auth.admin.getUserById(userId);
    
    if (authError) throw new AuthenticationError(`Failed to update user: ${authError.message}`);
    
    // Get extended user profile from database
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('auth_id', userId)
      .single();
    
    if (error && error.code !== 'PGRST116') { // PGRST116 is 'not found'
      throw new DatabaseError(`Failed to fetch user profile: ${error.message}`);
    }
    
    if (!data) {
      // Log this event in Sentry as it might indicate a sync issue
      Sentry.captureMessage('User found in auth but not in database', {
        level: 'warning',
        tags: { user_id: userId }
      });
      
      // Return basic profile from Supabase Auth
      return res.json({
        id: user.id,
        email: user.email,
        name: user.user_metadata?.name,
        role: user.user_metadata?.role || 'student',
        institution: user.user_metadata?.institution,
        field_of_study: user.user_metadata?.field_of_study,
        message: 'Basic profile. Please complete registration.'
      });
    }
    
    res.json(data);
  } catch (err) {
    console.error('Error fetching user profile:', err);
    
    // Set appropriate status code based on error type
    const statusCode = err.status || 500;
    
    res.status(statusCode).json({ 
      error: statusCode === 401 ? 'Authentication failed' : 'Failed to fetch user profile',
      message: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
  }
});

// Create or update user profile
router.post('/profile', async (req, res) => {
  try {
    const userId = req.auth.sub;
    const { name, email, role, institution, field_of_study } = req.body;
    
    // Validate role
    if (role && !['student', 'researcher'].includes(role)) {
      return res.status(400).json({ error: 'Invalid role. Must be "student" or "researcher"' });
    }
    
    // Update user metadata in Supabase Auth
    const { error: authError } = await supabase.auth.admin.updateUserById(
      userId,
      { 
        user_metadata: { 
          role: role || 'student',
          name,
          institution,
          field_of_study
        }
      }
    );
    
    if (authError) throw new AuthenticationError(`Failed to update user: ${authError.message}`);
    
    // Check if user exists in our extended profiles table
    const { data: existingUser } = await supabase
      .from('users')
      .select('id')
      .eq('auth_id', userId)
      .single();
    
    if (existingUser) {
      // Update existing extended profile
      const { data, error } = await supabase
        .from('users')
        .update({
          name,
          email,
          role: role || 'student',
          institution,
          field_of_study,
          updated_at: new Date()
        })
        .eq('auth_id', userId)
        .select()
        .single();
      
      if (error) throw error;
      
      res.json(data);
    } else {
      // Create new extended profile
      const { data, error } = await supabase
        .from('users')
        .insert({
          auth_id: userId,
          name,
          email,
          role: role || 'student',
          institution,
          field_of_study,
          created_at: new Date(),
          updated_at: new Date()
        })
        .select()
        .single();
      
      if (error) throw error;
      
      res.status(201).json(data);
    }
  } catch (err) {
    console.error('Error updating user profile:', err);
    res.status(500).json({ error: 'Failed to update user profile' });
  }
});

// Get all users (admin only)
router.get('/', checkRole(['admin']), async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*');
    
    if (error) throw error;
    
    res.json(data);
  } catch (err) {
    console.error('Error fetching users:', err);
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

module.exports = router;
