# Cercle

An AI-powered SaaS Workspace built for Students and Researchers to accelerate academic research, learning, and writing.

## Overview

Cercle combines a Smart Query Engine, a Research Amplifier, a Writing Assistant, and intuitive Project Management tools — all within a minimal, modular interface.

### Mission
To empower students and researchers to think, learn, and create faster using AI, while keeping academic quality and rigor at the center.

## Features

- **Smart Query Engine**: Advanced search capabilities with rich-text output including graphs, formulas, and citations
- **Research Amplifier**: Tools to enhance and accelerate research workflows
- **Writing Assistant**: AI-powered writing help for academic papers and projects
- **Project Management**: Organize research projects, deadlines, and resources

## Project Structure

```
cercle/
├── frontend/               # React frontend application
├── backend/                # Backend services
│   ├── node-services/      # Node.js microservices
│   └── python-services/    # FastAPI (Python) microservices
├── infra/                  # Infrastructure configuration
│   ├── docker-compose.yml  # Local development setup
│   └── render/             # Render deployment configurations
├── docs/                   # Documentation
└── .github/                # GitHub Actions workflows
```

## Development Phases

### Phase 1: Project Setup (Completed)
- ✅ Set up project directory structure
- ✅ Create Docker containers for local development
- ✅ Set up CI/CD pipeline with GitHub Actions
- ✅ Configure Dev/Test/Staging environments (Render)
- ✅ Set up basic microservice skeleton (Node.js + FastAPI)
- ✅ Implement Supabase Authentication
- ✅ Create frontend components and layouts
- ✅ Set up basic API endpoints

### Phase 2: Core Functionality (Next)
- Implement Smart Query Engine
- Develop Research Amplifier
- Create Writing Assistant
- Build Project Management features
- Implement real-time collaboration

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js (v18+)
- Python (v3.9+)
- Git
- Supabase account

### Local Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-org/cercle.git
   cd cercle
   ```

2. Set up environment variables:
   ```
   # Frontend
   cp frontend/.env.example frontend/.env
   # Node.js backend
   cp backend/node-services/.env.example backend/node-services/.env
   # Python backend
   cp backend/python-services/.env.example backend/python-services/.env
   ```

3. Start the local development environment:
   ```
   cd infra
   docker-compose up
   ```

4. Access the services:
   - Frontend: http://localhost:3000
   - Node.js API: http://localhost:8000
   - Python API: http://localhost:8001

### Running Tests

```
# Frontend tests
cd frontend
npm test

# Node.js backend tests
cd backend/node-services
npm test

# Python backend tests
cd backend/python-services
pytest
```

## Architecture

Cercle uses a microservice architecture with:

- **Frontend**: React.js with React Router for navigation
- **Backend**: 
  - Node.js (Express) for web API and real-time features
  - FastAPI (Python) for AI/ML processing
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Supabase Authentication
- **Caching**: Redis
- **Deployment**: Render

## Environments
- Development: dev.cercle.app
- Testing: test.cercle.app
- Staging: staging.cercle.app

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Submit a pull request to `develop`
4. Ensure all CI checks pass

## License

[MIT License](LICENSE)
