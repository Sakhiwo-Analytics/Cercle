# Cercle Developer Getting Started Guide

This guide will help you set up your local development environment for the Cercle project and understand the key components of the system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Running the Application](#running-the-application)
4. [Project Structure](#project-structure)
5. [Authentication](#authentication)
6. [Database](#database)
7. [API Endpoints](#api-endpoints)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18+)
- **npm** (v8+) or **yarn** (v1.22+)
- **Python** (v3.9+)
- **Docker** and **Docker Compose**
- **Git**

You'll also need:

- A Supabase account (free tier is sufficient for development)
- Code editor (VS Code recommended)

## Project Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-org/cercle.git
cd cercle
```

2. **Set up environment variables**

```bash
# Frontend
cp frontend/.env.example frontend/.env

# Node.js backend
cp backend/node-services/.env.example backend/node-services/.env

# Python backend
cp backend/python-services/.env.example backend/python-services/.env
```

3. **Update the environment files with your Supabase credentials**

Create a new Supabase project at [https://app.supabase.io](https://app.supabase.io) and add your project URL and anon key to the `.env` files.

4. **Install dependencies**

```bash
# Frontend
cd frontend
npm install

# Node.js backend
cd ../backend/node-services
npm install

# Python backend
cd ../python-services
pip install -r requirements.txt
```

## Running the Application

### Using Docker Compose (Recommended)

The easiest way to run the entire application stack is using Docker Compose:

```bash
cd infra
docker-compose up
```

This will start:
- Frontend on http://localhost:3000
- Node.js backend on http://localhost:8000
- Python backend on http://localhost:8001
- Redis on localhost:6379

### Running Services Individually

**Frontend:**

```bash
cd frontend
npm start
```

**Node.js Backend:**

```bash
cd backend/node-services
npm run dev
```

**Python Backend:**

```bash
cd backend/python-services
uvicorn app.main:app --reload --port 8001
```

## Project Structure

```
cercle/
├── frontend/               # React frontend application
│   ├── public/             # Static files
│   ├── src/                # Source code
│   │   ├── components/     # Reusable components
│   │   ├── contexts/       # React contexts (Auth, etc.)
│   │   ├── pages/          # Page components
│   │   └── styles/         # CSS files
├── backend/                # Backend services
│   ├── node-services/      # Node.js microservices
│   │   ├── src/            # Source code
│   │   │   ├── migrations/ # Database migrations
│   │   │   ├── routes/     # API routes
│   │   │   └── utils/      # Utility functions
│   └── python-services/    # FastAPI (Python) microservices
│       ├── app/            # Source code
│       │   ├── api/        # API endpoints
│       │   ├── core/       # Core functionality
│       │   └── models/     # Data models
├── infra/                  # Infrastructure configuration
│   ├── docker-compose.yml  # Local development setup
│   └── render/             # Render deployment configurations
├── docs/                   # Documentation
└── .github/                # GitHub Actions workflows
```

## Authentication

Cercle uses Supabase Authentication for user management. The authentication flow is handled by the `AuthContext` in the frontend.

### Key Authentication Files

- `frontend/src/supabaseClient.js` - Initializes the Supabase client
- `frontend/src/contexts/AuthContext.js` - Manages authentication state
- `frontend/src/components/ProtectedRoute.js` - Protects routes from unauthenticated access

### Authentication Flow

1. User signs up or logs in via the Login/Signup pages
2. Supabase handles the authentication and returns a session
3. The session is stored and managed by the AuthContext
4. Protected routes check for an active session before rendering

For more details, see the [Supabase Authentication Guide](./supabase-auth-setup.md).

## Database

Cercle uses PostgreSQL via Supabase for data storage. The database schema is managed through migration scripts.

### Running Migrations

To set up or update the database schema:

```bash
cd backend/node-services
node src/utils/db-migrate.js
```

### Key Database Tables

- `users` - User profiles
- `projects` - User projects
- `files` - Uploaded files
- `file_shares` - File sharing permissions
- `research_queries` - Research query history
- `documents` - Writing documents
- `document_versions` - Document version history

## API Endpoints

### Node.js Backend (Port 8000)

#### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login a user
- `POST /api/auth/logout` - Logout a user

#### Projects
- `GET /api/projects` - Get all projects for the user
- `GET /api/projects/:id` - Get a specific project
- `POST /api/projects` - Create a new project
- `PUT /api/projects/:id` - Update a project
- `DELETE /api/projects/:id` - Delete a project

#### Files
- `GET /api/files` - Get all files for the user
- `GET /api/files/:id` - Get a specific file
- `POST /api/files` - Upload a new file
- `DELETE /api/files/:id` - Delete a file
- `POST /api/files/:id/share` - Share a file with another user

### Python Backend (Port 8001)

#### Research
- `POST /api/research/query` - Submit a research query
- `GET /api/research/queries` - Get all research queries for the user
- `GET /api/research/queries/:id` - Get a specific research query

#### Writing Assistant
- `POST /api/writing/suggest` - Get writing suggestions
- `POST /api/writing/analyze` - Analyze text

## Testing

### Frontend Tests

```bash
cd frontend
npm test
```

### Backend Tests

```bash
# Node.js backend
cd backend/node-services
npm test

# Python backend
cd backend/python-services
pytest
```

## Deployment

Cercle is configured for deployment on Render using the configuration files in the `infra/render` directory.

### Environments

- **Development**: dev.cercle.app
- **Testing**: test.cercle.app
- **Staging**: staging.cercle.app

### Deployment Process

1. Push changes to the appropriate branch
2. GitHub Actions will run tests and build the application
3. If tests pass, the application will be deployed to the corresponding environment

## Troubleshooting

### Common Issues

#### Frontend
- **Authentication Issues**: Check your Supabase URL and anon key in the `.env` file
- **CORS Errors**: Ensure your backend URLs are correctly set in the `.env` file

#### Backend
- **Database Connection Issues**: Verify your Supabase credentials
- **Migration Errors**: Check the migration scripts for syntax errors

#### Docker
- **Port Conflicts**: Ensure no other services are running on ports 3000, 8000, or 8001
- **Container Startup Issues**: Check the Docker logs for error messages

### Getting Help

If you encounter issues not covered in this guide:

1. Check the project documentation in the `docs` directory
2. Review the GitHub issues for similar problems
3. Reach out to the development team

---

Happy coding with Cercle! 🚀
