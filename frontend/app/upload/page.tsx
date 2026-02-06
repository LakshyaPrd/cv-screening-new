'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, X, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '@/lib/api';

interface UploadedFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

export default function UploadPage() {
  const router = useRouter();
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [description, setDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  };

  const addFiles = (newFiles: File[]) => {
    const uploadedFiles: UploadedFile[] = newFiles.map(file => ({
      file,
      status: 'pending',
      progress: 0,
    }));
    setFiles(prev => [...prev, ...uploadedFiles]);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    
    try {
      // Update all files to uploading status
      setFiles(prev => prev.map(f => ({ ...f, status: 'uploading' as const, progress: 50 })));

      const fileList = files.map(f => f.file);
      const result = await api.uploadBatch(fileList, description);

      // Update all files to success
      setFiles(prev => prev.map(f => ({ ...f, status: 'success' as const, progress: 100 })));

      // Redirect to batch detail after 1 second
      setTimeout(() => {
        router.push(`/batches/${result.batch_id}`);
      }, 1000);

    } catch (error: any) {
      console.error('Upload error:', error);
      setFiles(prev => prev.map(f => ({
        ...f,
        status: 'error' as const,
        error: error.response?.data?.detail || 'Upload failed'
      })));
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const totalSize = files.reduce((acc, f) => acc + f.file.size, 0);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload CVs & Portfolios</h1>
        <p className="text-gray-600 mt-2">
          Upload PDF, JPG, PNG, or TIFF files for OCR processing and candidate extraction
        </p>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-12 text-center transition ${
          isDragging
            ? 'border-orange-500 bg-orange-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <h3 className="text-lg font-semibold text-gray-700 mb-2">
          Drop files here or click to browse
        </h3>
        <p className="text-gray-500 mb-4">
          Supports: PDF, JPG, PNG, TIFF, DOC, DOCX • Max 50MB per file
        </p>
        <input
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.tiff,.doc,.docx"
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-block bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold cursor-pointer hover:bg-orange-700 transition"
        >
          Select Files
        </label>
      </div>

      {/* Description Input */}
      {files.length > 0 && (
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Batch Description (Optional)
          </label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., BIM Architect candidates - December 2024"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">
              Selected Files ({files.length})
            </h3>
            <span className="text-sm text-gray-500">
              Total: {formatFileSize(totalSize)}
            </span>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {files.map((uploadedFile, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
              >
                <FileText className="w-5 h-5 text-orange-600 flex-shrink-0" />
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {uploadedFile.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(uploadedFile.file.size)}
                  </p>
                </div>

                {uploadedFile.status === 'pending' && (
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-600 transition"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}

                {uploadedFile.status === 'uploading' && (
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-orange-600 transition-all duration-300"
                        style={{ width: `${uploadedFile.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">{uploadedFile.progress}%</span>
                  </div>
                )}

                {uploadedFile.status === 'success' && (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                )}

                {uploadedFile.status === 'error' && (
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    <span className="text-xs text-red-600">{uploadedFile.error}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-6 flex gap-3">
            <button
              onClick={handleUpload}
              disabled={isUploading || files.some(f => f.status === 'success')}
              className="flex-1 bg-orange-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              {isUploading ? 'Uploading...' : `Upload ${files.length} File${files.length > 1 ? 's' : ''}`}
            </button>
            
            {!isUploading && (
              <button
                onClick={() => setFiles([])}
                className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
              >
                Clear All
              </button>
            )}
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 bg-orange-50 border border-orange-200 rounded-lg p-4">
        <h4 className="font-semibold text-orange-900 mb-2">What happens next?</h4>
        <ul className="text-sm text-orange-800 space-y-1">
          <li>• Files are uploaded and queued for processing</li>
          <li>• OCR extracts text from PDFs and images using Tesseract</li>
          <li>• System extracts candidate data (name, email, skills, experience)</li>
          <li>• You can track progress in the Batches section</li>
          <li>• Match candidates against job descriptions when ready</li>
        </ul>
      </div>
    </div>
  );
}
