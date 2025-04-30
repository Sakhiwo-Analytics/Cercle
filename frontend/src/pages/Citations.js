import React, { useState } from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Citations.css';

function Citations() {
  const { user } = useAuth();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('checker');
  const [citationResults, setCitationResults] = useState(null);
  const [citationStyle, setCitationStyle] = useState('apa');
  const [sourceQuery, setSourceQuery] = useState('');
  const [suggestedSources, setSuggestedSources] = useState(null);

  const handleCheckCitations = async () => {
    if (!content.trim()) return;
    
    setLoading(true);
    
    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/check-citations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.access_token}`
        },
        body: JSON.stringify({
          content
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to check citations');
      }
      
      const data = await response.json();
      setCitationResults(data);
    } catch (error) {
      console.error('Error checking citations:', error);
      alert('Failed to check citations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestSources = async () => {
    if (!sourceQuery.trim()) return;
    
    setLoading(true);
    
    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/suggest-sources', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.access_token}`
        },
        body: JSON.stringify({
          query: sourceQuery
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to suggest sources');
      }
      
      const data = await response.json();
      setSuggestedSources(data);
    } catch (error) {
      console.error('Error suggesting sources:', error);
      alert('Failed to suggest sources. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFormatCitation = async (source) => {
    setLoading(true);
    
    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/format-citation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.access_token}`
        },
        body: JSON.stringify({
          source,
          style: citationStyle
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to format citation');
      }
      
      const data = await response.json();
      
      // Update the source with the formatted citation
      const updatedSources = suggestedSources.sources.map(s => {
        if (s.title === source.title) {
          return { ...s, formatted_citation: data.formatted_citation };
        }
        return s;
      });
      
      setSuggestedSources({
        ...suggestedSources,
        sources: updatedSources
      });
    } catch (error) {
      console.error('Error formatting citation:', error);
      alert('Failed to format citation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCitation = (citation) => {
    navigator.clipboard.writeText(citation)
      .then(() => {
        alert('Citation copied to clipboard!');
      })
      .catch(err => {
        console.error('Failed to copy citation:', err);
        alert('Failed to copy citation. Please try again.');
      });
  };

  return (
    <Layout>
      <div className="citations-container">
        <div className="citations-header">
          <h1>Citation Assistant</h1>
          <div className="tab-navigation">
            <button 
              className={`tab-button ${activeTab === 'checker' ? 'active' : ''}`}
              onClick={() => setActiveTab('checker')}
            >
              Citation Checker
            </button>
            <button 
              className={`tab-button ${activeTab === 'sources' ? 'active' : ''}`}
              onClick={() => setActiveTab('sources')}
            >
              Source Suggestions
            </button>
          </div>
        </div>
        
        {activeTab === 'checker' && (
          <div className="citation-checker-section">
            <div className="checker-input">
              <textarea
                placeholder="Paste your text to check for statements that need citations..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="content-input"
                rows={10}
              />
              
              <button 
                className="check-button"
                onClick={handleCheckCitations}
                disabled={loading || !content.trim()}
              >
                {loading ? 'Checking...' : 'Check for Missing Citations'}
              </button>
            </div>
            
            {citationResults && !loading && (
              <div className="citation-results">
                <h2>Citation Analysis</h2>
                
                <div className="citation-summary">
                  <p>
                    <strong>Found {citationResults.statements_needing_citation.length} statements</strong> that may require citations.
                  </p>
                </div>
                
                <div className="citation-statements">
                  {citationResults.statements_needing_citation.map((statement, index) => (
                    <div key={index} className="citation-statement">
                      <div className="statement-content">
                        <p>"{statement.text}"</p>
                      </div>
                      <div className="statement-reason">
                        <p><strong>Reason:</strong> {statement.reason}</p>
                      </div>
                      <div className="statement-suggestion">
                        <p><strong>Suggestion:</strong> {statement.suggestion}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'sources' && (
          <div className="source-suggestions-section">
            <div className="source-search">
              <div className="search-controls">
                <input
                  type="text"
                  placeholder="Enter a topic or statement to find relevant sources..."
                  value={sourceQuery}
                  onChange={(e) => setSourceQuery(e.target.value)}
                  className="source-query-input"
                />
                
                <select 
                  value={citationStyle} 
                  onChange={(e) => setCitationStyle(e.target.value)}
                  className="citation-style-select"
                >
                  <option value="apa">APA</option>
                  <option value="mla">MLA</option>
                  <option value="chicago">Chicago</option>
                  <option value="harvard">Harvard</option>
                  <option value="ieee">IEEE</option>
                </select>
              </div>
              
              <button 
                className="search-button"
                onClick={handleSuggestSources}
                disabled={loading || !sourceQuery.trim()}
              >
                {loading ? 'Searching...' : 'Find Sources'}
              </button>
            </div>
            
            {suggestedSources && !loading && (
              <div className="suggested-sources">
                <h2>Suggested Sources</h2>
                
                <div className="sources-list">
                  {suggestedSources.sources.map((source, index) => (
                    <div key={index} className="source-item">
                      <div className="source-details">
                        <h3>{source.title}</h3>
                        <p><strong>Authors:</strong> {source.authors}</p>
                        <p><strong>Year:</strong> {source.year}</p>
                        <p><strong>Publication:</strong> {source.publication}</p>
                        {source.url && <p><strong>URL:</strong> <a href={source.url} target="_blank" rel="noopener noreferrer">{source.url}</a></p>}
                      </div>
                      
                      {source.formatted_citation ? (
                        <div className="formatted-citation">
                          <h4>{citationStyle.toUpperCase()} Citation</h4>
                          <p className="citation-text">{source.formatted_citation}</p>
                          <button 
                            className="copy-button"
                            onClick={() => handleCopyCitation(source.formatted_citation)}
                          >
                            Copy Citation
                          </button>
                        </div>
                      ) : (
                        <button 
                          className="format-button"
                          onClick={() => handleFormatCitation(source)}
                          disabled={loading}
                        >
                          Format as {citationStyle.toUpperCase()}
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}

export default Citations;
