import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/NotFound.css';

function NotFound() {
  const { user } = useAuth();
  
  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you are looking for doesn't exist or has been moved.</p>
        
        {user ? (
          <Link to="/dashboard" className="back-button">Back to Dashboard</Link>
        ) : (
          <Link to="/login" className="back-button">Back to Login</Link>
        )}
      </div>
    </div>
  );
}

export default NotFound;
