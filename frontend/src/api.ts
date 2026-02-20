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

// ── Phase 1: Concept Intelligence ──

export async function analyzePhase1(payload: {
    scriptText: string;
    genre?: string;
    theme?: string;
    scale?: string;
}) {
    return request<any>('/phase1/analyze', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export async function confirmPhase1(payload: {
    title: string;
    genre: string;
    language: string;
    theme: string;
    scale: string;
    conceptRisk: string;
    targetAudience: string;
    goDecision: string;
}) {
    return request<any>('/phase1/confirm', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

// ── Phase 2: Packaging & Feasibility ──

export async function analyzeFeasibility(projectId: ProjectId, payload: {
    budgetLevel: string;
    talentStrategy: string;
}) {
    return request<any>(`/phase2/feasibility/${projectId}`, {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export async function analyzePackaging(projectId: ProjectId, payload: {
    budgetLevel: string;
    talentStrategy: string;
}) {
    return request<any>(`/phase2/packaging/${projectId}`, {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export async function confirmPhase2(projectId: ProjectId, payload: {
    budgetLevel: string;
    talentStrategy: string;
}) {
    return request<any>(`/phase2/confirm/${projectId}`, {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

// ── Phase 3: Production Intelligence ──

export async function analyzePhase3(payload: {
    projectId?: number;
    plannedShootDays: number;
    daysPerWeek: number;
    hoursPerDay: number;
    crewSize: number;
    complexityLevel: number;
    currentProgressPercent: number;
    actualShootDays?: number | null;
}) {
    return request<any>('/phase3/analyze', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export async function confirmPhase3(projectId: ProjectId, payload: {
    plannedShootDays: number;
    actualShootDays?: number | null;
    productionHealth: string;
}) {
    return request<any>(`/phase3/confirm/${projectId}`, {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}
