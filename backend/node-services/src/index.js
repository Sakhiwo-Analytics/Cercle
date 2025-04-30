require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const Sentry = require('@sentry/node');
const { ProfilingIntegration } = require('@sentry/profiling-node');
const { checkJwt, checkRole } = require('./middleware/auth');

// Initialize express app
const app = express();
const port = process.env.PORT || 8000;

// Initialize Sentry
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    // Enable HTTP calls tracing
    new Sentry.Integrations.Http({ tracing: true }),
    // Enable Express.js middleware tracing
    new Sentry.Integrations.Express({ app }),
    new ProfilingIntegration(),
  ],
  // Set tracesSampleRate to 1.0 for development, lower for production
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.2 : 1.0,
  // Set profilesSampleRate to 1.0 for development, lower for production
  profilesSampleRate: process.env.NODE_ENV === 'production' ? 0.2 : 1.0,
});

// The request handler must be the first middleware on the app
app.use(Sentry.Handlers.requestHandler());
// TracingHandler creates a trace for every incoming request
app.use(Sentry.Handlers.tracingHandler());

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(express.json()); // Parse JSON request body
app.use(morgan('dev')); // Request logging

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to Cercle API' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Protected routes
app.get('/api/user/profile', checkJwt, (req, res) => {
  // This route is protected, only authenticated users can access
  res.json({ 
    message: 'Protected user profile route',
    user: req.auth
  });
});

// User routes
const usersRouter = require('./routes/users');
app.use('/api/users', checkJwt, usersRouter);

// File routes
const filesRouter = require('./routes/files');
app.use('/api/files', checkJwt, filesRouter);

// Projects routes
const projectsRouter = require('./routes/projects');
app.use('/api/projects', checkJwt, projectsRouter);

// Research routes
const researchRouter = require('./routes/research');
app.use('/api/research', checkJwt, researchRouter);

// The error handler must be registered before any other error middleware and after all controllers
app.use(Sentry.Handlers.errorHandler());

// Error handling middleware
app.use((err, req, res, next) => {
  // Log error to console
  console.error(err.stack);
  
  // Add additional context to Sentry
  Sentry.withScope(scope => {
    // Add request details
    scope.setExtra('url', req.url);
    scope.setExtra('method', req.method);
    
    // Categorize errors
    if (err.name === 'AuthenticationError') {
      scope.setTag('error_type', 'auth');
      scope.setLevel('warning');
    } else if (err.name === 'DatabaseError') {
      scope.setTag('error_type', 'database');
      scope.setLevel('error');
    } else if (err.name === 'StorageError') {
      scope.setTag('error_type', 'storage');
      scope.setLevel('error');
    }
    
    // Capture exception with enhanced context
    Sentry.captureException(err);
  });
  
  // Send response to client
  res.status(err.status || 500).json({ 
    error: err.status === 401 ? 'Unauthorized' : 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined,
    // Include a Sentry event ID so users can reference it when reporting issues
    eventId: res.sentry
  });
});

// Start server
app.listen(port, () => {
  console.log(`Cercle API server running on port ${port}`);
});

module.exports = app; // For testing
