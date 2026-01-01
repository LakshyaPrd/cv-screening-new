'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { Briefcase, Plus, X, AlertCircle } from 'lucide-react';
import api, { JobDescriptionCreate } from '@/lib/api';

export default function CreateJobDescriptionPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<JobDescriptionCreate>({
    title: '',
    description: '',
    must_have_skills: [],
    nice_to_have_skills: [],
    required_tools: [],
    role_keywords: [],
    location_preference: '',
    skill_weight: 40,
    role_weight: 20,
    tool_weight: 15,
    experience_weight: 15,
    portfolio_weight: 10,
    quality_weight: 5,
    minimum_score_threshold: 50,
  });

  const [skillInput, setSkillInput] = useState('');
  const [niceSkillInput, setNiceSkillInput] = useState('');
  const [toolInput, setToolInput] = useState('');
  const [roleInput, setRoleInput] = useState('');

  const createMutation = useMutation({
    mutationFn: (data: JobDescriptionCreate) => api.createJobDescription(data),
    onSuccess: (data) => {
      router.push(`/job-descriptions/${data.jd_id}`);
    },
  });

  const addItem = (field: keyof JobDescriptionCreate, value: string, resetFn: (v: string) => void) => {
    if (!value.trim()) return;
    const current = (formData[field] as string[]) ?? [];
    if (!current.includes(value.trim())) {
      setFormData({
        ...formData,
        [field]: [...current, value.trim()],
      });
    }
    resetFn('');
  };

  const removeItem = (field: keyof JobDescriptionCreate, index: number) => {
    const current = (formData[field] as string[]) ?? [];
    setFormData({
      ...formData,
      [field]: current.filter((_, i) => i !== index),
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate weights sum to 100
    const totalWeight = 
      formData.skill_weight! +
      formData.role_weight! +
      formData.tool_weight! +
      formData.experience_weight! +
      formData.portfolio_weight! +
      formData.quality_weight!;
    
    if (totalWeight !== 100) {
      alert(`Weights must sum to 100. Current total: ${totalWeight}`);
      return;
    }

    createMutation.mutate(formData);
  };

  const totalWeight = 
    (formData.skill_weight || 0) +
    (formData.role_weight || 0) +
    (formData.tool_weight || 0) +
    (formData.experience_weight || 0) +
    (formData.portfolio_weight || 0) +
    (formData.quality_weight || 0);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create Job Description</h1>
        <p className="text-gray-600 mt-2">
          Define job requirements and scoring criteria for candidate matching
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Title *
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., Senior BIM Architect"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Description *
              </label>
              <textarea
                required
                rows={6}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe the role, responsibilities, and requirements..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location Preference
              </label>
              <input
                type="text"
                value={formData.location_preference}
                onChange={(e) => setFormData({ ...formData, location_preference: e.target.value })}
                placeholder="e.g., Dubai, Remote, Hybrid"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
            </div>
          </div>
        </div>

        {/* Requirements */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Requirements</h2>

          {/* Must-Have Skills */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Must-Have Skills *
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('must_have_skills', skillInput, setSkillInput))}
                placeholder="e.g., Revit, BIM"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
              <button
                type="button"
                onClick={() => addItem('must_have_skills', skillInput, setSkillInput)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.must_have_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => removeItem('must_have_skills', idx)}
                    className="hover:text-red-900"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Nice-to-Have Skills */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nice-to-Have Skills
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={niceSkillInput}
                onChange={(e) => setNiceSkillInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('nice_to_have_skills', niceSkillInput, setNiceSkillInput))}
                placeholder="e.g., Navisworks, 3ds Max"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
              <button
                type="button"
                onClick={() => addItem('nice_to_have_skills', niceSkillInput, setNiceSkillInput)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.nice_to_have_skills?.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => removeItem('nice_to_have_skills', idx)}
                    className="hover:text-blue-900"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Required Tools */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Required Software/Tools
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={toolInput}
                onChange={(e) => setToolInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('required_tools', toolInput, setToolInput))}
                placeholder="e.g., AutoCAD, BIM 360"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
              <button
                type="button"
                onClick={() => addItem('required_tools', toolInput, setToolInput)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.required_tools?.map((tool, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm text-gray-900"
                >
                  {tool}
                  <button
                    type="button"
                    onClick={() => removeItem('required_tools', idx)}
                    className="hover:text-green-900"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Role Keywords */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Role Keywords
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={roleInput}
                onChange={(e) => setRoleInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('role_keywords', roleInput, setRoleInput))}
                placeholder="e.g., BIM Architect, Design Manager"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
              <button
                type="button"
                onClick={() => addItem('role_keywords', roleInput, setRoleInput)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.role_keywords?.map((role, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm text-gray-900"
                >
                  {role}
                  <button
                    type="button"
                    onClick={() => removeItem('role_keywords', idx)}
                    className="hover:text-purple-900"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Scoring Weights */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Scoring Weights</h2>
          <p className="text-sm text-gray-600 mb-4">
            Adjust how much each factor contributes to the overall match score (must sum to 100)
          </p>

          {totalWeight !== 100 && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <span className="text-sm text-yellow-800">
                Total weight: {totalWeight}% (must be exactly 100%)
              </span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            {[
              { key: 'skill_weight', label: 'Skills Match', default: 40 },
              { key: 'role_weight', label: 'Role/Title Match', default: 20 },
              { key: 'tool_weight', label: 'Tools/Software', default: 15 },
              { key: 'experience_weight', label: 'Experience', default: 15 },
              { key: 'portfolio_weight', label: 'Portfolio', default: 10 },
              { key: 'quality_weight', label: 'CV Quality', default: 5 },
            ].map(({ key, label, default: defaultVal }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {label}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={formData[key as keyof JobDescriptionCreate] as number}
                    onChange={(e) => setFormData({
                      ...formData,
                      [key]: parseInt(e.target.value)
                    })}
                    className="flex-1"
                  />
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData[key as keyof JobDescriptionCreate] as number}
                    onChange={(e) => setFormData({
                      ...formData,
                      [key]: parseInt(e.target.value) || 0
                    })}
                    className="w-16 px-2 py-1 border border-gray-300 rounded text-center text-gray-900"
                  />
                  <span className="text-sm text-gray-600">%</span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Score Threshold
            </label>
            <div className="flex items-center gap-2 max-w-xs">
              <input
                type="range"
                min="0"
                max="100"
                value={formData.minimum_score_threshold}
                onChange={(e) => setFormData({
                  ...formData,
                  minimum_score_threshold: parseInt(e.target.value)
                })}
                className="flex-1"
              />
              <input
                type="number"
                min="0"
                max="100"
                value={formData.minimum_score_threshold}
                onChange={(e) => setFormData({
                  ...formData,
                  minimum_score_threshold: parseInt(e.target.value) || 0
                })}
                className="w-16 px-2 py-1 border border-gray-300 rounded text-center text-gray-900"
              />
              <span className="text-sm text-gray-600">%</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Only candidates scoring above this threshold will be shown
            </p>
          </div>
        </div>

        {/* Submit */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={createMutation.isPending || totalWeight !== 100}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Job Description'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
        </div>

        {createMutation.isError && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">
              Error: {(createMutation.error as any)?.response?.data?.detail || 'Failed to create job description'}
            </p>
          </div>
        )}
      </form>
    </div>
  );
}
