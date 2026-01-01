'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Briefcase, Plus, Loader2, MapPin } from 'lucide-react';
import api from '@/lib/api';
import { formatDate } from '@/lib/utils';

export default function JobDescriptionsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['job-descriptions'],
    queryFn: () => api.listJobDescriptions(0, 20),
  });

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Job Descriptions</h1>
          <p className="text-gray-600 mt-2">Manage job descriptions and match candidates</p>
        </div>
        <Link
          href="/job-descriptions/create"
          className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
        >
          <Plus className="w-5 h-5" />
          Create New JD
        </Link>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center min-h-96">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : !data || data.job_descriptions.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Briefcase className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Job Descriptions Yet</h3>
          <p className="text-gray-600 mb-6">
            Create your first job description to start matching candidates
          </p>
          <Link
            href="/job-descriptions/create"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            <Plus className="w-5 h-5" />
            Create Job Description
          </Link>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {data.job_descriptions.map((jd) => (
            <Link
              key={jd.jd_id}
              href={`/job-descriptions/${jd.jd_id}`}
              className="block bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:border-blue-300 hover:shadow-md transition"
            >
              <div className="flex items-start gap-3 mb-4">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Briefcase className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-900">{jd.title}</h3>
                  {jd.location_preference && (
                    <div className="flex items-center gap-1 text-sm text-gray-600 mt-1">
                      <MapPin className="w-4 h-4" />
                      {jd.location_preference}
                    </div>
                  )}
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {jd.description}
              </p>

              <div className="space-y-2 mb-4">
                {/* Must-Have Skills */}
                {jd.must_have_skills && jd.must_have_skills.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Must-Have Skills:</p>
                    <div className="flex flex-wrap gap-1">
                      {jd.must_have_skills.slice(0, 3).map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                      {jd.must_have_skills.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{jd.must_have_skills.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Tools */}
                {jd.required_tools && jd.required_tools.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Required Tools:</p>
                    <div className="flex flex-wrap gap-1">
                      {jd.required_tools.slice(0, 3).map((tool, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full"
                        >
                          {tool}
                        </span>
                      ))}
                      {jd.required_tools.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{jd.required_tools.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div>
                  <p className="text-xs text-gray-500">Min. Score</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {jd.minimum_score_threshold}%
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Created</p>
                  <p className="text-sm text-gray-900">{formatDate(jd.created_at)}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {data && data.total > 20 && (
        <div className="mt-6 text-center text-sm text-gray-600">
          Showing {Math.min(20, data.total)} of {data.total} job descriptions
        </div>
      )}
    </div>
  );
}
