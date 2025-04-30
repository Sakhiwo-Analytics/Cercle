import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Layout.css';

function Layout({ children }) {
  const { user, signOut } = useAuth();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await signOut();
      // Redirect is handled by the auth state change in AuthContext
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="logo">
          <Link to="/dashboard">Cercle</Link>
        </div>
        <nav className="nav">
          <ul className="nav-list">
            <li className={`nav-item ${isActive('/dashboard')}`}>
              <Link to="/dashboard">Dashboard</Link>
            </li>
            <li className={`nav-item ${isActive('/research')}`}>
              <Link to="/research">Research</Link>
            </li>
            <li className={`nav-item ${isActive('/writing')}`}>
              <Link to="/writing">Writing</Link>
            </li>
            <li className={`nav-item ${isActive('/notes')}`}>
              <Link to="/notes">AI Notebook</Link>
            </li>
            <li className={`nav-item ${isActive('/citations')}`}>
              <Link to="/citations">Citations</Link>
            </li>
            <li className={`nav-item ${isActive('/projects')}`}>
              <Link to="/projects">Projects</Link>
            </li>
          </ul>
        </nav>
        <div className="user-menu">
          <div className="user-info">
            <span className="user-name">{user?.email}</span>
          </div>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>
      <main className="main-content">
        {children}
      </main>
      <footer className="footer">
        <div className="footer-content">
          <p>&copy; {new Date().getFullYear()} Cercle - Academic Research & Writing Assistant</p>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
