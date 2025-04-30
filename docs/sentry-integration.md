# Sentry Integration for Cercle

This document outlines how Sentry is integrated into the Cercle project for error tracking and monitoring.

## Overview

Sentry is used to track errors and exceptions across the Cercle application. It provides:

- Real-time error tracking
- User context for errors
- Performance monitoring
- Detailed error reports with stack traces

## Backend Integration

The Node.js backend is configured to use Sentry for error tracking with the following features:

### Error Categorization

Errors are categorized into specific types for better tracking and alerting:

- `AuthenticationError`: Issues with user authentication
- `AuthorizationError`: Permission-related issues
- `DatabaseError`: Database connection or query issues
- `StorageError`: Supabase Storage-related issues
- `ValidationError`: Input validation failures
- `NotFoundError`: Resource not found errors

### User Context

When a user is authenticated, their information is added to the Sentry context:

```javascript
Sentry.configureScope((scope) => {
  scope.setUser({
    id: user.id,
    email: user.email,
    role: user.role || 'student'
  });
});
```

This allows you to track which users are experiencing errors and filter by user role.

## Setting Up Alert Rules

To complete the Sentry integration, you should set up alert rules in the Sentry dashboard:

1. Log in to your [Sentry Dashboard](https://sentry.io)
2. Navigate to **Alerts** > **Rules**
3. Create the following alert rules:

### Authentication Errors

- **Rule Name**: Authentication Failures
- **Conditions**: 
  - When: The error message contains "authentication" or "auth"
  - Or: The error's tag "error_type" equals "auth"
- **Actions**: 
  - Send email to your team
  - Send Slack notification (if configured)

### Database Errors

- **Rule Name**: Database Issues
- **Conditions**: 
  - When: The error's tag "error_type" equals "database"
- **Actions**: 
  - Send email to your team
  - Send Slack notification (if configured)

### Storage Errors

- **Rule Name**: Supabase Storage Issues
- **Conditions**: 
  - When: The error's tag "error_type" equals "storage"
- **Actions**: 
  - Send email to your team
  - Send Slack notification (if configured)

## Monitoring Dashboard

Create a custom dashboard in Sentry to monitor:

1. Error rates by type
2. User-impacting issues
3. Performance metrics

## Best Practices

When developing new features for Cercle:

1. Use the appropriate error class for different types of errors
2. Add context to errors with `Sentry.withScope()`
3. Use `Sentry.captureMessage()` for important non-error events
4. Set appropriate severity levels for different types of issues

## Troubleshooting

If errors are not appearing in Sentry:

1. Verify that `SENTRY_DSN` is correctly set in your `.env` file
2. Check that Sentry initialization happens before any potential errors
3. Ensure error handling middleware is correctly configured

## Related Files

- `src/utils/errors.js`: Custom error classes
- `src/middleware/auth.js`: User context for Sentry
- `src/index.js`: Sentry initialization and error handlers
