import React, { useState } from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Research.css';

function Research() {
  const { supabase } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('query');
  const [libraryItems, setLibraryItems] = useState([
    { id: 1, title: 'Quantum Tunneling Paper', type: 'article', authors: 'A. Einstein, N. Bohr', year: 2024 },
    { id: 2, title: 'Machine Learning Applications in Research', type: 'book', authors: 'A. Turing, G. Hinton', year: 2023 },
    { id: 3, title: 'AI Ethics in Academia', type: 'paper', authors: 'S. Russell, P. Norvig', year: 2022 }
  ]);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setLoading(true);
    
    try {
      // In a real implementation, this would call your backend API
      // For now, we'll simulate a response after a delay
      setTimeout(() => {
        if (query.toLowerCase().includes('quantum')) {
          setResults({
            title: "Quantum Mechanics",
            content: `Quantum mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles. It is the foundation of all quantum physics including quantum chemistry, quantum field theory, quantum technology, and quantum information science.`,
            sections: [
              {
                title: "Basic Principles",
                content: "Quantum mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles."
              },
              {
                title: "Mathematical Formulation",
                content: "The mathematical formulations of quantum mechanics are abstract. They describe the wave-like behavior of subatomic particles using complex mathematical structures."
              }
            ],
            formulas: [
              {
                name: "Schrödinger Equation",
                latex: "i\\hbar\\frac{\\partial}{\\partial t}\\Psi(\\mathbf{r},t) = \\hat H\\Psi(\\mathbf{r},t)"
              }
            ],
            references: [
              {
                title: "Introduction to Quantum Mechanics",
                author: "David J. Griffiths",
                year: 2017
              },
              {
                title: "Quantum Physics",
                author: "Stephen Gasiorowicz",
                year: 2003
              }
            ]
          });
        } else {
          setResults({
            title: query,
            content: `Here are the research results for "${query}"`,
            sections: [
              {
                title: "Overview",
                content: `This is an overview of ${query}.`
              }
            ],
            references: []
          });
        }
        setLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error searching:', error);
      setLoading(false);
    }
  };

  const handleSaveToLibrary = () => {
    // In a real implementation, this would save to your database
    alert('Saved to library!');
  };

  const handlePinToNotes = () => {
    // In a real implementation, this would pin to user notes
    alert('Pinned to notes!');
  };

  return (
    <Layout>
      <div className="research-container">
        <div className="research-header">
          <h1>Research Canvas</h1>
          <div className="tab-navigation">
            <button 
              className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
              onClick={() => setActiveTab('query')}
            >
              Smart Query Engine
            </button>
            <button 
              className={`tab-button ${activeTab === 'amplifier' ? 'active' : ''}`}
              onClick={() => setActiveTab('amplifier')}
            >
              Research Amplifier
            </button>
            <button 
              className={`tab-button ${activeTab === 'library' ? 'active' : ''}`}
              onClick={() => setActiveTab('library')}
            >
              My Library
            </button>
          </div>
        </div>
        
        {activeTab === 'query' && (
          <div className="query-section">
            <form onSubmit={handleSearch} className="query-form">
              <input
                type="text"
                placeholder="Enter your research query..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="query-input"
              />
              <button 
                type="submit" 
                className="query-button"
                disabled={loading || !query.trim()}
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </form>
            
            {loading ? (
              <div className="loading-results">
                <div className="loading-spinner"></div>
                <p>Processing your query...</p>
              </div>
            ) : results ? (
              <div className="results-container">
                <div className="results-header">
                  <h2>{results.title}</h2>
                </div>
                <div className="results-content">
                  <p>{results.content}</p>
                  
                  {results.sections && results.sections.map((section, index) => (
                    <div key={index} className="results-section">
                      <h3>{section.title}</h3>
                      <p>{section.content}</p>
                    </div>
                  ))}
                  
                  {results.formulas && results.formulas.map((formula, index) => (
                    <div key={index} className="formula">
                      <p><strong>{formula.name}:</strong></p>
                      <p>{formula.latex}</p>
                    </div>
                  ))}
                  
                  {results.references && results.references.length > 0 && (
                    <div className="references">
                      <h3>References</h3>
                      {results.references.map((ref, index) => (
                        <div key={index} className="reference-item">
                          <p>
                            {ref.author} ({ref.year}). <em>{ref.title}</em>.
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="results-actions">
                  <button className="action-button" onClick={handlePinToNotes}>
                    <span className="action-icon">📌</span> Pin to Notes
                  </button>
                  <button className="action-button" onClick={handleSaveToLibrary}>
                    <span className="action-icon">💾</span> Save to Library
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        )}
        
        {activeTab === 'amplifier' && (
          <div className="amplifier-section">
            <p>Research Amplifier functionality will be implemented in the next phase.</p>
          </div>
        )}
        
        {activeTab === 'library' && (
          <div className="library-section">
            <h2>My Research Library</h2>
            <div className="library-grid">
              {libraryItems.map(item => (
                <div key={item.id} className="library-item">
                  <div className="library-item-content">
                    <h3>{item.title}</h3>
                    <p>{item.authors}</p>
                    <div className="library-meta">
                      <span className="library-type">{item.type}</span>
                      <span>{item.year}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default Research;
