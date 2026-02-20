import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from '../api';
import type {
  FilmProject,
  ProjectId,
  Scale,
  BudgetLevel,
  TalentStrategy,
  AudienceType,
  MarketingBudgetLevel,
  PrimaryMarketingChannel,
  ReleaseModel,
  DistributionConfidence,
} from '../types';

/**
 * React Query Hooks for Backend Integration
 *
 * All backend operations go through these hooks using the REST API client.
 */

// Get all film projects
export function useGetAllProjects() {
  return useQuery<FilmProject[]>({
    queryKey: ['projects'],
    queryFn: () => api.getAllProjects(),
  });
}

// Get single film project
export function useGetProject(projectId: ProjectId) {
  return useQuery<FilmProject | null>({
    queryKey: ['project', String(projectId)],
    queryFn: () => api.getProject(projectId),
    enabled: !!projectId,
  });
}

// Create new film project
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      title: string;
      genre: string;
      language: string;
      theme: string;
      scale: Scale;
      budgetLevel: BudgetLevel;
      talentStrategy: TalentStrategy;
      plannedShootDays: number;
      audienceType: AudienceType;
      marketingBudgetLevel: MarketingBudgetLevel;
      primaryMarketingChannel: PrimaryMarketingChannel;
      releaseModel: ReleaseModel;
      distributionConfidence: DistributionConfidence;
    }) => api.createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

// Update film project phase
export function useUpdateProjectPhase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { projectId: ProjectId; newPhase: number }) =>
      api.updateProjectPhase(data.projectId, data.newPhase),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', String(variables.projectId)] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

// Add project insight
export function useAddProjectInsight() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { projectId: ProjectId; content: string }) =>
      api.addProjectInsight(data.projectId, data.content),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', String(variables.projectId)] });
      queryClient.invalidateQueries({ queryKey: ['insights', String(variables.projectId)] });
    },
  });
}

// Get project insights
export function useGetProjectInsights(projectId: ProjectId) {
  return useQuery({
    queryKey: ['insights', String(projectId)],
    queryFn: () => api.getProjectInsights(projectId),
    enabled: !!projectId,
  });
}
