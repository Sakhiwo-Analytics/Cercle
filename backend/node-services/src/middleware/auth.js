const { createClient } = require('@supabase/supabase-js');
const Sentry = require('@sentry/node');

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// Supabase JWT validation middleware
const checkJwt = async (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid token' });
  }
  
  const token = authHeader.split(' ')[1];
  
  try {
    // Verify the JWT token with Supabase
    const { data: { user }, error } = await supabase.auth.getUser(token);
    
    if (error) throw error;
    
    if (!user) {
      return res.status(401).json({ error: 'Invalid token' });
    }
    
    // Add user info to request object
    req.auth = {
      sub: user.id,
      email: user.email,
      claims: {
        'https://cercle.app/role': user.user_metadata?.role || 'student'
      }
    };
    
    // Set user context in Sentry for error tracking
    Sentry.configureScope((scope) => {
      scope.setUser({
        id: user.id,
        email: user.email,
        role: user.user_metadata?.role || 'student'
      });
    });
    
    next();
  } catch (err) {
    console.error('Token verification error:', err);
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Role-based access control middleware
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

module.exports = {
  checkJwt,
  checkRole
};
