'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ExternalLink, MapPin, Building, Briefcase, DollarSign, Clock, Eye } from 'lucide-react';
import CandidateDetailsModal from './CandidateDetailsModal';

export interface Match {
  match_id: string;
  candidate_id: string;
  total_score: number;
  
  // Basic Info
  candidate_name?: string;
  candidate_email?: string;
  candidate_phone?: string;
  nationality?: string;
  marital_status?: string;
  current_city?: string;
  current_country?: string;
  
  // Position & Experience
  current_position?: string;
  discipline?: string;
  sub_discipline?: string;
  total_experience_years?: number;
  gcc_experience_years?: number;
  worked_on_gcc_projects?: boolean;
  worked_with_mncs?: boolean;
  
  // Work History
  work_history?: Array<{
    job_title: string;
    seniority_level?: string;
    company_name?: string;
    company_location?: string;
    start_date?: string;
    end_date?: string;
    duration_months?: number;
    mode_of_work?: string;
  }>;
  latest_company?: string;
  latest_position?: string;
  
  // Software & Skills
  top_software?: string[];
  software_experience?: Array<{
    software_name: string;
    proficiency_level?: string;
    years_of_experience?: number;
  }>;
  
  // Education
  highest_degree?: string;
  education_details?: Array<{
    degree: string;
    major?: string;
    graduation_year?: string;
  }>;
  
  // Salary & Availability
  expected_salary_aed?: number;
  notice_period_days?: number;
  willing_to_relocate?: boolean;
  willing_to_travel?: boolean;
  
  // Evaluation
  portfolio_relevancy_score?: number;
  english_proficiency?: string;
  soft_skills?: string[];

  // Detailed Scores & Justification
  skill_score?: number;
  role_score?: number;
  tool_score?: number;
  experience_score?: number;
  portfolio_score?: number;
  quality_score?: number;
  justification?: string;
  matched_skills?: string[];
  missing_skills?: string[];
  
  // Links
  linkedin_url?: string;
  portfolio_url?: string;
  
  // Match Flags
  is_shortlisted?: boolean;
}

interface CandidateDataTableProps {
  matches: Match[];
  onShortlist?: (matchIds: string[]) => void;
  selectedMatches?: string[];
  onToggleSelect?: (matchId: string) => void;
}

