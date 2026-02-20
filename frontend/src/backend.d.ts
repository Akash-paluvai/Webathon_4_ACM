import type { Principal } from "@icp-sdk/core/principal";
export interface Some<T> {
    __kind__: "Some";
    value: T;
}
export interface None {
    __kind__: "None";
}
export type Option<T> = Some<T> | None;
export interface Insight {
    content: string;
    timestamp: bigint;
}
export interface FilmProject {
    id: ProjectId;
    currentPhase: bigint;
    distributionConfidence: DistributionConfidence;
    theme: string;
    title: string;
    marketingBudgetLevel: MarketingBudgetLevel;
    primaryMarketingChannel: PrimaryMarketingChannel;
    lastUpdated: bigint;
    actualShootDays?: bigint;
    budgetLevel: BudgetLevel;
    scale: Scale;
    language: string;
    productionHealth: ProductionHealth;
    talentStrategy: TalentStrategy;
    genre: string;
    releaseModel: ReleaseModel;
    audienceType: AudienceType;
    plannedShootDays: bigint;
}
export type ProjectId = bigint;
export enum AudienceType {
    mainstream = "mainstream",
    niche = "niche",
    broad = "broad"
}
export enum DistributionConfidence {
    low = "low",
    high = "high",
    medium = "medium"
}
export enum MarketingBudgetLevel {
    low = "low",
    high = "high",
    unassigned = "unassigned",
    medium = "medium"
}
export enum PrimaryMarketingChannel {
    pr = "pr",
    influencer = "influencer",
    digitalAds = "digitalAds",
    festival = "festival",
    undefined_ = "undefined"
}
export enum ProductionHealth {
    good = "good",
    critical = "critical",
    atRisk = "atRisk"
}
export enum ReleaseModel {
    ott = "ott",
    hybrid = "hybrid",
    theatre = "theatre"
}
export enum Scale {
    studio = "studio",
    blockbuster = "blockbuster",
    indie = "indie"
}
export enum TalentStrategy {
    starDriven = "starDriven",
    established = "established",
    emerging = "emerging",
    unknown_ = "unknown"
}
export interface backendInterface {
    addProjectInsight(projectId: ProjectId, content: string): Promise<void>;
    createFilmProject(title: string, genre: string, language: string, theme: string, scale: Scale, budgetLevel: BudgetLevel, talentStrategy: TalentStrategy, plannedShootDays: bigint, audienceType: AudienceType, marketingBudgetLevel: MarketingBudgetLevel, primaryMarketingChannel: PrimaryMarketingChannel, releaseModel: ReleaseModel, distributionConfidence: DistributionConfidence): Promise<ProjectId>;
    didRuntimeTrap(): Promise<boolean>;
    getAllFilmProjects(): Promise<Array<FilmProject>>;
    getFilmProject(projectId: ProjectId): Promise<FilmProject | null>;
    getFilmProjectWithInsights(projectId: ProjectId): Promise<[FilmProject, Array<Insight>]>;
    getMaxProjectId(): Promise<bigint>;
    getProjectInsights(projectId: ProjectId): Promise<Array<Insight>>;
    getProjectTitlesStartingWith(letter: string): Promise<Array<string>>;
    updateFilmProject(projectId: ProjectId, title: string, phase: bigint, genre: string, language: string, theme: string, scale: Scale, budgetLevel: BudgetLevel, talentStrategy: TalentStrategy, plannedShootDays: bigint, actualShootDays: bigint, productionHealth: ProductionHealth, audienceType: AudienceType, marketingBudgetLevel: MarketingBudgetLevel, primaryMarketingChannel: PrimaryMarketingChannel, releaseModel: ReleaseModel, distributionConfidence: DistributionConfidence): Promise<void>;
    updateFilmProjectPhase(projectId: ProjectId, newPhase: bigint): Promise<void>;
}
