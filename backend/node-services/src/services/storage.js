const { createClient } = require('@supabase/supabase-js');
const crypto = require('crypto');
const path = require('path');
const { StorageError } = require('../utils/errors');

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// Default bucket name
const defaultBucket = 'files';

// Generate a unique filename
const generateUniqueFileName = (originalName) => {
  const timestamp = Date.now();
  const randomString = crypto.randomBytes(8).toString('hex');
  const extension = path.extname(originalName);
  const sanitizedName = path.basename(originalName, extension)
    .replace(/[^a-zA-Z0-9]/g, '-')
    .toLowerCase();
  
  return `${sanitizedName}-${timestamp}-${randomString}${extension}`;
};

// Generate a presigned URL for uploading a file
const getPresignedUploadUrl = async (userId, fileName, fileType, folder = 'uploads') => {
  const uniqueFileName = generateUniqueFileName(fileName);
  const filePath = `${folder}/${userId}/${uniqueFileName}`;
  
  // Create the folder if it doesn't exist
  await supabase.storage.from(defaultBucket).upload(`${folder}/${userId}/.folder`, new Uint8Array(0), {
    upsert: true,
    contentType: 'application/x-directory'
  }).catch(() => {});
  
  // Get a signed URL for uploading
  const { data, error } = await supabase.storage.from(defaultBucket)
    .createSignedUploadUrl(filePath);
  
  if (error) throw new StorageError(`Failed to create upload URL: ${error.message}`);
  
  return {
    uploadUrl: data.signedUrl,
    fileKey: filePath,
    fileName: uniqueFileName
  };
};

// List files in a directory
const listFiles = async (userId, folder = 'uploads') => {
  const { data, error } = await supabase.storage.from(defaultBucket)
    .list(`${folder}/${userId}`);
  
  if (error) throw new StorageError(`Failed to list files: ${error.message}`);
  
  return data;
};

// Generate a presigned URL for downloading a file
const getPresignedDownloadUrl = async (fileKey) => {
  const { data, error } = await supabase.storage.from(defaultBucket)
    .createSignedUrl(fileKey, 60 * 60); // 1 hour expiry
  
  if (error) throw new StorageError(`Failed to create download URL: ${error.message}`);
  
  return data.signedUrl;
};

// Delete a file from Supabase Storage
const deleteFile = async (fileKey) => {
  const { error } = await supabase.storage.from(defaultBucket)
    .remove([fileKey]);
  
  if (error) throw new StorageError(`Failed to delete file: ${error.message}`);
  
  return { success: true };
};

module.exports = {
  getPresignedUploadUrl,
  getPresignedDownloadUrl,
  deleteFile
};
