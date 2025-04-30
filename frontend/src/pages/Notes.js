import React, { useState } from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Notes.css';

// Mind Map Visualization Component
function MindMapVisualization({ data }) {
  return (
    <div className="mind-map-visualization">
      {!data ? (
        <p>No mind map data available</p>
      ) : (
        <div className="mind-map-content">
          <div className="mind-map-root">
            <div className="node root-node">{data.central_topic}</div>
            <div className="branches">
              {data.branches && data.branches.map((branch, index) => (
                <div key={index} className="branch">
                  <div className="node branch-node">{branch.topic}</div>
                  <div className="sub-branches">
                    {branch.subtopics && branch.subtopics.map((subtopic, idx) => (
                      <div key={idx} className="node sub-node">{subtopic}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Flashcard Study Interface Component
function FlashcardStudyInterface({ flashcards }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  
  if (!flashcards || flashcards.length === 0) {
    return <p>No flashcards available</p>;
  }
  
  const handleNext = () => {
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setFlipped(false);
    }
  };
  
  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setFlipped(false);
    }
  };
  
  const handleFlip = () => {
    setFlipped(!flipped);
  };
  
  return (
    <div className="flashcard-study">
      <div className="flashcard-progress">
        <span>{currentIndex + 1} of {flashcards.length}</span>
      </div>
      
      <div 
        className={`flashcard ${flipped ? 'flipped' : ''}`}
        onClick={handleFlip}
      >
        <div className="flashcard-inner">
          <div className="flashcard-front">
            <p>{flashcards[currentIndex].question}</p>
          </div>
          <div className="flashcard-back">
            <p>{flashcards[currentIndex].answer}</p>
          </div>
        </div>
      </div>
      
      <div className="flashcard-controls">
        <button 
          className="flashcard-button"
          onClick={handlePrevious}
          disabled={currentIndex === 0}
        >
          Previous
        </button>
        <button 
          className="flashcard-button flip-button"
          onClick={handleFlip}
        >
          Flip
        </button>
        <button 
          className="flashcard-button"
          onClick={handleNext}
          disabled={currentIndex === flashcards.length - 1}
        >
          Next
        </button>
      </div>
    </div>
  );
}

function Notes() {
  const { user } = useAuth();
  const [content, setContent] = useState('');
  const [format, setFormat] = useState('outline');
  const [subject, setSubject] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedNotes, setGeneratedNotes] = useState(null);
  const [activeTab, setActiveTab] = useState('notes');
  const [savedNotes, setSavedNotes] = useState([
    { id: 1, title: 'Quantum Physics Notes', format: 'outline', date: '2 days ago' },
    { id: 2, title: 'Machine Learning Concepts', format: 'cornell', date: '1 week ago' },
    { id: 3, title: 'History of Computing', format: 'mindmap', date: '2 weeks ago' }
  ]);

  const handleGenerateNotes = async () => {
    if (!content.trim()) return;
    
    setLoading(true);
    
    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/generate-notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.access_token}`
        },
        body: JSON.stringify({
          content,
          format_type: format,
          subject: subject || undefined
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate notes');
      }
      
      const data = await response.json();
      setGeneratedNotes(data);
    } catch (error) {
      console.error('Error generating notes:', error);
      alert('Failed to generate notes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMindMap = async () => {
    if (!content.trim()) return;
    
    setLoading(true);
    
    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/generate-mindmap', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.access_token}`
        },
        body: JSON.stringify({
          content,
          subject: subject || undefined
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate mind map');
      }
      
      const data = await response.json();
      setGeneratedNotes({
        ...data,
        format: 'mindmap'
      });
    } catch (error) {
      console.error('Error generating mind map:', error);
      alert('Failed to generate mind map. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFlashcards = async () => {
    if (!content.trim()) return;
    
    setLoading(true);
    
    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/generate-flashcards', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.access_token}`
        },
        body: JSON.stringify({
          content,
          subject: subject || undefined
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate flashcards');
      }
      
      const data = await response.json();
      setGeneratedNotes({
        ...data,
        format: 'flashcards'
      });
    } catch (error) {
      console.error('Error generating flashcards:', error);
      alert('Failed to generate flashcards. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNotes = () => {
    if (!generatedNotes) return;
    
    // In a real implementation, this would save to your database
    alert('Notes saved successfully!');
    
    // Add to saved notes (simulated)
    const newNote = {
      id: savedNotes.length + 1,
      title: subject || 'Untitled Notes',
      format: format,
      date: 'Just now'
    };
    
    setSavedNotes([newNote, ...savedNotes]);
  };

  return (
    <Layout>
      <div className="notes-container">
        <div className="notes-header">
          <h1>AI Notebook</h1>
          <div className="tab-navigation">
            <button 
              className={`tab-button ${activeTab === 'notes' ? 'active' : ''}`}
              onClick={() => setActiveTab('notes')}
            >
              Auto-Notes
            </button>
            <button 
              className={`tab-button ${activeTab === 'mindmap' ? 'active' : ''}`}
              onClick={() => setActiveTab('mindmap')}
            >
              Mind Maps
            </button>
            <button 
              className={`tab-button ${activeTab === 'flashcards' ? 'active' : ''}`}
              onClick={() => setActiveTab('flashcards')}
            >
              Flashcards
            </button>
            <button 
              className={`tab-button ${activeTab === 'saved' ? 'active' : ''}`}
              onClick={() => setActiveTab('saved')}
            >
              Saved Notes
            </button>
          </div>
        </div>
        
        {(activeTab === 'notes' || activeTab === 'mindmap' || activeTab === 'flashcards') && (
          <div className="notes-input-section">
            <div className="input-controls">
              <input
                type="text"
                placeholder="Subject (optional)"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="subject-input"
              />
              
              {activeTab === 'notes' && (
                <select 
                  value={format} 
                  onChange={(e) => setFormat(e.target.value)}
                  className="format-select"
                >
                  <option value="outline">Outline</option>
                  <option value="cornell">Cornell Notes</option>
                  <option value="summary">Summary</option>
                  <option value="detailed">Detailed Notes</option>
                </select>
              )}
            </div>
            
            <textarea
              placeholder="Paste your lecture notes, article, or any text you want to convert..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="content-input"
              rows={10}
            />
            
            <div className="generate-actions">
              {activeTab === 'notes' && (
                <button 
                  className="generate-button"
                  onClick={handleGenerateNotes}
                  disabled={loading || !content.trim()}
                >
                  {loading ? 'Generating...' : 'Generate Structured Notes'}
                </button>
              )}
              
              {activeTab === 'mindmap' && (
                <button 
                  className="generate-button"
                  onClick={handleGenerateMindMap}
                  disabled={loading || !content.trim()}
                >
                  {loading ? 'Generating...' : 'Generate Mind Map'}
                </button>
              )}
              
              {activeTab === 'flashcards' && (
                <button 
                  className="generate-button"
                  onClick={handleGenerateFlashcards}
                  disabled={loading || !content.trim()}
                >
                  {loading ? 'Generating...' : 'Generate Flashcards'}
                </button>
              )}
            </div>
          </div>
        )}
        
        {(activeTab === 'notes' || activeTab === 'mindmap' || activeTab === 'flashcards') && generatedNotes && !loading && (
          <div className="generated-content">
            <div className="generated-header">
              <h2>{subject || 'Generated Content'}</h2>
              <button className="save-button" onClick={handleSaveNotes}>
                <span className="button-icon">💾</span> Save
              </button>
            </div>
            
            {generatedNotes.format === 'mindmap' ? (
              <div className="mindmap-container">
                <MindMapVisualization data={generatedNotes.mind_map} />
              </div>
            ) : generatedNotes.format === 'flashcards' ? (
              <div className="flashcards-container">
                <FlashcardStudyInterface flashcards={generatedNotes.flashcards} />
              </div>
            ) : (
              <div className="structured-notes">
                {generatedNotes.sections && generatedNotes.sections.map((section, index) => (
                  <div key={index} className="note-section">
                    <h3>{section.title}</h3>
                    <div 
                      className="section-content"
                      dangerouslySetInnerHTML={{ __html: section.content.replace(/\n/g, '<br/>') }}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'saved' && (
          <div className="saved-notes-section">
            <h2>Your Saved Notes</h2>
            <div className="notes-grid">
              {savedNotes.map(note => (
                <div key={note.id} className="note-card">
                  <div className="note-card-content">
                    <h3>{note.title}</h3>
                    <div className="note-meta">
                      <span className="note-format">{note.format}</span>
                      <span className="note-date">{note.date}</span>
                    </div>
                  </div>
                  <div className="note-actions">
                    <button className="note-action-button">
                      <span className="button-icon">✏️</span>
                    </button>
                    <button className="note-action-button">
                      <span className="button-icon">🗑️</span>
                    </button>
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

export default Notes;
