-- Create file_shares table for sharing files between users
CREATE TABLE IF NOT EXISTS file_shares (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
  shared_by UUID NOT NULL REFERENCES users(id),
  shared_with UUID NOT NULL REFERENCES users(id),
  permission_level VARCHAR(50) NOT NULL DEFAULT 'view',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_file_shares_file_id ON file_shares(file_id);
CREATE INDEX IF NOT EXISTS idx_file_shares_shared_by ON file_shares(shared_by);
CREATE INDEX IF NOT EXISTS idx_file_shares_shared_with ON file_shares(shared_with);

-- Enable Row Level Security
ALTER TABLE file_shares ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view shares they've created
CREATE POLICY "Users can view shares they've created"
  ON file_shares
  FOR SELECT
  USING (shared_by = auth.uid());

-- Create policy for users to view files shared with them
CREATE POLICY "Users can view files shared with them"
  ON file_shares
  FOR SELECT
  USING (shared_with = auth.uid());

-- Create policy for users to create shares for their own files
CREATE POLICY "Users can create shares for their own files"
  ON file_shares
  FOR INSERT
  WITH CHECK (shared_by = auth.uid() AND EXISTS (
    SELECT 1 FROM files WHERE files.id = file_id AND files.user_id = auth.uid()
  ));

-- Create policy for users to delete shares they've created
CREATE POLICY "Users can delete shares they've created"
  ON file_shares
  FOR DELETE
  USING (shared_by = auth.uid());
