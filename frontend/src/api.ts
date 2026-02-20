// REST API client for the Python FastAPI backend
import type {
    FilmProject,
    Insight,
    FilmProjectWithInsights,
    ProjectId,
    Scale,
    BudgetLevel,
    TalentStrategy,
    AudienceType,
    MarketingBudgetLevel,
    PrimaryMarketingChannel,
    ReleaseModel,
    DistributionConfidence,
    ProductionHealth,
} from './types';

const API_BASE = '/api';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${url}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
}

// ── Film Project API ──

export async function getAllProjects(): Promise<FilmProject[]> {
    return request<FilmProject[]>('/projects');
}

export async function getProject(projectId: ProjectId): Promise<FilmProject> {
    return request<FilmProject>(`/projects/${projectId}`);
}

export async function createProject(data: {
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
}): Promise<FilmProject> {
    return request<FilmProject>('/projects', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function updateProject(
    projectId: ProjectId,
    data: {
        title: string;
        phase: number;
        genre: string;
        language: string;
        theme: string;
        scale: Scale;
        budgetLevel: BudgetLevel;
        talentStrategy: TalentStrategy;
        plannedShootDays: number;
        actualShootDays?: number | null;
        productionHealth: ProductionHealth;
        audienceType: AudienceType;
        marketingBudgetLevel: MarketingBudgetLevel;
        primaryMarketingChannel: PrimaryMarketingChannel;
        releaseModel: ReleaseModel;
        distributionConfidence: DistributionConfidence;
    }
): Promise<FilmProject> {
    return request<FilmProject>(`/projects/${projectId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

export async function updateProjectPhase(
    projectId: ProjectId,
    newPhase: number
): Promise<FilmProject> {
    return request<FilmProject>(`/projects/${projectId}/phase`, {
        method: 'PATCH',
        body: JSON.stringify({ newPhase }),
    });
}

// ── Insight API ──

export async function getProjectInsights(projectId: ProjectId): Promise<Insight[]> {
    return request<Insight[]>(`/projects/${projectId}/insights`);
}

export async function addProjectInsight(
    projectId: ProjectId,
    content: string
): Promise<Insight> {
    return request<Insight>(`/projects/${projectId}/insights`, {
        method: 'POST',
        body: JSON.stringify({ content }),
    });
}

export async function getProjectWithInsights(
    projectId: ProjectId
): Promise<FilmProjectWithInsights> {
    return request<FilmProjectWithInsights>(`/projects/${projectId}/with-insights`);
}
