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

// ── Phase 4 API ──

export interface Phase4Result {
    projectId: number;
    testStrategy: string;
    audienceType: string;
    audienceInterestScore: number;
    trailerFeatures: Record<string, unknown>;
}

export async function submitPhase4(
    projectId: ProjectId,
    trailerFile: File,
    testStrategy: string
): Promise<Phase4Result> {
    const form = new FormData();
    form.append('trailer_video', trailerFile);
    form.append('testStrategy', testStrategy);

    const res = await fetch(`${API_BASE}/projects/${projectId}/phase/4`, {
        method: 'POST',
        body: form,
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
}

export async function generatePhase4Insights(
    projectId: ProjectId,
    data: {
        audienceType: string;
        audienceInterestScore: number;
        testStrategy: string;
        trailerFeatures: Record<string, unknown>;
    }
): Promise<{ insights: string[] }> {
    return request<{ insights: string[] }>(`/projects/${projectId}/phase/4/insights`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ── Phase 5 API ──

export interface Phase5Result {
    projectId: number;
    marketingBudgetLevel: string;
    primaryMarketingChannel: string;
    budgetAllocation: Record<string, number>;
    discoverabilityScore: number;
    marketingRisk: string;
    riskFlags: string[];
    explanation: string;
    alternativeScenarios: {
        name: string;
        budgetAllocation: Record<string, number>;
        discoverabilityScore: number;
        risk: string;
    }[];
    diminishingReturnsInsight: string;
    riskDecomposition: {
        budgetRisk: string;
        audienceFitRisk: string;
        channelConcentrationRisk: string;
    };
    channelDeprioritization: string;
}

export async function submitPhase5(
    projectId: ProjectId,
    marketingBudgetLevel: string
): Promise<Phase5Result> {
    return request<Phase5Result>(`/projects/${projectId}/phase/5`, {
        method: 'POST',
        body: JSON.stringify({ marketingBudgetLevel }),
    });
}

// ── Trending Creators API ──

export interface TrendingCreator {
    name: string;
    platform: string;
    thumbnailUrl: string;
    activityScore: number;
    category: string;
    reason: string;
}

export async function fetchTrendingCreators(
    genre?: string,
    region?: string
): Promise<{ creators: TrendingCreator[] }> {
    const params = new URLSearchParams();
    if (genre) params.set('genre', genre);
    if (region) params.set('region', region);
    const qs = params.toString();
    return request<{ creators: TrendingCreator[] }>(
        `/marketing/trending-creators${qs ? `?${qs}` : ''}`
    );
}
