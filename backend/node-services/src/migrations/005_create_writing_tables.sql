-- Create documents table for the writing assistant
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id),
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  title VARCHAR(255) NOT NULL,
  content TEXT,
  document_type VARCHAR(50) NOT NULL DEFAULT 'note',
  status VARCHAR(50) NOT NULL DEFAULT 'draft',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id);

-- Enable Row Level Security
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own documents
CREATE POLICY "Users can view their own documents"
  ON documents
  FOR SELECT
  USING (user_id = auth.uid());

-- Create policy for users to insert their own documents
CREATE POLICY "Users can insert their own documents"
  ON documents
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- Create policy for users to update their own documents
CREATE POLICY "Users can update their own documents"
  ON documents
  FOR UPDATE
  USING (user_id = auth.uid());

-- Create policy for users to delete their own documents
CREATE POLICY "Users can delete their own documents"
  ON documents
  FOR DELETE
  USING (user_id = auth.uid());

-- Create document_versions table for version history
CREATE TABLE IF NOT EXISTS document_versions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  version_number INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on document_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON document_versions(document_id);

-- Enable Row Level Security
ALTER TABLE document_versions ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view versions of their own documents
CREATE POLICY "Users can view versions of their own documents"
  ON document_versions
  FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_id 
    AND documents.user_id = auth.uid()
  ));

-- Create policy for users to insert versions of their own documents
CREATE POLICY "Users can insert versions of their own documents"
  ON document_versions
  FOR INSERT
  WITH CHECK (EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_id 
    AND documents.user_id = auth.uid()
  ));

-- Create policy for users to delete versions of their own documents
CREATE POLICY "Users can delete versions of their own documents"
  ON document_versions
  FOR DELETE
  USING (EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_id 
    AND documents.user_id = auth.uid()
  ));

-- Create writing_suggestions table for AI suggestions
CREATE TABLE IF NOT EXISTS writing_suggestions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  suggestion_text TEXT NOT NULL,
  suggestion_type VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on document_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_writing_suggestions_document_id ON writing_suggestions(document_id);

-- Enable Row Level Security
ALTER TABLE writing_suggestions ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view suggestions for their own documents
CREATE POLICY "Users can view suggestions for their own documents"
  ON writing_suggestions
  FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_id 
    AND documents.user_id = auth.uid()
  ));

-- Create policy for users to insert suggestions for their own documents
CREATE POLICY "Users can insert suggestions for their own documents"
  ON writing_suggestions
  FOR INSERT
  WITH CHECK (EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_id 
    AND documents.user_id = auth.uid()
  ));

-- Create policy for users to update suggestions for their own documents
CREATE POLICY "Users can update suggestions for their own documents"
  ON writing_suggestions
  FOR UPDATE
  USING (EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_id 
    AND documents.user_id = auth.uid()
  ));

-- Create policy for users to delete suggestions for their own documents
CREATE POLICY "Users can delete suggestions for their own documents"
  ON writing_suggestions
  FOR DELETE
  USING (EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_id 
    AND documents.user_id = auth.uid()
  ));
