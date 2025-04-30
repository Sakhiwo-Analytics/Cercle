# Setting Up Supabase Storage for Cercle

This guide explains how to set up and configure Supabase Storage for the Cercle project, which replaces the previously planned AWS S3 integration.

## 1. Create a Storage Bucket

1. Log in to your [Supabase Dashboard](https://app.supabase.com)
2. Select your Cercle project
3. Navigate to the "Storage" section in the left sidebar
4. Click "Create bucket"
5. Name the bucket `files` (this is important as the code references this name)
6. Choose "Private" for the bucket type (recommended for security)
7. Click "Create bucket" to finish

## 2. Configure Bucket Permissions

For proper security, we need to set up Row Level Security (RLS) policies:

1. In the Storage section, select the `files` bucket
2. Go to the "Policies" tab
3. Create the following policies:

### For File Uploads (INSERT)

```sql
CREATE POLICY "Allow authenticated users to upload files"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  -- Only allow users to upload to their own folder
  bucket_id = 'files' AND
  (storage.foldername(name))[1] = 'uploads' AND
  (storage.foldername(name))[2] = auth.uid()
);
```

### For File Downloads (SELECT)

```sql
CREATE POLICY "Allow users to view their own files"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  -- Only allow users to view their own files
  bucket_id = 'files' AND
  (storage.foldername(name))[1] = 'uploads' AND
  (storage.foldername(name))[2] = auth.uid()
);
```

### For File Sharing (SELECT - Optional)

```sql
CREATE POLICY "Allow users to view shared files"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'files' AND
  EXISTS (
    SELECT 1 FROM file_shares fs
    JOIN files f ON fs.file_id = f.id
    WHERE f.file_key = name AND fs.shared_with = auth.uid()
  )
);
```

### For File Deletion (DELETE)

```sql
CREATE POLICY "Allow users to delete their own files"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'files' AND
  (storage.foldername(name))[1] = 'uploads' AND
  (storage.foldername(name))[2] = auth.uid()
);
```

## 3. Update Environment Variables

Make sure your `.env` file contains the correct Supabase variables:

```
SUPABASE_URL=https://drajewtkgnymjpfmcawi.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRyYWpld3RrZ255bWpwZm1jYXdpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTcwMjAxNCwiZXhwIjoyMDYxMjc4MDE0fQ.Yb3uEC6mrcw42ImclsxyWa0XWB70MhZILxvV2M7zQMI
```

The `SUPABASE_KEY` should be the service role key (not the anon key) since it needs permissions to manage files.

## 4. Testing the Storage Integration

You can test the storage integration with the following steps:

1. Start your Cercle backend server
2. Use Postman or a similar tool to:
   - Get an upload URL: `POST /api/files/upload-url`
   - Upload a file using the returned URL
   - Confirm the upload: `POST /api/files/confirm-upload/:fileId`
   - Get a download URL: `GET /api/files/download-url/:fileId`

## 5. Troubleshooting

If you encounter issues:

1. **Permission Denied**: Check your RLS policies and make sure they're correctly configured
2. **Bucket Not Found**: Verify that you've created a bucket named `files`
3. **Authentication Issues**: Ensure you're using the service role key for server-side operations
4. **CORS Issues**: Configure CORS in the Supabase dashboard if needed for frontend uploads

## Benefits of Using Supabase Storage

- Unified authentication with your existing Supabase setup
- Simplified permissions through RLS policies
- No need for separate AWS credentials
- Built-in file management through the Supabase dashboard
- Cost-effective for most use cases