export default function CandidateDataTable({
  matches,
  onShortlist,
  selectedMatches = [],
  onToggleSelect,
}: CandidateDataTableProps) {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<Match | null>(null);
  const [sortBy, setSortBy] = useState<string>('total_score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const sortedMatches = [...matches].sort((a, b) => {
    let aVal: any = (a as any)[sortBy];
    let bVal: any = (b as any)[sortBy];
    
    if (aVal === null || aVal === undefined) return 1;
    if (bVal === null || bVal === undefined) return -1;
    
    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-blue-600 bg-blue-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const toggleExpand = (matchId: string) => {
    setExpandedRow(expandedRow === matchId ? null : matchId);
  };

  return (
    <>
    <div className="overflow-x-auto bg-white rounded-xl shadow-sm border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {onToggleSelect && (
              <th className="px-3 py-3 text-left">
                <input type="checkbox" className="rounded" />
              </th>
            )}
            <th className="px-3 py-3 text-left w-20">Actions</th>
            <th
              className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('total_score')}
            >
              Score {sortBy === 'total_score' && (sortOrder === 'asc' ? '↑' : '↓')}
            </th>
            <th
              className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('candidate_name')}
            >
              Name {sortBy === 'candidate_name' && (sortOrder === 'asc' ? '↑' : '↓')}
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
              Position & Discipline
            </th>
            <th
              className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('total_experience_years')}
            >
              Exp (Years) {sortBy === 'total_experience_years' && (sortOrder === 'asc' ? '↑' : '↓')}
            </th>
            <th
              className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('gcc_experience_years')}
            >
              GCC Exp {sortBy === 'gcc_experience_years' && (sortOrder === 'asc' ? '↑' : '↓')}
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
              Top Software
            </th>
            <th
              className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              onClick={() => handleSort('expected_salary_aed')}
            >
              Salary (AED) {sortBy === 'expected_salary_aed' && (sortOrder === 'asc' ? '↑' : '↓')}
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
              Contact
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedMatches.map((match) => (
            <React.Fragment key={match.match_id}>
              <tr
                className={`hover:bg-gray-50 ${
                  selectedMatches.includes(match.match_id) ? 'bg-blue-50' : ''
                }`}
              >
                {onToggleSelect && (
                  <td className="px-3 py-4">
                    <input
                      type="checkbox"
                      checked={selectedMatches.includes(match.match_id)}
                      onChange={() => onToggleSelect(match.match_id)}
                      className="rounded text-blue-600"
                    />
                  </td>
                )}
                <td className="px-3 py-4">
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setSelectedCandidate(match)}
                      className="p-1 text-blue-600 hover:bg-blue-50 rounded transition"
                      title="View Full Details"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => toggleExpand(match.match_id)}
                      className="text-gray-500 hover:text-gray-700 p-1 hover:bg-gray-100 rounded transition"
                      title="Expand Row"
                    >
                      {expandedRow === match.match_id ? (
                        <ChevronUp className="w-5 h-5" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${getScoreColor(match.total_score)}`}>
                    {match.total_score.toFixed(0)}
                  </span>
                </td>
                <td className="px-4 py-4">
                  <div className="text-sm font-medium text-gray-900">{match.candidate_name || 'Unknown'}</div>
                  <div className="text-xs text-gray-500 flex items-center mt-1">
                    <MapPin className="w-3 h-3 mr-1" />
                    {match.current_city || match.current_country || 'N/A'}
                    {match.nationality && <span className="ml-2">• {match.nationality}</span>}
                  </div>
                </td>
                <td className="px-4 py-4">
                  <div className="text-sm font-medium text-gray-900">
                    {match.current_position || match.latest_position || 'N/A'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {match.discipline && <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded mr-1">{match.discipline}</span>}
                    {match.sub_discipline && <span className="text-gray-600">{match.sub_discipline}</span>}
                  </div>
                </td>
                <td className="px-4 py-4">
                  <div className="text-sm font-semibold text-gray-900">
                    {match.total_experience_years?.toFixed(1) || 'N/A'}
                  </div>
                  {match.worked_with_mncs && (
                    <div className="text-xs text-green-600 font-medium">MNC ✓</div>
                  )}
                </td>
                <td className="px-4 py-4">
                  <div className="text-sm font-semibold text-gray-900">
                    {match.gcc_experience_years?.toFixed(1) || '0'} yrs
                  </div>
                  {match.worked_on_gcc_projects && (
                    <div className="text-xs text-green-600">GCC Projects ✓</div>
                  )}
                </td>
                <td className="px-4 py-4">
                  <div className="flex flex-wrap gap-1">
                    {match.top_software?.slice(0, 3).map((software, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 bg-purple-100 text-purple-800 text-xs rounded"
                      >
                        {software}
                      </span>
                    ))}
                    {(match.top_software?.length || 0) > 3 && (
                      <span className="text-xs text-gray-500">+{match.top_software!.length - 3}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-4">
                  {match.expected_salary_aed ? (
                    <div className="text-sm font-semibold text-gray-900 flex items-center">
                      <DollarSign className="w-3 h-3 mr-1" />
                      {match.expected_salary_aed.toLocaleString()}
                    </div>
                  ) : (
                    <span className="text-xs text-gray-400">Not specified</span>
                  )}
                  {match.notice_period_days !== null && match.notice_period_days !== undefined && (
                    <div className="text-xs text-gray-500 flex items-center mt-1">
                      <Clock className="w-3 h-3 mr-1" />
                      {match.notice_period_days} days
                    </div>
                  )}
                </td>
                <td className="px-4 py-4">
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>{match.candidate_email || 'N/A'}</div>
                    <div>{match.candidate_phone || 'N/A'}</div>
                    {match.linkedin_url && (
                      <a
                        href={match.linkedin_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 flex items-center"
                      >
                        <ExternalLink className="w-3 h-3 mr-1" />
                        LinkedIn
                      </a>
                    )}
                  </div>
                </td>
              </tr>
              
              {/* Expanded Row - Work History Details */}
              {expandedRow === match.match_id && (
                <tr className="bg-gray-50">
                  <td colSpan={onToggleSelect ? 10 : 9} className="px-6 py-4">
                    <div className="space-y-4">
                      {/* Work History Table */}
                      {match.work_history && match.work_history.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                            <Briefcase className="w-4 h-4 mr-2" />
                            Work History
                          </h4>
                          <div className="overflow-x-auto">
                            <table className="min-w-full bg-white shadow-sm rounded-lg text-xs">
                              <thead className="bg-gray-100">
                                <tr>
                                  <th className="px-3 py-2 text-left font-medium text-gray-700">Job Title</th>
                                  <th className="px-3 py-2 text-left font-medium text-gray-700">Seniority</th>
                                  <th className="px-3 py-2 text-left font-medium text-gray-700">Company</th>
                                  <th className="px-3 py-2 text-left font-medium text-gray-700">Location</th>
                                  <th className="px-3 py-2 text-left font-medium text-gray-700">Duration</th>
                                  <th className="px-3 py-2 text-left font-medium text-gray-700">Mode</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-gray-200">
                                {match.work_history.map((job, idx) => (
                                  <tr key={idx}>
                                    <td className="px-3 py-2 text-gray-900">{job.job_title}</td>
                                    <td className="px-3 py-2">
                                      <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded">
                                        {job.seniority_level || 'N/A'}
                                      </span>
                                    </td>
                                    <td className="px-3 py-2 text-gray-700">{job.company_name || 'N/A'}</td>
                                    <td className="px-3 py-2 text-gray-600">{job.company_location || 'N/A'}</td>
                                    <td className="px-3 py-2 text-gray-700">
                                      <div>{job.start_date} - {job.end_date}</div>
                                      {job.duration_months && (
                                        <div className="text-gray-500">
                                          ({Math.floor(job.duration_months / 12)}y {job.duration_months % 12}m)
                                        </div>
                                      )}
                                    </td>
                                    <td className="px-3 py-2 text-gray-600">{job.mode_of_work || 'On-site'}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}

                      {/* Software Skills */}
                      {match.software_experience && match.software_experience.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">Software Proficiency</h4>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                            {match.software_experience.map((sw, idx) => (
                              <div key={idx} className="bg-white p-2 rounded border border-gray-200">
                                <div className="font-medium text-gray-900 text-sm">{sw.software_name}</div>
                                <div className="text-xs text-gray-600">
                                  {sw.proficiency_level || 'Intermediate'} • {sw.years_of_experience?.toFixed(1) || '1'} yrs
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Additional Info */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t border-gray-200">
                        {match.highest_degree && (
                          <div>
                            <div className="text-xs text-gray-500">Education</div>
                            <div className="text-sm font-medium text-gray-900">{match.highest_degree}</div>
                          </div>
                        )}
                        {match.english_proficiency && (
                          <div>
                            <div className="text-xs text-gray-500">English</div>
                            <div className="text-sm font-medium text-gray-900">{match.english_proficiency}</div>
                          </div>
                        )}
                        {match.portfolio_relevancy_score !== null && match.portfolio_relevancy_score !== undefined && (
                          <div>
                            <div className="text-xs text-gray-500">Portfolio Score</div>
                            <div className="text-sm font-medium text-gray-900">{match.portfolio_relevancy_score.toFixed(0)}/100</div>
                          </div>
                        )}
                        {match.soft_skills && match.soft_skills.length > 0 && (
                          <div>
                            <div className="text-xs text-gray-500">Soft Skills</div>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {match.soft_skills.slice(0, 3).map((skill, idx) => (
                                <span key={idx} className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Personal & Availability Details */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 mt-4">
                        {match.nationality && (
                          <div>
                            <div className="text-xs text-gray-500">Nationality</div>
                            <div className="text-sm font-medium text-gray-900">{match.nationality}</div>
                          </div>
                        )}
                        {match.marital_status && (
                          <div>
                            <div className="text-xs text-gray-500">Marital Status</div>
                            <div className="text-sm font-medium text-gray-900">{match.marital_status}</div>
                          </div>
                        )}
                        <div>
                          <div className="text-xs text-gray-500">Relocation</div>
                          <div className="text-sm font-medium text-gray-900">
                            {match.willing_to_relocate ? (
                              <span className="text-green-600">✓ Willing</span>
                            ) : (
                              <span className="text-gray-400">✗ Not specified</span>
                            )}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500">Travel</div>
                          <div className="text-sm font-medium text-gray-900">
                            {match.willing_to_travel ? (
                              <span className="text-green-600">✓ Willing</span>
                            ) : (
                              <span className="text-gray-400">✗ Not specified</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>

      {matches.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No candidates found matching the criteria
        </div>
      )}
    </div>
    
    <CandidateDetailsModal 
        isOpen={!!selectedCandidate} 
        onClose={() => setSelectedCandidate(null)} 
        match={selectedCandidate} 
      />
    </>
  );
}
