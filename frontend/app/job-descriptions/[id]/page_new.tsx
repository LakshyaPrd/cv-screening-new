'use client';

import { use, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { Loader2, Zap, Star, Users, Eye, X } from 'lucide-react';
import api from '@/lib/api';
import { Match } from '@/components/CandidateDataTable';

export default function JobDescriptionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [selectedMatches, setSelectedMatches] = useState<string[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<Match | null>(null);
  const [selectedBatchId, setSelectedBatchId] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'notes' | 'tags' | 'email' | 'cv'>('cv');
  const [notes, setNotes] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  const [filters, setFilters] = useState({
    min_score: 50,
    is_shortlisted: undefined as boolean | undefined,
    page: 1,
    page_size: 50,
  });

  const { data: jd, isLoading: jdLoading } = useQuery({
    queryKey: ['jd', id],
    queryFn: () => api.getJobDescription(id),
  });

  const { data: batchesList } = useQuery({
    queryKey: ['batches-list'],
    queryFn: () => api.listBatches(0, 100),
  });

  const { data: batchCandidates } = useQuery({
    queryKey: ['batch-candidates', selectedBatchId],
    queryFn: () => selectedBatchId ? api.getBatchCandidates(selectedBatchId, 0, 1000) : null,
    enabled: !!selectedBatchId,
  });

  const { data: matchesData, isLoading: matchesLoading } = useQuery({
    queryKey: ['matches', id, filters],
    queryFn: () => api.getMatches(id, filters),
  });

  const filteredCandidates = matchesData?.matches.filter(match => {
    if (!selectedBatchId) return false;
    return batchCandidates?.candidates.some(c => c.candidate_id === match.candidate_id);
  }) || [];

  const queryClient = useQueryClient();

  const matchMutation = useMutation({
    mutationFn: () => api.matchCandidates(id, selectedBatchId),
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
        <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
      </div>
    );
  }

  if (!jd) {
    return <div className="text-center py-12">Job Description not found</div>;
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const isNewCandidate = (candidate: Match) => {
    const createdAt = new Date(candidate.created_at);
    const now = new Date();
    const diffHours = (now.getTime() - createdAt.getTime()) / (1000 * 60 * 60);
    return diffHours < 24;
  };

  const handleCardClick = (candidate: Match) => {
    setSelectedCandidate(candidate);
    setActiveTab('cv');
  };

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  return (
    <div className="max-w-full mx-auto bg-gray-50 min-h-screen">
      <div className="p-6">
        <Link href="/job-descriptions" className="text-orange-600 hover:text-orange-700 mb-2 inline-block">
          ← Back to Job Descriptions
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{jd.title}</h1>
        <p className="text-gray-600 mt-1">{jd.description}</p>
      </div>

      {/* Actions */}
      <div className="bg-white shadow-sm border-y border-gray-200 p-6 mb-4">
        <div className="max-w-7xl mx-auto">
          <h3 className="font-semibold text-gray-900 mb-4">Candidate Matching</h3>
          
          <div className="grid md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Batch to Match *
              </label>
              <select
                value={selectedBatchId}
                onChange={(e) => setSelectedBatchId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-gray-900"
              >
                <option value="">Select a batch...</option>
                {batchesList?.batches
                  .filter(batch => batch.status === 'completed')
                  .map((batch) => (
                    <option key={batch.batch_id} value={batch.batch_id}>
                      {batch.description || `Batch ${batch.batch_id.slice(0, 8)}`} 
                      {' '}({batch.processed_files} CVs processed)
                    </option>
                  ))}
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={() => matchMutation.mutate()}
                disabled={matchMutation.isPending || !selectedBatchId}
                className="w-full inline-flex items-center justify-center gap-2 bg-orange-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-orange-700 disabled:bg-gray-400 transition"
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
          </div>

          {!selectedBatchId && (
            <div className="mt-3 text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
              Please select a batch to match candidates from
            </div>
          )}

          {matchMutation.isSuccess && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 text-sm">
                ✓ Matching completed successfully! Results are shown below.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      {!selectedBatchId ? (
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Select a Batch to Begin</h3>
            <p className="text-gray-600">
              Choose a batch from the dropdown above and click "Run Matching" to find the best candidates
            </p>
          </div>
        </div>
      ) : matchesLoading ? (
        <div className="flex items-center justify-center min-h-96">
          <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
        </div>
      ) : filteredCandidates.length === 0 ? (
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Matches Found</h3>
            <p className="text-gray-600 mb-6">
              Run the matching algorithm to find candidates from the selected batch
            </p>
            <button
              onClick={() => matchMutation.mutate()}
              disabled={matchMutation.isPending}
              className="inline-flex items-center gap-2 bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-orange-700 transition"
            >
              <Zap className="w-5 h-5" />
              Run Matching Now
            </button>
          </div>
        </div>
      ) : (
        <div className="flex gap-0 h-[calc(100vh-350px)]">
          {/* LEFT PANEL - Candidates List */}
          <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">Candidates</h2>
              <p className="text-sm text-gray-500">{filteredCandidates.length} matched</p>
            </div>

            <div className="flex-1 overflow-y-auto px-4">
              <div className="space-y-3 pb-4 pt-4">
                {filteredCandidates.map((candidate) => {
                  const candidateId = candidate.match_id
                  const isActive = selectedCandidate?.match_id === candidateId
                  const isNew = isNewCandidate(candidate)

                  return (
                    <div
                      key={candidateId}
                      onClick={() => handleCardClick(candidate)}
                      className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all border ${
                        isActive
                          ? 'bg-orange-50 border-orange-200'
                          : 'bg-white border-gray-200 hover:border-orange-300 hover:shadow-sm'
                      }`}
                    >
                      {/* Avatar */}
                      <div className="w-12 h-12 rounded-full bg-white border-2 border-orange-500 flex items-center justify-center text-orange-600 font-bold shrink-0">
                        {getInitials(candidate.candidate_name || 'UN')}
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-gray-900 truncate">
                          {candidate.candidate_name || 'Unknown'}
                        </h4>
                        <p className="text-sm text-gray-600 truncate">
                          {candidate.matched_skills?.slice(0, 3).join(', ') || 'No skills listed'}
                        </p>
                      </div>

                      {/* Badge */}
                      <div className="flex items-center gap-2">
                        {isNew && (
                          <span className="px-2 py-1 bg-orange-500 text-white text-xs font-bold rounded">
                            NEW
                          </span>
                        )}
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* RIGHT PANEL - Candidate Profile */}
          {selectedCandidate ? (
            <div className="flex-1 overflow-y-auto bg-gray-50">
              {(() => {
                const personalInfo = {
                  name: selectedCandidate.candidate_name,
                  email: selectedCandidate.candidate_email,
                  phone: selectedCandidate.candidate_phone,
                  location: selectedCandidate.candidate_location || selectedCandidate.current_city,
                };

                return (
                  <div className="max-w-4xl mx-auto p-8">
                    {/* Header with Close Button */}
                    <div className="flex items-center justify-between mb-8">
                      <h1 className="text-3xl font-bold text-gray-900">
                        Candidate Profile: {personalInfo.name || 'Unknown'}
                      </h1>
                      <button
                        onClick={() => setSelectedCandidate(null)}
                        className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg transition-colors"
                        title="Close profile"
                      >
                        <X className="w-6 h-6" />
                      </button>
                    </div>

                    {/* Profile Card */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
                      <div className="flex items-start gap-6 mb-8">
                        {/* Profile Photo */}
                        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center text-white text-3xl font-bold shrink-0">
                          {getInitials(selectedCandidate.candidate_name || 'UN')}
                        </div>

                        {/* Basic Info */}
                        <div className="flex-1">
                          <h2 className="text-2xl font-bold text-gray-900 mb-1">
                            {personalInfo.name || 'Unknown'}
                          </h2>
                          <p className="text-gray-600 mb-3">
                            {selectedCandidate.current_position || 'Position not specified'}
                          </p>
                          <div className="flex items-center gap-6 text-sm text-gray-600">
                            {personalInfo.email && (
                              <div className="flex items-center gap-2">
                                <svg className="w-4 h-4 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                                </svg>
                                <span>{personalInfo.email}</span>
                              </div>
                            )}
                            {personalInfo.phone && (
                              <div className="flex items-center gap-2">
                                <svg className="w-4 h-4 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                                </svg>
                                <span>{personalInfo.phone}</span>
                              </div>
                            )}
                            {personalInfo.location && (
                              <div className="flex items-center gap-2">
                                <svg className="w-4 h-4 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                                </svg>
                                <span>{personalInfo.location}</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Match Score */}
                        <div className="text-center">
                          <div className="text-4xl font-bold text-orange-600">
                            {selectedCandidate.total_score.toFixed(0)}
                          </div>
                          <div className="text-sm text-gray-500">Match Score</div>
                        </div>
                      </div>

                      {/* Tabs */}
                      <div className="flex gap-6 border-b border-gray-200 mb-6">
                        <button
                          onClick={() => setActiveTab('notes')}
                          className={`pb-3 font-medium transition-colors ${
                            activeTab === 'notes'
                              ? 'text-orange-600 border-b-2 border-orange-600'
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          📝 Notes
                        </button>
                        <button
                          onClick={() => setActiveTab('tags')}
                          className={`pb-3 font-medium transition-colors ${
                            activeTab === 'tags'
                              ? 'text-orange-600 border-b-2 border-orange-600'
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          🏷️ Tags
                        </button>
                        <button
                          onClick={() => setActiveTab('email')}
                          className={`pb-3 font-medium transition-colors ${
                            activeTab === 'email'
                              ? 'text-orange-600 border-b-2 border-orange-600'
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          📧 Email Info
                        </button>
                        <button
                          onClick={() => setActiveTab('cv')}
                          className={`pb-3 font-medium transition-colors ${
                            activeTab === 'cv'
                              ? 'text-orange-600 border-b-2 border-orange-600'
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          👤 CV Details
                        </button>
                      </div>

                      {/* Tab Content */}
                      <div>
                        {/* Notes Tab */}
                        {activeTab === 'notes' && (
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-3">Notes</h4>
                            <textarea
                              value={notes}
                              onChange={(e) => setNotes(e.target.value)}
                              placeholder="Add your notes about this candidate..."
                              className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                            />
                            <button className="mt-3 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm">
                              Save Notes
                            </button>
                          </div>
                        )}

                        {/* Tags Tab */}
                        {activeTab === 'tags' && (
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-3">Tags</h4>
                            <div className="flex gap-2 mb-4">
                              <input
                                type="text"
                                value={newTag}
                                onChange={(e) => setNewTag(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && addTag()}
                                placeholder="Add a tag..."
                                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                              />
                              <button
                                onClick={addTag}
                                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm"
                              >
                                Add
                              </button>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {tags.length > 0 ? (
                                tags.map((tag, index) => (
                                  <span
                                    key={index}
                                    className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm flex items-center gap-2"
                                  >
                                    {tag}
                                    <button
                                      onClick={() => removeTag(tag)}
                                      className="text-orange-600 hover:text-orange-900 font-bold"
                                    >
                                      ×
                                    </button>
                                  </span>
                                ))
                              ) : (
                                <p className="text-gray-500 italic text-sm">No tags added yet</p>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Email Info Tab */}
                        {activeTab === 'email' && (
                          <div className="space-y-4">
                            <h4 className="font-semibold text-gray-900 mb-3">Email Information</h4>
                            <div className="space-y-3">
                              <div>
                                <label className="text-sm font-medium text-gray-700">Email Address</label>
                                <p className="text-gray-900 mt-1">{selectedCandidate.candidate_email || 'N/A'}</p>
                              </div>
                              <div>
                                <label className="text-sm font-medium text-gray-700">Contact</label>
                                <p className="text-gray-900 mt-1">{selectedCandidate.candidate_phone || 'N/A'}</p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* CV Details Tab */}
                        {activeTab === 'cv' && (
                          <div className="space-y-6">
                            <div>
                              <h4 className="text-lg font-semibold text-gray-900 mb-3">📝 Professional Summary</h4>
                              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                                <p className="text-gray-800 leading-relaxed">
                                  {selectedCandidate.justification || 'No summary available'}
                                </p>
                              </div>
                            </div>

                            <div>
                              <h4 className="text-lg font-semibold text-gray-900 mb-3">👤 Personal Information</h4>
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <label className="text-sm font-medium text-gray-700">Name</label>
                                  <p className="text-gray-900 mt-1">{selectedCandidate.candidate_name || 'N/A'}</p>
                                </div>
                                <div>
                                  <label className="text-sm font-medium text-gray-700">Email</label>
                                  <p className="text-gray-900 mt-1">{selectedCandidate.candidate_email || 'N/A'}</p>
                                </div>
                                <div>
                                  <label className="text-sm font-medium text-gray-700">Phone</label>
                                  <p className="text-gray-900 mt-1">{selectedCandidate.candidate_phone || 'N/A'}</p>
                                </div>
                                <div>
                                  <label className="text-sm font-medium text-gray-700">Location</label>
                                  <p className="text-gray-900 mt-1">{selectedCandidate.candidate_location || selectedCandidate.current_city || 'None'}</p>
                                </div>
                              </div>
                            </div>

                            {/* Skills */}
                            <div>
                              <h4 className="text-lg font-semibold text-gray-900 mb-3">✓ Matched Skills</h4>
                              <div className="flex flex-wrap gap-2">
                                {selectedCandidate.matched_skills && selectedCandidate.matched_skills.length > 0 ? (
                                  selectedCandidate.matched_skills.map((skill, idx) => (
                                    <span
                                      key={idx}
                                      className="px-3 py-1.5 bg-green-100 text-green-800 rounded-lg text-sm"
                                    >
                                      {skill}
                                    </span>
                                  ))
                                ) : (
                                  <p className="text-gray-500 text-sm">No matched skills</p>
                                )}
                              </div>
                            </div>

                            {/* Work History */}
                            {selectedCandidate.work_history && selectedCandidate.work_history.length > 0 && (
                              <div>
                                <h4 className="text-lg font-semibold text-gray-900 mb-3">💼 Work Experience</h4>
                                <div className="space-y-4">
                                  {selectedCandidate.work_history.map((job, idx) => (
                                    <div key={idx} className="border-l-2 border-orange-500 pl-4 pb-4">
                                      <h5 className="font-semibold text-gray-900">{job.job_title}</h5>
                                      <p className="text-sm text-gray-600">{job.company_name}</p>
                                      <p className="text-xs text-gray-500 mt-1">
                                        {job.start_date} - {job.end_date}
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Education */}
                            {selectedCandidate.education_details && selectedCandidate.education_details.length > 0 && (
                              <div>
                                <h4 className="text-lg font-semibold text-gray-900 mb-3">🎓 Education</h4>
                                <div className="space-y-3">
                                  {selectedCandidate.education_details.map((edu, idx) => (
                                    <div key={idx} className="bg-gray-50 rounded-lg p-4">
                                      <h5 className="font-semibold text-gray-900">{edu.degree}</h5>
                                      {edu.major && <p className="text-sm text-gray-600">{edu.major}</p>}
                                      {edu.graduation_year && (
                                        <p className="text-xs text-gray-500 mt-1">Graduated: {edu.graduation_year}</p>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-50">
              <div className="text-center text-gray-500">
                <Eye className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p>Select a candidate to view their profile</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
