'use client';

import { use, useEffect, useState } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { FileText, Clock, CheckCircle2, XCircle, Loader2, ArrowRight } from 'lucide-react';
import api, { BatchResponse } from '@/lib/api';
import { formatDate } from '@/lib/utils';

export default function BatchDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  
  const { data: batch, isLoading, error } = useQuery({
    queryKey: ['batch', id],
    queryFn: () => api.getBatch(id),
    refetchInterval: (query) => {
      // Refetch every 2 seconds if still processing
      return query.state.data?.status === 'processing' || query.state.data?.status === 'queued' ? 2000 : false;
    },
  });

  const { data: candidatesData } = useQuery({
    queryKey: ['batch-candidates', id],
    queryFn: () => api.getBatchCandidates(id, 0, 50),
    enabled: batch?.status === 'completed',
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
      </div>
    );
  }

  if (error || !batch) {
    return (
      <div className="max-w-2xl mx-auto mt-12 text-center">
        <XCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Batch Not Found</h2>
        <p className="text-gray-600 mb-6">The batch you're looking for doesn't exist.</p>
        <Link
          href="/batches"
          className="inline-block bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-orange-700 transition"
        >
          View All Batches
        </Link>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-6 h-6 text-green-600" />;
      case 'processing':
      case 'queued':
        return <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-600" />;
      default:
        return <Clock className="w-6 h-6 text-gray-600" />;
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
      {/* Header */}
      <div className="mb-8">
        <Link href="/batches" className="text-orange-600 hover:text-orange-700 mb-2 inline-block">
          ← Back to Batches
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Batch Details</h1>
        <p className="text-gray-600 mt-1">Batch ID: {batch.batch_id}</p>
      </div>

      {/* Status Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-3">
            {getStatusIcon(batch.status)}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {batch.description || 'Untitled Batch'}
              </h2>
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mt-2 ${getStatusColor(batch.status)}`}>
                {batch.status.charAt(0).toUpperCase() + batch.status.slice(1)}
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Created</p>
            <p className="text-sm font-medium text-gray-900">{formatDate(batch.created_at)}</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Processing Progress</span>
            <span className="text-sm text-gray-600">
              {batch.processed_files} / {batch.total_files} files
            </span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-orange-600 transition-all duration-300"
              style={{ width: `${batch.progress_percentage}%` }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-1">{batch.progress_percentage.toFixed(1)}% complete</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{batch.total_files}</p>
            <p className="text-sm text-gray-600">Total Files</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{batch.processed_files}</p>
            <p className="text-sm text-gray-600">Processed</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-red-600">{batch.failed_files}</p>
            <p className="text-sm text-gray-600">Failed</p>
          </div>
        </div>
      </div>

      {/* Candidates List - HIDDEN UNTIL MATCHING */}
      {/* Candidates are now only visible after matching against a job description */}
      {false && batch.status === 'completed' && candidatesData && candidatesData.candidates.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Extracted Candidates ({candidatesData.total})
          </h3>
          
          <div className="space-y-3">
            {candidatesData.candidates.map((candidate) => (
              <div
                key={candidate.candidate_id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">
                      {candidate.name || 'Unknown Name'}
                    </h4>
                    <div className="mt-2 space-y-1">
                      {candidate.email && (
                        <p className="text-sm text-gray-600">📧 {candidate.email}</p>
                      )}
                      {candidate.phone && (
                        <p className="text-sm text-gray-600">📱 {candidate.phone}</p>
                      )}
                      {candidate.location && (
                        <p className="text-sm text-gray-600">📍 {candidate.location}</p>
                      )}
                    </div>
                    
                    {/* Skills */}
                    {candidate.skills && candidate.skills.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs text-gray-500 mb-1">Skills:</p>
                        <div className="flex flex-wrap gap-1">
                          {candidate.skills.slice(0, 5).map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full"
                            >
                              {skill}
                            </span>
                          ))}
                          {candidate.skills.length > 5 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{candidate.skills.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Tools */}
                    {candidate.tools && candidate.tools.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs text-gray-500 mb-1">Tools:</p>
                        <div className="flex flex-wrap gap-1">
                          {candidate.tools.slice(0, 5).map((tool, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full"
                            >
                              {tool}
                            </span>
                          ))}
                          {candidate.tools.length > 5 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{candidate.tools.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="ml-4 flex flex-col items-end gap-2">
                    {candidate.ocr_quality_score !== undefined && (
                      <div className="text-right">
                        <p className="text-xs text-gray-500">OCR Quality</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {candidate.ocr_quality_score.toFixed(0)}%
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Match Action */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <Link
              href="/job-descriptions"
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              Match Candidates to Job Description
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}

      {/* Processing Message */}
      {(batch.status === 'processing' || batch.status === 'queued') && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 text-center">
          <Loader2 className="w-12 h-12 text-orange-600 mx-auto mb-3 animate-spin" />
          <h3 className="text-lg font-semibold text-orange-900 mb-2">
            Processing in Progress
          </h3>
          <p className="text-orange-700">
            Your CVs are being processed. This page will auto-update when complete.
          </p>
        </div>
      )}

      {/* Success Message - Redirects to JD matching */}
      {batch.status === 'completed' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
          <CheckCircle2 className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Batch Processing Complete!
          </h3>
          <p className="text-gray-600 mb-6">
            {batch.processed_files} CVs have been successfully processed and are ready for matching.
          </p>
          <Link
            href="/job-descriptions"
            className="inline-flex items-center gap-2 bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-orange-700 transition"
          >
            Match Candidates to Job Description
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}
    </div>
  );
}
