-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(50) NOT NULL DEFAULT 'active',
  due_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- Enable Row Level Security
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own projects
CREATE POLICY "Users can view their own projects"
  ON projects
  FOR SELECT
  USING (user_id = auth.uid());

-- Create policy for users to insert their own projects
CREATE POLICY "Users can insert their own projects"
  ON projects
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- Create policy for users to update their own projects
CREATE POLICY "Users can update their own projects"
  ON projects
  FOR UPDATE
  USING (user_id = auth.uid());

-- Create policy for users to delete their own projects
CREATE POLICY "Users can delete their own projects"
  ON projects
  FOR DELETE
  USING (user_id = auth.uid());

-- Create research_queries table
CREATE TABLE IF NOT EXISTS research_queries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id),
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  query_text TEXT NOT NULL,
  result_data JSONB,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_research_queries_user_id ON research_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_research_queries_project_id ON research_queries(project_id);

-- Enable Row Level Security
ALTER TABLE research_queries ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own research queries
CREATE POLICY "Users can view their own research queries"
  ON research_queries
  FOR SELECT
  USING (user_id = auth.uid());

-- Create policy for users to insert their own research queries
CREATE POLICY "Users can insert their own research queries"
  ON research_queries
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- Create policy for users to update their own research queries
CREATE POLICY "Users can update their own research queries"
  ON research_queries
  FOR UPDATE
  USING (user_id = auth.uid());

-- Create policy for users to delete their own research queries
CREATE POLICY "Users can delete their own research queries"
  ON research_queries
  FOR DELETE
  USING (user_id = auth.uid());

-- Policy: Admins can read all profiles
CREATE POLICY "Admins can read all profiles"
ON users
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid()
    AND auth.users.user_metadata->>'role' = 'admin'
  )
);

-- Policy: Admins can update all profiles
CREATE POLICY "Admins can update all profiles"
ON users
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid()
    AND auth.users.user_metadata->>'role' = 'admin'
  )
);
