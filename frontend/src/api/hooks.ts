// TanStack Query hooks for ScholarPilot AI API endpoints

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest, storeToken } from './client';
import type {
  StudentProfile,
  ProfileCreateResponse,
  DocumentOut,
  JobOut,
  EventsResponse,
  ResultsOut,
  DraftOut,
} from '../types/api';

// 1. Profile registration and retrieval
export function useCreateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (profile: Partial<StudentProfile>) => {
      const res = await apiRequest<ProfileCreateResponse>('/api/v1/profiles', {
        method: 'POST',
        body: JSON.stringify(profile),
      });
      storeToken(res.id, res.access_token);
      return res;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['profile', data.id], data.profile);
    },
  });
}

export function useProfile(profileId?: string) {
  return useQuery({
    queryKey: ['profile', profileId],
    queryFn: () => apiRequest<{ id: string; profile: StudentProfile }>(`/api/v1/profiles/${profileId}`, {}, profileId),
    enabled: Boolean(profileId),
  });
}

// 2. Document upload
export function useUploadDocument(profileId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ kind, file }: { kind: string; file: File }) => {
      if (!profileId) throw new Error('Profile ID required to upload document');
      const formData = new FormData();
      formData.append('kind', kind);
      formData.append('file', file);
      return apiRequest<DocumentOut>(`/api/v1/profiles/${profileId}/documents`, {
        method: 'POST',
        body: formData,
      }, profileId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', profileId] });
    },
  });
}

// 3. Research job management
export function useStartResearchJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      profileId,
      countries,
      maxCandidates,
    }: {
      profileId: string;
      countries?: string[];
      maxCandidates?: number;
    }) => {
      return apiRequest<JobOut>('/api/v1/research-jobs', {
        method: 'POST',
        body: JSON.stringify({
          profile_id: profileId,
          countries,
          max_candidates: maxCandidates,
        }),
      }, profileId);
    },
    onSuccess: (job) => {
      queryClient.setQueryData(['job', job.id], job);
    },
  });
}

export function useJob(jobId?: string) {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => apiRequest<JobOut>(`/api/v1/research-jobs/${jobId}`),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'queued' || status === 'running') {
        return 1500;
      }
      return false;
    },
  });
}

export function useJobEvents(jobId?: string, isLive: boolean = true) {
  return useQuery({
    queryKey: ['events', jobId],
    queryFn: () => apiRequest<EventsResponse>(`/api/v1/research-jobs/${jobId}/events?limit=300`),
    enabled: Boolean(jobId),
    refetchInterval: isLive ? 1500 : false,
  });
}

export function useJobResults(jobId?: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['results', jobId],
    queryFn: () => apiRequest<ResultsOut>(`/api/v1/research-jobs/${jobId}/results`),
    enabled: Boolean(jobId) && enabled,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCancelJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (jobId: string) => {
      return apiRequest<JobOut>(`/api/v1/research-jobs/${jobId}/cancel`, {
        method: 'POST',
      });
    },
    onSuccess: (job) => {
      queryClient.setQueryData(['job', job.id], job);
      queryClient.invalidateQueries({ queryKey: ['events', job.id] });
    },
  });
}

export function useRetryJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (jobId: string) => {
      return apiRequest<JobOut>(`/api/v1/research-jobs/${jobId}/retry`, {
        method: 'POST',
      });
    },
    onSuccess: (job) => {
      queryClient.setQueryData(['job', job.id], job);
      queryClient.invalidateQueries({ queryKey: ['events', job.id] });
      queryClient.invalidateQueries({ queryKey: ['results', job.id] });
    },
  });
}

// 4. Drafts (Statement of Purpose generation)
export function useGenerateDraft() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      jobId,
      opportunityId,
      tone,
    }: {
      jobId: string;
      opportunityId: string;
      tone?: string;
    }) => {
      return apiRequest<DraftOut>(`/api/v1/research-jobs/${jobId}/drafts`, {
        method: 'POST',
        body: JSON.stringify({
          opportunity_id: opportunityId,
          tone: tone || 'academic',
        }),
      });
    },
    onSuccess: (draft) => {
      queryClient.setQueryData(['draft', draft.job_id, draft.id], draft);
    },
  });
}

export function useDraft(jobId?: string, draftId?: string) {
  return useQuery({
    queryKey: ['draft', jobId, draftId],
    queryFn: () => apiRequest<DraftOut>(`/api/v1/research-jobs/${jobId}/drafts/${draftId}`),
    enabled: Boolean(jobId && draftId),
  });
}
