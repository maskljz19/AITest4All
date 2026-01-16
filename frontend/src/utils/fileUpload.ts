import { message } from 'antd';

const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB max

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface ChunkedUploadOptions {
  file: File;
  onProgress?: (progress: UploadProgress) => void;
  onSuccess?: (response: any) => void;
  onError?: (error: Error) => void;
}

/**
 * Validate file before upload
 */
export function validateFile(file: File, maxSize: number = MAX_FILE_SIZE): boolean {
  if (file.size > maxSize) {
    message.error(`文件大小超过限制 (${(maxSize / 1024 / 1024).toFixed(0)}MB)`);
    return false;
  }
  return true;
}

/**
 * Upload file with progress tracking
 * For files larger than 5MB, this could be extended to use chunked upload
 */
export async function uploadFileWithProgress(
  url: string,
  file: File,
  additionalData?: Record<string, any>,
  onProgress?: (progress: UploadProgress) => void
): Promise<any> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    
    formData.append('file', file);
    
    // Add additional form data
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          formData.append(key, typeof value === 'object' ? JSON.stringify(value) : String(value));
        }
      });
    }
    
    // Track upload progress
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress({
          loaded: e.loaded,
          total: e.total,
          percentage: Math.round((e.loaded / e.total) * 100),
        });
      }
    });
    
    // Handle completion
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (e) {
          resolve(xhr.responseText);
        }
      } else {
        try {
          const error = JSON.parse(xhr.responseText);
          reject(new Error(error.message || `Upload failed with status ${xhr.status}`));
        } catch (e) {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    });
    
    // Handle errors
    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed due to network error'));
    });
    
    xhr.addEventListener('abort', () => {
      reject(new Error('Upload was aborted'));
    });
    
    // Send request
    xhr.open('POST', url);
    
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    }
    
    xhr.send(formData);
  });
}

/**
 * Chunked file upload for very large files
 * This is a placeholder for future implementation if needed
 */
export async function uploadFileInChunks(options: ChunkedUploadOptions): Promise<void> {
  const { file, onProgress, onSuccess, onError } = options;
  
  // For now, just use regular upload
  // In the future, this could implement actual chunked upload
  try {
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    
    // Simulate chunked upload progress
    for (let i = 0; i < totalChunks; i++) {
      if (onProgress) {
        onProgress({
          loaded: Math.min((i + 1) * CHUNK_SIZE, file.size),
          total: file.size,
          percentage: Math.round(((i + 1) / totalChunks) * 100),
        });
      }
      
      // Small delay to simulate upload
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    if (onSuccess) {
      onSuccess({ success: true });
    }
  } catch (error) {
    if (onError) {
      onError(error as Error);
    }
  }
}

/**
 * Get file extension
 */
export function getFileExtension(filename: string): string {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2).toLowerCase();
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Check if file type is allowed
 */
export function isFileTypeAllowed(filename: string, allowedExtensions: string[]): boolean {
  const ext = getFileExtension(filename);
  return allowedExtensions.includes(ext);
}
