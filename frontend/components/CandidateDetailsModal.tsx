import React from 'react';
import { X, MapPin, Briefcase, Mail, Phone, ExternalLink, Calendar, Star, Award, GraduationCap, CheckCircle, XCircle, Brain, Target, Wrench } from 'lucide-react';
import { Match } from './CandidateDataTable';

interface CandidateDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  match: Match | null;
}

export default function CandidateDetailsModal({ isOpen, onClose, match }: CandidateDetailsModalProps) {
  if (!isOpen || !match) return null;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-orange-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-blue-50 border-orange-200';
    if (score >= 40) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm overflow-y-auto">
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header - Fixed at top */}
        <div className="flex items-start justify-between p-6 border-b border-gray-100 bg-white z-10">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{match.candidate_name || 'Candidate Details'}</h2>
            <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-gray-600">
              {match.current_position && (
                <div className="flex items-center gap-1">
                  <Briefcase className="w-4 h-4 text-gray-400" />
                  {match.current_position}
                </div>
              )}
              {(match.current_city || match.current_country) && (
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  <span>{[match.current_city, match.current_country].filter(Boolean).join(', ')}</span>
                </div>
              )}
              {match.total_experience_years !== undefined && (
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>{match.total_experience_years} Years Experience</span>
                </div>
              )}
            </div>
            
            {/* Contact Info */}
            <div className="flex flex-wrap gap-4 mt-3">
              {match.candidate_email && (
                <a href={`mailto:${match.candidate_email}`} className="flex items-center gap-1.5 text-sm text-orange-600 hover:text-orange-800 bg-blue-50 px-2 py-1 rounded">
                  <Mail className="w-3.5 h-3.5" />
                  {match.candidate_email}
                </a>
              )}
              {match.candidate_phone && (
                <a href={`tel:${match.candidate_phone}`} className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 bg-gray-50 px-2 py-1 rounded">
                  <Phone className="w-3.5 h-3.5" />
                  {match.candidate_phone}
                </a>
              )}
              {match.linkedin_url && (
                <a href={match.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 text-sm text-[#0077b5] hover:underline bg-blue-50 px-2 py-1 rounded">
                  <ExternalLink className="w-3.5 h-3.5" />
                  LinkedIn Profile
                </a>
              )}
            </div>
          </div>
          
          <div className={`flex flex-col items-center justify-center p-4 rounded-xl border ${getScoreBg(match.total_score || 0)}`}>
            <span className={`text-3xl font-bold ${getScoreColor(match.total_score || 0)}`}>
              {(match.total_score || 0).toFixed(0)}
            </span>
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Match Score</span>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="overflow-y-auto p-6 space-y-8">
          
          {/* AI Analysis & Justification */}
          {match.justification && (
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-600" />
                AI Analysis
              </h3>
              <div className="bg-purple-50 border border-purple-100 rounded-xl p-4">
                <p className="text-gray-800 leading-relaxed">{match.justification}</p>
              </div>
              
              {/* Score Breakdown */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-4">
                {[
                  { label: 'Skills', val: match.skill_score },
                  { label: 'Role', val: match.role_score },
                  { label: 'Tools', val: match.tool_score },
                  { label: 'Experience', val: match.experience_score },
                  { label: 'Portfolio', val: match.portfolio_score },
                  { label: 'Quality', val: match.quality_score },
                ].map((item, idx) => (
                   item.val !== undefined && (
                    <div key={idx} className="bg-gray-50 rounded-lg p-3 text-center border border-gray-100">
                      <div className="text-xs text-gray-500 mb-1">{item.label}</div>
                      <div className="font-bold text-gray-900">{item.val.toFixed(0)}</div>
                    </div>
                  )
                ))}
              </div>
            </section>
          )}

          {/* Skills Analysis */}
          <section className="grid md:grid-cols-2 gap-6">
            {/* Matched Skills */}
            {match.matched_skills && match.matched_skills.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Matched Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {match.matched_skills.map((skill, idx) => (
                    <span key={idx} className="px-3 py-1.5 bg-green-50 text-green-700 rounded-lg text-sm border border-green-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Missing Skills */}
            {match.missing_skills && match.missing_skills.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <XCircle className="w-4 h-4 text-red-600" />
                  Missing Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {match.missing_skills.map((skill, idx) => (
                    <span key={idx} className="px-3 py-1.5 bg-red-50 text-red-700 rounded-lg text-sm border border-red-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* Work History */}
          {match.work_history && match.work_history.length > 0 && (
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-orange-600" />
                Work History
              </h3>
              <div className="space-y-4">
                {match.work_history.map((job, idx) => (
                  <div key={idx} className="relative pl-6 pb-6 border-l-2 border-gray-200 last:border-0 last:pb-0">
                    <div className="absolute top-0 left-[-9px] w-4 h-4 rounded-full bg-blue-100 border-2 border-orange-500"></div>
                    <div>
                      <h4 className="font-semibold text-gray-900 text-base">{job.job_title}</h4>
                      <div className="text-sm font-medium text-gray-700 mt-1">
                        {job.company_name} {job.company_location ? `• ${job.company_location}` : ''}
                      </div>
                      <div className="text-xs text-gray-500 mt-1 mb-2">
                        {job.start_date} - {job.end_date} 
                        {job.duration_months && ` • ${Math.floor(job.duration_months/12)}y ${job.duration_months%12}m`}
                      </div>
                      {/* Detailed info if available in extract (not explicitly in Match interface but logical to display if I add it) */}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Education */}
          {match.education_details && match.education_details.length > 0 && (
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-indigo-600" />
                Education
              </h3>
              <div className="grid gap-4">
                {match.education_details.map((edu, idx) => (
                  <div key={idx} className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                    <h4 className="font-semibold text-gray-900">{edu.degree}</h4>
                    {edu.major && <div className="text-indigo-600 text-sm font-medium mt-1">{edu.major}</div>}
                    <div className="text-sm text-gray-600 mt-1">
                      {edu.graduation_year ? `Graduated: ${edu.graduation_year}` : ''}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Software & Skills */}
          {match.software_experience && match.software_experience.length > 0 && (
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Wrench className="w-5 h-5 text-orange-600" />
                Software Proficiency
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {match.software_experience.map((sw, idx) => (
                  <div key={idx} className="bg-white border border-gray-200 p-3 rounded-lg shadow-sm">
                    <div className="font-medium text-gray-900">{sw.software_name}</div>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs bg-gray-100 px-2 py-0.5 rounded text-gray-600">{sw.proficiency_level || 'User'}</span>
                      <span className="text-xs text-gray-500">{sw.years_of_experience?.toFixed(1) || '-'} yrs</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex justify-end">
          <button 
            onClick={onClose}
            className="px-6 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-100 transition shadow-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
