const express = require('express');
const router = express.Router();
const { createClient } = require('@supabase/supabase-js');
const { getPresignedUploadUrl, getPresignedDownloadUrl, deleteFile } = require('../services/storage');
const { checkRole } = require('../middleware/auth');

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// Get upload URL for a file
router.post('/upload-url', async (req, res) => {
  try {
    const userId = req.auth.sub;
    const { fileName, fileType, folder } = req.body;
    
    if (!fileName || !fileType) {
      return res.status(400).json({ error: 'fileName and fileType are required' });
    }
    
    const { uploadUrl, fileKey, fileName: uniqueFileName } = await getPresignedUploadUrl(
      userId, 
      fileName, 
      fileType, 
      folder
    );
    
    // Store file metadata in database
    const { data, error } = await supabase
      .from('files')
      .insert({
        user_id: userId,
        file_name: fileName,
        file_key: fileKey,
        file_type: fileType,
        status: 'pending',
        created_at: new Date()
      })
      .select()
      .single();
    
    if (error) throw error;
    
    res.json({
      uploadUrl,
      fileId: data.id,
      fileKey
    });
  } catch (err) {
    console.error('Error generating upload URL:', err);
    res.status(500).json({ error: 'Failed to generate upload URL' });
  }
});

// Confirm file upload completion
router.post('/confirm-upload/:fileId', async (req, res) => {
  try {
    const userId = req.auth.sub;
    const { fileId } = req.params;
    
    // Update file status in database
    const { data, error } = await supabase
      .from('files')
      .update({
        status: 'uploaded',
        updated_at: new Date()
      })
      .eq('id', fileId)
      .eq('user_id', userId)
      .select()
      .single();
    
    if (error) throw error;
    
    if (!data) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    res.json(data);
  } catch (err) {
    console.error('Error confirming upload:', err);
    res.status(500).json({ error: 'Failed to confirm upload' });
  }
});

// Get download URL for a file
router.get('/download-url/:fileId', async (req, res) => {
  try {
    const userId = req.auth.sub;
    const { fileId } = req.params;
    
    // Get file metadata from database
    const { data, error } = await supabase
      .from('files')
      .select('*')
      .eq('id', fileId)
      .single();
    
    if (error) throw error;
    
    if (!data) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    // Check if user has access to this file
    if (data.user_id !== userId) {
      // Check if file is shared with this user
      const { data: sharedFile } = await supabase
        .from('file_shares')
        .select('*')
        .eq('file_id', fileId)
        .eq('shared_with', userId)
        .single();
      
      if (!sharedFile) {
        return res.status(403).json({ error: 'Access denied' });
      }
    }
    
    const downloadUrl = await getPresignedDownloadUrl(data.file_key);
    
    res.json({
      downloadUrl,
      fileName: data.file_name,
      fileType: data.file_type
    });
  } catch (err) {
    console.error('Error generating download URL:', err);
    res.status(500).json({ error: 'Failed to generate download URL' });
  }
});

// Delete a file
router.delete('/:fileId', async (req, res) => {
  try {
    const userId = req.auth.sub;
    const { fileId } = req.params;
    
    // Get file metadata from database
    const { data, error } = await supabase
      .from('files')
      .select('*')
      .eq('id', fileId)
      .eq('user_id', userId)
      .single();
    
    if (error) throw error;
    
    if (!data) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    // Delete file from Supabase Storage
    await deleteFile(data.file_key);
    
    // Delete file metadata from database
    const { error: deleteError } = await supabase
      .from('files')
      .delete()
      .eq('id', fileId);
    
    if (deleteError) throw deleteError;
    
    res.json({ message: 'File deleted successfully' });
  } catch (err) {
    console.error('Error deleting file:', err);
    res.status(500).json({ error: 'Failed to delete file' });
  }
});

// Get user's files
router.get('/', async (req, res) => {
  try {
    const userId = req.auth.sub;
    
    // Get files from database
    const { data, error } = await supabase
      .from('files')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    
    res.json(data);
  } catch (err) {
    console.error('Error fetching files:', err);
    res.status(500).json({ error: 'Failed to fetch files' });
  }
});

module.exports = router;
