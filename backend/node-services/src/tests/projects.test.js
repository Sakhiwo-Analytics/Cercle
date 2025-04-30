const request = require('supertest');
const express = require('express');
const projectsRouter = require('../routes/projects');
const { supabase } = require('../utils/supabaseClient');

// Mock Supabase
jest.mock('../utils/supabaseClient', () => ({
  supabase: {
    auth: {
      getUser: jest.fn()
    },
    from: jest.fn().mockReturnThis(),
    select: jest.fn().mockReturnThis(),
    eq: jest.fn().mockReturnThis(),
    order: jest.fn().mockReturnThis(),
    insert: jest.fn().mockReturnThis(),
    update: jest.fn().mockReturnThis(),
    delete: jest.fn().mockReturnThis(),
    match: jest.fn().mockReturnThis()
  }
}));

// Setup Express app for testing
const app = express();
app.use(express.json());
app.use('/api/projects', projectsRouter);

describe('Projects API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Mock authenticated user for tests
  const mockUser = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    email: 'test@example.com'
  };

  // Mock middleware to simulate authenticated requests
  app.use((req, res, next) => {
    req.user = mockUser;
    next();
  });

  describe('GET /api/projects', () => {
    it('should return all projects for the user', async () => {
      // Mock the Supabase response
      const mockProjects = [
        { id: '1', title: 'Project 1', description: 'Description 1', user_id: mockUser.id },
        { id: '2', title: 'Project 2', description: 'Description 2', user_id: mockUser.id }
      ];
      
      supabase.from().select().eq().order().mockResolvedValue({
        data: mockProjects,
        error: null
      });

      const response = await request(app).get('/api/projects');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockProjects);
      expect(supabase.from).toHaveBeenCalledWith('projects');
      expect(supabase.select).toHaveBeenCalled();
      expect(supabase.eq).toHaveBeenCalledWith('user_id', mockUser.id);
    });

    it('should handle errors from Supabase', async () => {
      // Mock a Supabase error
      supabase.from().select().eq().order().mockResolvedValue({
        data: null,
        error: { message: 'Database error' }
      });

      const response = await request(app).get('/api/projects');
      
      expect(response.status).toBe(500);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('GET /api/projects/:id', () => {
    it('should return a specific project', async () => {
      const mockProject = { 
        id: '1', 
        title: 'Project 1', 
        description: 'Description 1', 
        user_id: mockUser.id 
      };
      
      supabase.from().select().eq().eq().mockResolvedValue({
        data: [mockProject],
        error: null
      });

      const response = await request(app).get('/api/projects/1');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockProject);
      expect(supabase.from).toHaveBeenCalledWith('projects');
      expect(supabase.select).toHaveBeenCalled();
      expect(supabase.eq).toHaveBeenCalledWith('id', '1');
      expect(supabase.eq).toHaveBeenCalledWith('user_id', mockUser.id);
    });

    it('should return 404 if project not found', async () => {
      supabase.from().select().eq().eq().mockResolvedValue({
        data: [],
        error: null
      });

      const response = await request(app).get('/api/projects/999');
      
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('POST /api/projects', () => {
    it('should create a new project', async () => {
      const newProject = { 
        title: 'New Project', 
        description: 'New Description' 
      };
      
      const createdProject = {
        ...newProject,
        id: '3',
        user_id: mockUser.id,
        created_at: new Date().toISOString()
      };
      
      supabase.from().insert().mockResolvedValue({
        data: [createdProject],
        error: null
      });

      const response = await request(app)
        .post('/api/projects')
        .send(newProject);
      
      expect(response.status).toBe(201);
      expect(response.body).toEqual(createdProject);
      expect(supabase.from).toHaveBeenCalledWith('projects');
      expect(supabase.insert).toHaveBeenCalledWith({
        ...newProject,
        user_id: mockUser.id
      });
    });

    it('should handle validation errors', async () => {
      const response = await request(app)
        .post('/api/projects')
        .send({ description: 'Missing title' });
      
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('PUT /api/projects/:id', () => {
    it('should update an existing project', async () => {
      const updatedProject = { 
        title: 'Updated Project', 
        description: 'Updated Description' 
      };
      
      // Mock project exists check
      supabase.from().select().eq().eq().mockResolvedValue({
        data: [{ id: '1', user_id: mockUser.id }],
        error: null
      });
      
      // Mock update
      supabase.from().update().match().mockResolvedValue({
        data: [{ ...updatedProject, id: '1', user_id: mockUser.id }],
        error: null
      });

      const response = await request(app)
        .put('/api/projects/1')
        .send(updatedProject);
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('title', updatedProject.title);
      expect(supabase.from).toHaveBeenCalledWith('projects');
      expect(supabase.update).toHaveBeenCalledWith(updatedProject);
      expect(supabase.match).toHaveBeenCalledWith({ id: '1', user_id: mockUser.id });
    });

    it('should return 404 if project not found', async () => {
      supabase.from().select().eq().eq().mockResolvedValue({
        data: [],
        error: null
      });

      const response = await request(app)
        .put('/api/projects/999')
        .send({ title: 'Updated Project' });
      
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('DELETE /api/projects/:id', () => {
    it('should delete a project', async () => {
      // Mock project exists check
      supabase.from().select().eq().eq().mockResolvedValue({
        data: [{ id: '1', user_id: mockUser.id }],
        error: null
      });
      
      // Mock delete
      supabase.from().delete().match().mockResolvedValue({
        data: [{ id: '1' }],
        error: null
      });

      const response = await request(app).delete('/api/projects/1');
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('message');
      expect(supabase.from).toHaveBeenCalledWith('projects');
      expect(supabase.delete).toHaveBeenCalled();
      expect(supabase.match).toHaveBeenCalledWith({ id: '1', user_id: mockUser.id });
    });

    it('should return 404 if project not found', async () => {
      supabase.from().select().eq().eq().mockResolvedValue({
        data: [],
        error: null
      });

      const response = await request(app).delete('/api/projects/999');
      
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty('error');
    });
  });
});
