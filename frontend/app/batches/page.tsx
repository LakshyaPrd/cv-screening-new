'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { FileText, Clock, CheckCircle2, XCircle, Loader2, Upload as UploadIcon } from 'lucide-react';
import api from '@/lib/api';
import { formatDate } from '@/lib/utils';

export default function BatchesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['batches'],
    queryFn: () => api.listBatches(0, 20),
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'processing':
      case 'queued':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'queued':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">CV Batches</h1>
          <p className="text-gray-600 mt-2">View and manage uploaded CV batches</p>
        </div>
        <Link
          href="/upload"
          className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
        >
          <UploadIcon className="w-5 h-5" />
          Upload New Batch
        </Link>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center min-h-96">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : !data || data.batches.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Batches Yet</h3>
          <p className="text-gray-600 mb-6">
            Upload your first batch of CVs to get started with candidate screening
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            <UploadIcon className="w-5 h-5" />
            Upload CVs
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {data.batches.map((batch) => (
            <Link
              key={batch.batch_id}
              href={`/batches/${batch.batch_id}`}
              className="block bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:border-blue-300 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  {getStatusIcon(batch.status)}
                  
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg">
                      {batch.description || 'Untitled Batch'}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      ID: {batch.batch_id.slice(0, 8)}...
                    </p>
                    
                    <div className="mt-3 flex items-center gap-4 text-sm text-gray-600">
                      <span>{batch.total_files} files</span>
                      <span>•</span>
                      <span>{batch.processed_files} processed</span>
                      {batch.failed_files > 0 && (
                        <>
                          <span>•</span>
                          <span className="text-red-600">{batch.failed_files} failed</span>
                        </>
                      )}
                    </div>

                    {/* Progress Bar */}
                    {(batch.status === 'processing' || batch.status === 'queued') && (
                      <div className="mt-3 max-w-xs">
                        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-600 transition-all duration-300"
                            style={{ width: `${batch.progress_percentage}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {batch.progress_percentage.toFixed(0)}% complete
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="ml-4 text-right">
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(batch.status)}`}>
                    {batch.status.charAt(0).toUpperCase() + batch.status.slice(1)}
                  </span>
                  <p className="text-sm text-gray-500 mt-2">
                    {formatDate(batch.created_at)}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {data && data.total > 20 && (
        <div className="mt-6 text-center text-sm text-gray-600">
          Showing {Math.min(20, data.total)} of {data.total} batches
        </div>
      )}
    </div>
  );
}
