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
    trailerFeatures: Record<string, any>;
    enhancedSignals?: {
        violenceLikelihood: string;
        emotionalTone: string;
        genreInclination: string;
        behavioralDynamics: string;
        intensityScore: number;
    };
    enhancedAnalysisAvailable: boolean;
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

export interface AIInsights {
    marketRead: string;
    riskSignals: string;
    strategicRecommendations: string;
    enhancedAnalysisAvailable?: boolean;
    enhancedSignals?: Phase4Result['enhancedSignals'];
}

export async function generatePhase4Insights(
    projectId: ProjectId,
    data: {
        audienceType: string;
        audienceInterestScore: number;
        testStrategy: string;
        trailerFeatures: Record<string, unknown>;
    }
): Promise<AIInsights> {
    return request<AIInsights>(`/projects/${projectId}/phase/4/insights`, {
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
    decisionRationale: {
        audience: string;
        budget: string;
        channelReason: string;
        riskReason: string;
        interestContext: string;
        primaryAllocation: string;
    };
}

export interface ScenarioResult {
    discoverability: number;
    delta: number;
    primaryChannel: string;
    budgetAllocation: Record<string, number>;
    marketingRisk: string;
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

export async function simulateScenario(
    projectId: ProjectId,
    baselineMarketingBudgetLevel: string,
    audienceType?: string,
    marketingBudgetLevel?: string,
): Promise<{ scenarioResult: ScenarioResult }> {
    return request<{ scenarioResult: ScenarioResult }>(`/projects/${projectId}/phase/5/scenario`, {
        method: 'POST',
        body: JSON.stringify({
            baselineMarketingBudgetLevel,
            audienceType: audienceType || undefined,
            marketingBudgetLevel: marketingBudgetLevel || undefined,
        }),
    });
}

// ── High-Reach YouTube Channels API ──

export interface TrendingCreator {
    name: string;
    platform: string;
    logoUrl: string;
    subscribers: number;
    reachTier: string;
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

// ── Phase 6 Analysis API ──

export async function getPhase6Analysis(projectId: ProjectId): Promise<any> {
    const res = await fetch(`/phase6/analyze?project_id=${projectId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
}

// ── Phase 7 Release & Discoverability API ──

export async function getPhase7Timeline(projectId: ProjectId): Promise<any> {
    const res = await fetch(`/phase7/timeline/${projectId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
}

export async function getPhase7Demand(projectId: ProjectId): Promise<any> {
    const res = await fetch(`/phase7/demand/${projectId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
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

// ── Assistant API ──

export async function chatWithAssistant(payload: {
    message: string;
    phase?: string | null;
    history?: { role: string; content: string }[];
    projectId?: number;
}): Promise<{ text: string }> {
    return request<{ text: string }>('/assistant/chat', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}
// ── Phase 8: Post-Release Tracking ──

export interface Phase8Report {
    movie: {
        title: string;
        tmdb_id: number;
        release_date?: string;
        genre?: string;
        budget?: number;
        revenue?: number;
    };
    generated_at: string;
    sections: Record<string, {
        value: any;
        source_type: string;
        source_name: string;
        confidence: number;
        methodology?: string;
    }>;
    comparables_used: any[];
    diagnostics?: any;
    insights?: any;
}

export async function getPhase8Report(movieTitle: string): Promise<Phase8Report> {
    return request<Phase8Report>(`/phase8/report/${encodeURIComponent(movieTitle)}`);
}

export async function updatePhase8Results(
    projectId: ProjectId,
    data: {
        audienceResponse: string;
        monetizationOptions: string;
        learningSummary: string;
        currentPhase: number;
    }
): Promise<FilmProject> {
    // We use the general update project endpoint but we'll adapt it if needed
    // For Phase 8 specific save, we might need a dedicated endpoint or partial update
    return request<FilmProject>(`/projects/${projectId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}
