'use client';

import { use, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { Loader2, Zap, Users, Eye, X } from 'lucide-react';
import api from '@/lib/api';

interface Match {
  match_id: string;
  candidate_id: string;
  match_score: number;
  total_score: number;
  candidate_name?: string;
  candidate_email?: string;
  candidate_phone?: string;
  candidate_location?: string;
  current_city?: string;
  created_at: string;
  is_shortlisted: boolean;
  justification?: string;
  matched_skills?: string[];
  missing_skills?: string[];
  work_history?: Array<{
    job_title: string;
    company_name?: string;
    start_date?: string;
    end_date?: string;
  }>;
  education_details?: Array<{
    degree: string;
    major?: string;
    graduation_year?: string;
  }>;
  skill_score?: number;
  role_score?: number;
  tool_score?: number;
  experience_score?: number;
  portfolio_score?: number;
  quality_score?: number;
}

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

  // API already returns batch-filtered matches when batch_id is provided
  const filteredCandidates = matchesData?.matches || [];

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

  const getInitials = (name?: string) => {
    if (!name) return '??';
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
        <div className="max-w-7xl mx-auto px-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Candidates Found</h3>
            <p className="text-gray-600">
              {matchesData?.matches.length ? 
                "No candidates from this batch match the current filters" :
                "Run the matching algorithm to find suitable candidates"}
            </p>
          </div>
        </div>
      ) : (
        <div className="max-w-full mx-auto px-6 pb-8">
          {/* Split View: Candidate List + Profile Panel */}
          <div className="flex gap-0 h-[calc(100vh-350px)]">
            {/* LEFT: Candidate List */}
            <div className="w-80 bg-white border-r border-gray-200">
              <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">Candidates</h3>
                  <span className="text-sm text-gray-600">{filteredCandidates.length} found</span>
                </div>
                <input
                  type="text"
                  placeholder="Search candidates..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
              
              <div className="overflow-y-auto h-[calc(100%-80px)]">
                {filteredCandidates.map((candidate) => (
                  <div
                    key={candidate.match_id}
                    onClick={() => handleCardClick(candidate)}
                    className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition ${
                      selectedCandidate?.match_id === candidate.match_id ? 'bg-orange-50 border-l-4 border-l-orange-600' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-full ${
                        selectedCandidate?.match_id === candidate.match_id 
                          ? 'bg-gradient-to-br from-orange-500 to-orange-700' 
                          : 'bg-gradient-to-br from-orange-400 to-orange-600'
                      } flex items-center justify-center text-white font-bold text-sm flex-shrink-0`}>
                        {getInitials(candidate.candidate_name)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="font-semibold text-gray-900 truncate">
                            {candidate.candidate_name || 'Unknown'}
                          </h4>
                          {isNewCandidate(candidate) && (
                            <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full font-medium flex-shrink-0">
                              NEW
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 truncate">{candidate.candidate_email || 'No email'}</p>
                        <div className="flex items-center justify-between mt-2">
                          <span className={`text-2xl font-bold ${
                            candidate.match_score >= 80 ? 'text-green-600' :
                            candidate.match_score >= 60 ? 'text-orange-600' :
                            candidate.match_score >= 40 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {candidate.match_score}%
                          </span>
                          {candidate.is_shortlisted && (
                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs rounded-full font-medium">
                              Shortlisted
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* RIGHT: Profile Panel */}
            <div className="flex-1 overflow-y-auto bg-gray-50">
              {selectedCandidate ? (
                <div>
                  {/* Profile Header */}
                  <div className="bg-white border-b border-gray-200 p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-500 to-orange-700 flex items-center justify-center text-white font-bold text-xl">
                          {getInitials(selectedCandidate.candidate_name)}
                        </div>
                        <div>
                          <h2 className="text-2xl font-bold text-gray-900">{selectedCandidate.candidate_name || 'Unknown'}</h2>
                          <p className="text-gray-600 mt-1">{selectedCandidate.candidate_email || 'No email'}</p>
                          <div className="flex items-center gap-3 mt-2">
                            <span className={`text-3xl font-bold ${
                              selectedCandidate.match_score >= 80 ? 'text-green-600' :
                              selectedCandidate.match_score >= 60 ? 'text-orange-600' :
                              selectedCandidate.match_score >= 40 ? 'text-yellow-600' :
                              'text-red-600'
                            }`}>
                              {selectedCandidate.match_score}%
                            </span>
                            <span className="text-gray-500 text-sm">Match Score</span>
                            {selectedCandidate.is_shortlisted && (
                              <span className="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full font-medium">
                                Shortlisted
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedCandidate(null)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="w-6 h-6" />
                      </button>
                    </div>
                  </div>

                  {/* Tabs */}
                  <div className="bg-white border-b border-gray-200">
                    <div className="flex gap-1 px-6">
                      {[
                        { id: 'cv', label: 'CV Details' },
                        { id: 'notes', label: 'Notes' },
                        { id: 'tags', label: 'Tags' },
                        { id: 'email', label: 'Email Info' },
                      ].map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id as any)}
                          className={`px-6 py-3 font-medium text-sm border-b-2 transition ${
                            activeTab === tab.id
                              ? 'border-orange-600 text-orange-600'
                              : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                          }`}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Tab Content */}
                  <div className="p-6">
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
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Eye className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Select a Candidate</h3>
                    <p className="text-gray-600">Click on a candidate from the list to view their profile</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
