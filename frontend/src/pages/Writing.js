import React, { useState } from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Writing.css';

function Writing() {
  const { supabase } = useAuth();
  const [content, setContent] = useState('');
  const [suggestions, setSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('editor');
  const [documents, setDocuments] = useState([
    { id: 1, title: 'Research Paper Draft', lastEdited: '2 hours ago' },
    { id: 2, title: 'Literature Review Notes', lastEdited: '1 day ago' },
    { id: 3, title: 'Conference Abstract', lastEdited: '3 days ago' }
  ]);

  const handleAssistRequest = async () => {
    if (!content.trim()) return;
    
    setLoading(true);
    
    try {
      // In a real implementation, this would call your backend API
      // For now, we'll simulate a response after a delay
      setTimeout(() => {
        setSuggestions({
          grammar: [
            { original: "The data show that", suggestion: "The data shows that" },
            { original: "between the subjects", suggestion: "among the subjects" }
          ],
          style: [
            { original: "very important", suggestion: "crucial" },
            { original: "a lot of", suggestion: "numerous" }
          ],
          citations: [
            { text: "Consider citing Smith et al. (2022) for the methodology section." },
            { text: "The claim about quantum effects should be supported by a reference." }
          ],
          improved: content.replace("very important", "crucial").replace("a lot of", "numerous")
        });
        setLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error getting writing assistance:', error);
      setLoading(false);
    }
  };

  const handleApplySuggestion = (original, suggestion) => {
    setContent(content.replace(original, suggestion));
  };

  const handleApplyAll = () => {
    if (!suggestions) return;
    
    let updatedContent = content;
    
    suggestions.grammar.forEach(item => {
      updatedContent = updatedContent.replace(item.original, item.suggestion);
    });
    
    suggestions.style.forEach(item => {
      updatedContent = updatedContent.replace(item.original, item.suggestion);
    });
    
    setContent(updatedContent);
  };

  const handleSave = () => {
    // In a real implementation, this would save to your database
    alert('Document saved!');
  };

  return (
    <Layout>
      <div className="writing-container">
        <div className="writing-header">
          <h1>Writing Assistant</h1>
          <div className="tab-navigation">
            <button 
              className={`tab-button ${activeTab === 'editor' ? 'active' : ''}`}
              onClick={() => setActiveTab('editor')}
            >
              Editor
            </button>
            <button 
              className={`tab-button ${activeTab === 'documents' ? 'active' : ''}`}
              onClick={() => setActiveTab('documents')}
            >
              My Documents
            </button>
            <button 
              className={`tab-button ${activeTab === 'templates' ? 'active' : ''}`}
              onClick={() => setActiveTab('templates')}
            >
              Templates
            </button>
          </div>
        </div>
        
        {activeTab === 'editor' && (
          <div className="editor-section">
            <div className="editor-toolbar">
              <div className="document-title">
                <input 
                  type="text" 
                  placeholder="Untitled Document" 
                  className="title-input"
                />
              </div>
              <div className="toolbar-actions">
                <button className="toolbar-button" onClick={handleSave}>
                  <span className="button-icon">💾</span> Save
                </button>
                <button 
                  className="toolbar-button assist-button" 
                  onClick={handleAssistRequest}
                  disabled={loading || !content.trim()}
                >
                  <span className="button-icon">✨</span> 
                  {loading ? 'Processing...' : 'Get Assistance'}
                </button>
              </div>
            </div>
            
            <div className="editor-content">
              <div className="editor-main">
                <textarea
                  className="content-editor"
                  placeholder="Start writing or paste your text here..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                />
              </div>
              
              {suggestions && (
                <div className="suggestions-panel">
                  <div className="panel-header">
                    <h3>Writing Suggestions</h3>
                    <button 
                      className="apply-all-button"
                      onClick={handleApplyAll}
                    >
                      Apply All
                    </button>
                  </div>
                  
                  <div className="panel-content">
                    {suggestions.grammar.length > 0 && (
                      <div className="suggestion-section">
                        <h4>Grammar</h4>
                        {suggestions.grammar.map((item, index) => (
                          <div key={`grammar-${index}`} className="suggestion-item">
                            <p>
                              <span className="original">"{item.original}"</span> → 
                              <span className="suggestion">"{item.suggestion}"</span>
                            </p>
                            <button 
                              className="apply-button"
                              onClick={() => handleApplySuggestion(item.original, item.suggestion)}
                            >
                              Apply
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {suggestions.style.length > 0 && (
                      <div className="suggestion-section">
                        <h4>Style</h4>
                        {suggestions.style.map((item, index) => (
                          <div key={`style-${index}`} className="suggestion-item">
                            <p>
                              <span className="original">"{item.original}"</span> → 
                              <span className="suggestion">"{item.suggestion}"</span>
                            </p>
                            <button 
                              className="apply-button"
                              onClick={() => handleApplySuggestion(item.original, item.suggestion)}
                            >
                              Apply
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {suggestions.citations.length > 0 && (
                      <div className="suggestion-section">
                        <h4>Citations</h4>
                        {suggestions.citations.map((item, index) => (
                          <div key={`citation-${index}`} className="suggestion-item citation">
                            <p>{item.text}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        {activeTab === 'documents' && (
          <div className="documents-section">
            <div className="section-header">
              <h2>My Documents</h2>
              <button className="new-document-button">
                <span>+</span> New Document
              </button>
            </div>
            
            <div className="documents-list">
              {documents.map(doc => (
                <div key={doc.id} className="document-item">
                  <div className="document-icon">📄</div>
                  <div className="document-info">
                    <h3>{doc.title}</h3>
                    <p>Last edited: {doc.lastEdited}</p>
                  </div>
                  <div className="document-actions">
                    <button className="action-button">
                      <span className="button-icon">✏️</span>
                    </button>
                    <button className="action-button">
                      <span className="button-icon">🗑️</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'templates' && (
          <div className="templates-section">
            <h2>Document Templates</h2>
            <p>Templates will be implemented in the next phase.</p>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default Writing;
