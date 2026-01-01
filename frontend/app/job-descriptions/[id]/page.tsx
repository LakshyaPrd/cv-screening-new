'use client';

import { use, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { Loader2, Zap, Star, Users, Table2, LayoutGrid } from 'lucide-react';
import api from '@/lib/api';
import CandidateDataTable from '@/components/CandidateDataTable';

export default function JobDescriptionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [selectedMatches, setSelectedMatches] = useState<string[]>([]);
  const [selectedBatchId, setSelectedBatchId] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
  const [filters, setFilters] = useState({
    min_score: 50,
    is_shortlisted: undefined as boolean | undefined,
    page: 1,
    page_size: 20,
  });

  const { data: jd, isLoading: jdLoading } = useQuery({
    queryKey: ['jd', id],
    queryFn: () => api.getJobDescription(id),
  });

  const { data: batchesList } = useQuery({
    queryKey: ['batches-list'],
    queryFn: () => api.listBatches(0, 100),
  });

  // Fetch candidates from selected batch for filtering
  const { data: batchCandidates } = useQuery({
    queryKey: ['batch-candidates', selectedBatchId],
    queryFn: () => selectedBatchId !== 'all' ? api.getBatchCandidates(selectedBatchId, 0, 1000) : null,
    enabled: selectedBatchId !== 'all',
  });

  const { data: matchesData, isLoading: matchesLoading } = useQuery({
    queryKey: ['matches', id, filters],
    queryFn: () => api.getMatches(id, filters),
  });

  // Filter matches to only show candidates from selected batch
  const filteredMatches = matchesData?.matches.filter(match => {
    if (selectedBatchId === 'all') return true;
    return batchCandidates?.candidates.some(c => c.candidate_id === match.candidate_id);
  }) || [];

  const filteredTotal = selectedBatchId === 'all' 
    ? matchesData?.total || 0
    : filteredMatches.length;

  const queryClient = useQueryClient();

  const matchMutation = useMutation({
    mutationFn: () => api.matchCandidates(id, selectedBatchId !== 'all' ? selectedBatchId : undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches', id] });
    },
  });

  const shortlistMutation = useMutation({
    mutationFn: (matchIds: string[]) => api.shortlistCandidates(id, matchIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches', id] });
      setSelectedMatches([]);
    },
  });

  if (jdLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!jd) {
    return <div className="text-center py-12">Job Description not found</div>;
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-50';
    if (score >= 60) return 'bg-blue-50';
    if (score >= 40) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  const toggleSelectMatch = (matchId: string) => {
    setSelectedMatches(prev =>
      prev.includes(matchId)
        ? prev.filter(id => id !== matchId)
        : [...prev, matchId]
    );
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <Link href="/job-descriptions" className="text-blue-600 hover:text-blue-700 mb-2 inline-block">
          ← Back to Job Descriptions
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{jd.title}</h1>
        <p className="text-gray-600 mt-1">{jd.description}</p>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="font-semibold text-gray-900 mb-4">Candidate Matching</h3>
        
        {/* Batch Selector */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Batch to Match
          </label>
          <select
            value={selectedBatchId}
            onChange={(e) => setSelectedBatchId(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          >
            <option value="all">All Candidates in System ({matchesData?.total || 0})</option>
            {batchesList?.batches.map((batch) => (
              <option key={batch.batch_id} value={batch.batch_id}>
                {batch.description || `Batch ${batch.batch_id.slice(0, 8)}`} 
                {' '}({batch.processed_files} processed, {batch.failed_files} failed)
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">
            Choose a specific batch to match only those candidates, or select "All Candidates" to match everyone in the system.
          </p>
        </div>

        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-gray-600">
            Run matching algorithm to find best-fit candidates
          </p>
          <button
            onClick={() => matchMutation.mutate()}
            disabled={matchMutation.isPending}
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            {matchMutation.isPending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Matching...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Run Matching
              </>
            )}
          </button>
        </div>
        
        {/* Info message */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
          <strong>Note:</strong> {selectedBatchId === 'all' 
            ? `Matching ALL ${matchesData?.total || 0} candidates in the system.`
            : `Matching only candidates from the selected batch.`
          } Results are filtered by minimum score below.
        </div>

        {matchMutation.isSuccess && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 text-sm">
              ✓ Matching completed successfully! Results are shown below.
            </p>
          </div>
        )}
      </div>

      {/* Filters & View Toggle */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Filters & Display</h3>
          
          {/* View Toggle */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600 mr-2">View:</span>
            <button
              onClick={() => setViewMode('cards')}
              className={`px-4 py-2 rounded-lg font-medium transition flex items-center gap-2 ${
                viewMode === 'cards'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <LayoutGrid className="w-4 h-4" />
              Cards
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-4 py-2 rounded-lg font-medium transition flex items-center gap-2 ${
                viewMode === 'table'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Table2 className="w-4 h-4" />
              Table
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Score
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={filters.min_score}
              onChange={(e) => setFilters({ ...filters, min_score: parseInt(e.target.value) || 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Show Only
            </label>
            <select
              value={filters.is_shortlisted ? 'shortlisted' : 'all'}
              onChange={(e) => setFilters({
                ...filters,
                is_shortlisted: e.target.value === 'shortlisted' ? true : undefined
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="all">All Candidates</option>
              <option value="shortlisted">Shortlisted Only</option>
            </select>
          </div>

          <div className="lg:col-span-2 flex items-end gap-2">
            {selectedMatches.length > 0 && (
              <button
                onClick={() => shortlistMutation.mutate(selectedMatches)}
                disabled={shortlistMutation.isPending}
                className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-300 transition"
              >
                <Star className="w-4 h-4 inline mr-2" />
                Shortlist {selectedMatches.length} Selected
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Results */}
      {matchesLoading ? (
        <div className="flex items-center justify-center min-h-96">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : !matchesData || filteredMatches.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Matches Found</h3>
          <p className="text-gray-600 mb-6">
            {selectedBatchId === 'all' 
              ? 'Run the matching algorithm to find candidates for this job description'
              : 'No candidates from the selected batch match the criteria. Try lowering the minimum score or select a different batch.'}
          </p>
          <button
            onClick={() => matchMutation.mutate()}
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            <Zap className="w-5 h-5" />
            Run Matching Now
          </button>
        </div>
      ) : (
        <>
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {filteredMatches.length} of {filteredTotal} candidates
              {selectedBatchId !== 'all' && ' from selected batch'}
            </p>
            {selectedMatches.length > 0 && (
              <button
                onClick={() => setSelectedMatches([])}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Clear selection
              </button>
            )}
          </div>

          {/* Conditional View: Table or Cards */}
          {viewMode === 'table' ? (
            <CandidateDataTable
              matches={filteredMatches}
              selectedMatches={selectedMatches}
              onToggleSelect={toggleSelectMatch}
              onShortlist={(ids) => shortlistMutation.mutate(ids)}
            />
          ) : (
            <>
              <div className="space-y-4">
              {filteredMatches.map((match) => (
                <div
                  key={match.match_id}
                  className={`bg-white rounded-xl shadow-sm border-2 p-6 transition ${
                    selectedMatches.includes(match.match_id)
                      ? 'border-blue-500'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    {/* Checkbox */}
                    <input
                      type="checkbox"
                      checked={selectedMatches.includes(match.match_id)}
                      onChange={() => toggleSelectMatch(match.match_id)}
                      className="mt-1 w-5 h-5 text-blue-600 rounded"
                    />

                    {/* Score */}
                    <div className={`text-center px-4 py-3 rounded-lg ${getScoreBgColor(match.total_score)}`}>
                      <p className={`text-3xl font-bold ${getScoreColor(match.total_score)}`}>
                        {match.total_score.toFixed(0)}
                      </p>
                      <p className="text-xs text-gray-600">Score</p>
                    </div>

                    {/* Candidate Info */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {match.candidate_name || 'Unknown Name'}
                          </h3>
                          <div className="mt-1 space-y-1">
                            {match.candidate_email && (
                              <p className="text-sm text-gray-600">📧 {match.candidate_email}</p>
                            )}
                            {match.candidate_phone && (
                              <p className="text-sm text-gray-600">📱 {match.candidate_phone}</p>
                            )}
                          </div>
                        </div>

                        {match.is_shortlisted && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                            <Star className="w-4 h-4 fill-current" />
                            Shortlisted
                          </span>
                        )}
                      </div>

                      {/* Score Breakdown */}
                      <div className="grid grid-cols-3 gap-3 mb-3">
                        <div className="bg-gray-50 rounded px-3 py-2">
                          <p className="text-xs text-gray-500">Skills</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {match.skill_score.toFixed(0)}/{jd.skill_weight}
                          </p>
                        </div>
                        <div className="bg-gray-50 rounded px-3 py-2">
                          <p className="text-xs text-gray-500">Role</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {match.role_score.toFixed(0)}/{jd.role_weight}
                          </p>
                        </div>
                        <div className="bg-gray-50 rounded px-3 py-2">
                          <p className="text-xs text-gray-500">Tools</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {match.tool_score.toFixed(0)}/{jd.tool_weight}
                          </p>
                        </div>
                        <div className="bg-gray-50 rounded px-3 py-2">
                          <p className="text-xs text-gray-500">Experience</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {match.experience_score.toFixed(0)}/{jd.experience_weight}
                          </p>
                        </div>
                        <div className="bg-gray-50 rounded px-3 py-2">
                          <p className="text-xs text-gray-500">Portfolio</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {match.portfolio_score.toFixed(0)}/{jd.portfolio_weight}
                          </p>
                        </div>
                        <div className="bg-gray-50 rounded px-3 py-2">
                          <p className="text-xs text-gray-500">Quality</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {match.quality_score.toFixed(0)}/{jd.quality_weight}
                          </p>
                        </div>
                      </div>

                      {/* Justification */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                        <p className="text-xs font-semibold text-blue-900 mb-1">
                          Why this candidate is a good fit:
                        </p>
                        <p className="text-sm text-blue-800">{match.justification}</p>
                      </div>

                      {/* Skills Match */}
                      {match.matched_skills && match.matched_skills.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs text-gray-500 mb-1">Matched Skills:</p>
                          <div className="flex flex-wrap gap-1">
                            {match.matched_skills.map((skill, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                              >
                                ✓ {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {match.missing_skills && match.missing_skills.length > 0 && (
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Missing Skills:</p>
                          <div className="flex flex-wrap gap-1">
                            {match.missing_skills.slice(0, 5).map((skill, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full"
                              >
                                ✗ {skill}
                              </span>
                            ))}
                            {match.missing_skills.length > 5 && (
                              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                +{match.missing_skills.length - 5} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {matchesData?.total_pages && matchesData.total_pages > 1 && (
              <div className="mt-6 flex items-center justify-center gap-2">
                {Array.from({ length: Math.min(matchesData.total_pages, 5) }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => setFilters({ ...filters, page })}
                    className={`px-4 py-2 rounded-lg font-medium transition ${
                      page === filters.page
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
            )}
            </>
          )}
        </>
      )}
    </div>
  );
}
