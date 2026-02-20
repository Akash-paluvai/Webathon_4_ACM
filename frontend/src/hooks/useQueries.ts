import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useActor } from './useActor';
import type { FilmProject, ProjectId, Scale, TalentStrategy, AudienceType, MarketingBudgetLevel, PrimaryMarketingChannel, ReleaseModel, DistributionConfidence } from '@/backend';
import type { BudgetLevel } from '@/lib/types';

/**
 * React Query Hooks for Backend Integration
 * 
 * ARCHITECTURE NOTE:
 * - All backend operations go through these hooks
 * - Frontend NEVER accesses Internet Computer storage directly
 * - All data operations use the Motoko backend actor
 * - These hooks manage data invalidation and caching
 * 
 * DO NOT:
 * - Add database access logic here
 * - Create mock data or placeholder APIs
 * - Mix business logic with data fetching
 */

// Get all film projects
export function useGetAllProjects() {
  const { actor, isFetching } = useActor();

  return useQuery<FilmProject[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      if (!actor) return [];
      return actor.getAllFilmProjects();
    },
    enabled: !!actor && !isFetching,
  });
}

// Get single film project
export function useGetProject(projectId: ProjectId) {
  const { actor, isFetching } = useActor();

  return useQuery<FilmProject | null>({
    queryKey: ['project', projectId.toString()],
    queryFn: async () => {
      if (!actor) return null;
      return actor.getFilmProject(projectId);
    },
    enabled: !!actor && !isFetching && !!projectId,
  });
}

// Create new film project
export function useCreateProject() {
  const { actor } = useActor();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      title: string;
      genre: string;
      language: string;
      theme: string;
      scale: Scale;
      budgetLevel: BudgetLevel;
      talentStrategy: TalentStrategy;
      plannedShootDays: bigint;
      audienceType: AudienceType;
      marketingBudgetLevel: MarketingBudgetLevel;
      primaryMarketingChannel: PrimaryMarketingChannel;
      releaseModel: ReleaseModel;
      distributionConfidence: DistributionConfidence;
    }) => {
      if (!actor) throw new Error('Actor not initialized');
      
      return actor.createFilmProject(
        data.title,
        data.genre,
        data.language,
        data.theme,
        data.scale,
        data.budgetLevel as any,
        data.talentStrategy,
        data.plannedShootDays,
        data.audienceType,
        data.marketingBudgetLevel,
        data.primaryMarketingChannel,
        data.releaseModel,
        data.distributionConfidence
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

// Update film project phase
export function useUpdateProjectPhase() {
  const { actor } = useActor();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { projectId: ProjectId; newPhase: bigint }) => {
      if (!actor) throw new Error('Actor not initialized');
      return actor.updateFilmProjectPhase(data.projectId, data.newPhase);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId.toString()] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

// Add project insight
export function useAddProjectInsight() {
  const { actor } = useActor();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { projectId: ProjectId; content: string }) => {
      if (!actor) throw new Error('Actor not initialized');
      return actor.addProjectInsight(data.projectId, data.content);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId.toString()] });
      queryClient.invalidateQueries({ queryKey: ['insights', variables.projectId.toString()] });
    },
  });
}

// Get project insights
export function useGetProjectInsights(projectId: ProjectId) {
  const { actor, isFetching } = useActor();

  return useQuery({
    queryKey: ['insights', projectId.toString()],
    queryFn: async () => {
      if (!actor) return [];
      return actor.getProjectInsights(projectId);
    },
    enabled: !!actor && !isFetching && !!projectId,
  });
}
