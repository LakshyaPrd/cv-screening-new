/**
 * API client for CV Screening Platform
 * Provides type-safe methods for all backend endpoints
 */
import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface BatchResponse {
  batch_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  total_files: number;
  processed_files: number;
  failed_files: number;
  progress_percentage: number;
  description?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface CandidateResponse {
  candidate_id: string;
  batch_id: string;
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  skills?: string[];
  tools?: string[];
  education?: any[];
  experience?: any[];
  portfolio_urls?: string[];
  ocr_quality_score?: number;
  extraction_status: string;
  cv_file_path?: string;
  created_at: string;
}

export interface JobDescriptionCreate {
  title: string;
  description: string;
  must_have_skills: string[];
  nice_to_have_skills?: string[];
  required_tools?: string[];
  role_keywords?: string[];
  location_preference?: string;
  skill_weight?: number;
  role_weight?: number;
  tool_weight?: number;
  experience_weight?: number;
  portfolio_weight?: number;
  quality_weight?: number;
  minimum_score_threshold?: number;
}

export interface JobDescriptionResponse extends JobDescriptionCreate {
  jd_id: string;
  created_at: string;
  updated_at: string;
  is_active: number;
}

export interface MatchResultResponse {
  match_id: string;
  candidate_id: string;
  jd_id: string;
  total_score: number;
  skill_score: number;
  role_score: number;
  tool_score: number;
  experience_score: number;
  portfolio_score: number;
  quality_score: number;
  justification: string;
  matched_skills?: string[];
  missing_skills?: string[];
  matched_tools?: string[];
  is_shortlisted: boolean;
  is_rejected: boolean;
  created_at: string;
  candidate_name?: string;
  candidate_email?: string;
  candidate_phone?: string;
}

// API Functions
export const api = {
  // Upload
  uploadBatch: async (files: File[], description?: string) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    if (description) {
      formData.append('description', description);
    }

    const response = await apiClient.post<BatchResponse>('/upload/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Batches
  getBatch: async (batchId: string) => {
    const response = await apiClient.get<BatchResponse>(`/batch/${batchId}`);
    return response.data;
  },

  listBatches: async (skip = 0, limit = 20) => {
    const response = await apiClient.get<{ batches: BatchResponse[]; total: number }>(
      `/batches?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  getBatchCandidates: async (batchId: string, skip = 0, limit = 20) => {
    const response = await apiClient.get<{ candidates: CandidateResponse[]; total: number }>(
      `/batch/${batchId}/candidates?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Job Descriptions
  createJobDescription: async (jd: JobDescriptionCreate) => {
    const response = await apiClient.post<JobDescriptionResponse>('/jd', jd);
    return response.data;
  },

  getJobDescription: async (jdId: string) => {
    const response = await apiClient.get<JobDescriptionResponse>(`/jd/${jdId}`);
    return response.data;
  },

  listJobDescriptions: async (skip = 0, limit = 20) => {
    const response = await apiClient.get<{ job_descriptions: JobDescriptionResponse[]; total: number }>(
      `/jds?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Matching
  matchCandidates: async (jdId: string, batchId?: string) => {
    const response = await apiClient.post(`/jd/${jdId}/match`, { batch_id: batchId });
    return response.data;
  },

  getMatches: async (
    jdId: string,
    params: {
      min_score?: number;
      is_shortlisted?: boolean;
      page?: number;
      page_size?: number;
    } = {}
  ) => {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, value.toString());
      }
    });

    const response = await apiClient.get<{
      matches: MatchResultResponse[];
      total: number;
      total_pages: number;
      current_page: number;
    }>(`/jd/${jdId}/matches?${queryParams}`);
    return response.data;
  },

  shortlistCandidates: async (jdId: string, matchIds: string[]) => {
    const response = await apiClient.post(`/jd/${jdId}/shortlist`, { match_ids: matchIds });
    return response.data;
  },

  rejectCandidates: async (jdId: string, matchIds: string[]) => {
    const response = await apiClient.post(`/jd/${jdId}/reject`, { match_ids: matchIds });
    return response.data;
  },

  // Admin
  getDictionary: async (type: 'skills' | 'tools') => {
    const response = await apiClient.get<{ [key: string]: string[] }>(`/admin/${type}`);
    return response.data[type] || [];
  },

  updateDictionary: async (type: 'skills' | 'tools', items: string[]) => {
    const response = await apiClient.put(`/admin/${type}`, { [type]: items });
    return response.data;
  },

  getDefaultWeights: async () => {
    const response = await apiClient.get<{
      skill_weight: number;
      role_weight: number;
      tool_weight: number;
      experience_weight: number;
      portfolio_weight: number;
      quality_weight: number;
    }>('/admin/scoring-weights');
    return response.data;
  },

  updateDefaultWeights: async (weights: any) => {
    const response = await apiClient.put('/admin/scoring-weights', weights);
    return response.data;
  },

  getSystemHealth: async () => {
    const response = await apiClient.get<{
      total_batches: number;
      total_candidates: number;
      total_matches: number;
      ocr_config: any;
    }>('/admin/system-health');
    return response.data;
  },
};

export default api;
