-- Create files table
CREATE TABLE IF NOT EXISTS files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id),
  file_name VARCHAR(255) NOT NULL,
  file_key VARCHAR(512) NOT NULL UNIQUE,
  file_type VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);

-- Enable Row Level Security
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own files
CREATE POLICY "Users can view their own files"
  ON files
  FOR SELECT
  USING (user_id = auth.uid());

-- Create policy for users to insert their own files
CREATE POLICY "Users can insert their own files"
  ON files
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- Create policy for users to update their own files
CREATE POLICY "Users can update their own files"
  ON files
  FOR UPDATE
  USING (user_id = auth.uid());

-- Create policy for users to delete their own files
CREATE POLICY "Users can delete their own files"
  ON files
  FOR DELETE
  USING (user_id = auth.uid());
