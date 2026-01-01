'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings, Database, BarChart3, Plus, Trash2, Save } from 'lucide-react';
import api from '@/lib/api';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<'skills' | 'tools' | 'weights' | 'health'>('health');
  const queryClient = useQueryClient();

  // Fetch system health
  const { data: health } = useQuery({
    queryKey: ['admin-health'],
    queryFn: api.getSystemHealth,
  });

  // Fetch dictionaries
  const { data: skills = [] } = useQuery({
    queryKey: ['admin-skills'],
    queryFn: () => api.getDictionary('skills'),
  });

  const { data: tools = [] } = useQuery({
    queryKey: ['admin-tools'],
    queryFn: () => api.getDictionary('tools'),
  });

  // Fetch default weights
  const { data: weights } = useQuery({
    queryKey: ['admin-weights'],
    queryFn: api.getDefaultWeights,
  });

  const [newSkill, setNewSkill] = useState('');
  const [newTool, setNewTool] = useState('');
  const [editWeights, setEditWeights] = useState<any>(null);

  // Mutations
  const addSkillMutation = useMutation({
    mutationFn: (skill: string) => api.updateDictionary('skills', [...skills, skill]),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-skills'] }),
  });

  const removeSkillMutation = useMutation({
    mutationFn: (skill: string) => api.updateDictionary('skills', skills.filter((s: string) => s !== skill)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-skills'] }),
  });

  const addToolMutation = useMutation({
    mutationFn: (tool: string) => api.updateDictionary('tools', [...tools, tool]),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-tools'] }),
  });

  const removeToolMutation = useMutation({
    mutationFn: (tool: string) => api.updateDictionary('tools', tools.filter((t: string) => t !== tool)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-tools'] }),
  });

  const updateWeightsMutation = useMutation({
    mutationFn: (newWeights: any) => api.updateDefaultWeights(newWeights),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-weights'] });
      setEditWeights(null);
    },
  });

  const handleAddSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      addSkillMutation.mutate(newSkill.trim());
      setNewSkill('');
    }
  };

  const handleAddTool = () => {
    if (newTool.trim() && !tools.includes(newTool.trim())) {
      addToolMutation.mutate(newTool.trim());
      setNewTool('');
    }
  };

  const tabs = [
    { id: 'health', label: 'Dashboard', icon: BarChart3 },
    { id: 'skills', label: 'Skills', icon: Database },
    { id: 'tools', label: 'Tools', icon: Database },
    { id: 'weights', label: 'Weights', icon: Settings },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
        <p className="text-gray-600 mt-1">Manage system configuration and dictionaries</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <div className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 pb-4 px-1 border-b-2 font-medium transition ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-5 h-5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Health Dashboard */}
      {activeTab === 'health' && (
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Total Batches</h3>
            <p className="text-3xl font-bold text-gray-900">{health?.total_batches || 0}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Total Candidates</h3>
            <p className="text-3xl font-bold text-gray-900">{health?.total_candidates || 0}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Total Matches</h3>
            <p className="text-3xl font-bold text-gray-900">{health?.total_matches || 0}</p>
          </div>
        </div>
      )}

      {/* Skills Management */}
      {activeTab === 'skills' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Skills Dictionary</h2>
          <p className="text-sm text-gray-600 mb-6">
            These skills are used for extraction and matching. Total: <strong>{skills.length}</strong>
          </p>

          <div className="flex gap-2 mb-6">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
              placeholder="e.g., React, Python, BIM"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            />
            <button
              onClick={handleAddSkill}
              disabled={!newSkill.trim()}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 transition"
            >
              <Plus className="w-4 h-4" />
              Add Skill
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              {skills.map((skill: string) => (
                <div
                  key={skill}
                  className="flex items-center justify-between bg-blue-50 text-blue-900 px-3 py-2 rounded-lg"
                >
                  <span className="text-sm font-medium">{skill}</span>
                  <button
                    onClick={() => removeSkillMutation.mutate(skill)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tools Management */}
      {activeTab === 'tools' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Tools Dictionary</h2>
          <p className="text-sm text-gray-600 mb-6">
            These tools are used for extraction and matching. Total: <strong>{tools.length}</strong>
          </p>

          <div className="flex gap-2 mb-6">
            <input
              type="text"
              value={newTool}
              onChange={(e) => setNewTool(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddTool()}
              placeholder="e.g., Revit, AutoCAD, Photoshop"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            />
            <button
              onClick={handleAddTool}
              disabled={!newTool.trim()}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 transition"
            >
              <Plus className="w-4 h-4" />
              Add Tool
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              {tools.map((tool: string) => (
                <div
                  key={tool}
                  className="flex items-center justify-between bg-green-50 text-green-900 px-3 py-2 rounded-lg"
                >
                  <span className="text-sm font-medium">{tool}</span>
                  <button
                    onClick={() => removeToolMutation.mutate(tool)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Weights Configuration */}
      {activeTab === 'weights' && weights && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Default Scoring Weights</h2>
          <p className="text-sm text-gray-600 mb-6">
            These weights are used as defaults when creating new job descriptions. Total must equal 100%.
          </p>

          {!editWeights ? (
            <div className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                {Object.entries(weights).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                    <span className="font-medium text-gray-700 capitalize">
                      {key.replace('_weight', '').replace('_', ' ')}
                    </span>
                    <span className="text-2xl font-bold text-blue-600">{value}%</span>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setEditWeights(weights)}
                className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition"
              >
                Edit Weights
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {Object.entries(editWeights).map(([key, value]) => (
                <div key={key} className="flex items-center gap-4">
                  <label className="flex-1 font-medium text-gray-700 capitalize">
                    {key.replace('_weight', '').replace('_', ' ')}
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={value as number}
                    onChange={(e) =>
                      setEditWeights({ ...editWeights, [key]: parseInt(e.target.value) || 0 })
                    }
                    className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-center text-gray-900"
                  />
                  <span className="text-gray-600">%</span>
                </div>
              ))}
              <div className="flex items-center justify-between p-4 bg-gray-100 rounded-lg font-bold">
                <span>Total</span>
                <span
                  className={
                    Object.values(editWeights).reduce((a, b) => (a as number) + (b as number), 0) === 100
                      ? 'text-green-600'
                      : 'text-red-600'
                  }
                >
                  {Object.values(editWeights).reduce((a, b) => (a as number) + (b as number), 0) as number}%
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() =>
                    Object.values(editWeights).reduce((a: any, b: any) => a + b, 0) === 100 &&
                    updateWeightsMutation.mutate(editWeights)
                  }
                  disabled={Object.values(editWeights).reduce((a: any, b: any) => a + b, 0) !== 100}
                  className="flex-1 inline-flex items-center justify-center gap-2 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-300 transition"
                >
                  <Save className="w-5 h-5" />
                  Save Changes
                </button>
                <button
                  onClick={() => setEditWeights(null)}
                  className="flex-1 bg-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-400 transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
