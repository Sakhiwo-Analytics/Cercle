const express = require('express');
const router = express.Router();

// Get all research items for the authenticated user
router.get('/', (req, res) => {
  // In a real implementation, this would fetch from the database
  res.json({
    research_items: [
      {
        id: '1',
        title: 'Quantum Tunneling Paper',
        type: 'article',
        source: 'Journal of Quantum Physics',
        authors: ['A. Einstein', 'N. Bohr'],
        year: 2024,
        saved_at: new Date().toISOString()
      },
      {
        id: '2',
        title: 'Machine Learning Applications in Research',
        type: 'book',
        authors: ['A. Turing', 'G. Hinton'],
        year: 2023,
        saved_at: new Date().toISOString()
      }
    ]
  });
});

// Get a specific research item
router.get('/:id', (req, res) => {
  const itemId = req.params.id;
  // In a real implementation, this would fetch from the database
  res.json({
    id: itemId,
    title: 'Quantum Tunneling Paper',
    type: 'article',
    source: 'Journal of Quantum Physics',
    authors: ['A. Einstein', 'N. Bohr'],
    year: 2024,
    abstract: 'This paper discusses the quantum tunneling phenomenon...',
    content: 'Full content of the research paper...',
    notes: 'User notes about this paper...',
    saved_at: new Date().toISOString()
  });
});

// Save a new research item
router.post('/', (req, res) => {
  const { title, type, source, authors, year, abstract } = req.body;
  
  // Validate input
  if (!title || !type) {
    return res.status(400).json({ error: 'Title and type are required' });
  }
  
  // In a real implementation, this would save to the database
  res.status(201).json({
    id: Date.now().toString(),
    title,
    type,
    source: source || '',
    authors: authors || [],
    year: year || new Date().getFullYear(),
    abstract: abstract || '',
    saved_at: new Date().toISOString()
  });
});

// Update a research item
router.put('/:id', (req, res) => {
  const itemId = req.params.id;
  const { title, type, source, authors, year, abstract, notes } = req.body;
  
  // In a real implementation, this would update in the database
  res.json({
    id: itemId,
    title,
    type,
    source,
    authors,
    year,
    abstract,
    notes,
    updated_at: new Date().toISOString()
  });
});

// Delete a research item
router.delete('/:id', (req, res) => {
  const itemId = req.params.id;
  
  // In a real implementation, this would delete from the database
  res.status(204).send();
});

// Search for research items
router.get('/search/:query', (req, res) => {
  const query = req.params.query;
  
  // In a real implementation, this would search the database
  res.json({
    results: [
      {
        id: '1',
        title: `Search result for "${query}" - Item 1`,
        type: 'article',
        authors: ['Author 1', 'Author 2'],
        year: 2024,
        relevance_score: 0.95
      },
      {
        id: '2',
        title: `Search result for "${query}" - Item 2`,
        type: 'book',
        authors: ['Author 3'],
        year: 2023,
        relevance_score: 0.82
      }
    ]
  });
});

module.exports = router;
