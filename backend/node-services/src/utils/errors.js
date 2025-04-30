/**
 * Custom error classes for Cercle application
 * These help categorize errors for better tracking in Sentry
 */

class AuthenticationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'AuthenticationError';
    this.status = 401;
  }
}

class AuthorizationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'AuthorizationError';
    this.status = 403;
  }
}

class DatabaseError extends Error {
  constructor(message) {
    super(message);
    this.name = 'DatabaseError';
    this.status = 500;
  }
}

class StorageError extends Error {
  constructor(message) {
    super(message);
    this.name = 'StorageError';
    this.status = 500;
  }
}

class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
    this.status = 400;
  }
}

class NotFoundError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NotFoundError';
    this.status = 404;
  }
}

module.exports = {
  AuthenticationError,
  AuthorizationError,
  DatabaseError,
  StorageError,
  ValidationError,
  NotFoundError
};
