// Shared TypeScript types for Film Producer Decision Support Platform
// These replace the ICP Candid-generated types

export type ProjectId = number;

export enum Scale {
    indie = "indie",
    studio = "studio",
    blockbuster = "blockbuster",
}

export enum BudgetLevel {
    low = "low",
    medium = "medium",
    high = "high",
}

export enum TalentStrategy {
    unknown = "unknown",
    emerging = "emerging",
    established = "established",
    starDriven = "starDriven",
}

export enum ProductionHealth {
    good = "good",
    atRisk = "atRisk",
    critical = "critical",
}

export enum AudienceType {
    niche = "niche",
    broad = "broad",
    mainstream = "mainstream",
}

export enum MarketingBudgetLevel {
    low = "low",
    medium = "medium",
    high = "high",
    unassigned = "unassigned",
}

export enum PrimaryMarketingChannel {
    influencer = "influencer",
    festival = "festival",
    digitalAds = "digitalAds",
    pr = "pr",
    undefined = "undefined",
}

export enum ReleaseModel {
    theatre = "theatre",
    ott = "ott",
    hybrid = "hybrid",
}

export enum DistributionConfidence {
    low = "low",
    medium = "medium",
    high = "high",
}

export interface FilmProject {
    id: ProjectId;
    title: string;
    currentPhase: number;
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
    audienceResponse?: string;
    monetizationOptions?: string;
    learningSummary?: string;
    lastUpdated: string;
}

export interface Insight {
    id: number;
    content: string;
    timestamp: string;
}

export interface FilmProjectWithInsights {
    project: FilmProject;
    insights: Insight[];
}
