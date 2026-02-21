/**
 * PHASE 5 — Marketing Strategy Planning
 *
 * Two-column layout:
 *   LEFT:  Campaign config, optimized plan, comparative scenarios,
 *          strategic insights, risk flags
 *   RIGHT: Prominent Public Figures sidebar
 *
 * Persists: marketingBudgetLevel, primaryMarketingChannel
 * Response-only: budgetAllocation, discoverabilityScore, marketingRisk,
 *   riskFlags, explanation, alternativeScenarios, diminishingReturnsInsight,
 *   riskDecomposition, channelDeprioritization
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  ArrowLeft, Megaphone, BarChart3, AlertTriangle, Loader2,
  ShieldAlert, TrendingUp, Info, Lightbulb, Users,
  ChevronDown, ChevronUp, FlaskConical, ArrowUpRight, ArrowDownRight,
} from 'lucide-react';
import { submitPhase5, fetchTrendingCreators, simulateScenario, updateProjectPhase } from '@/api';
import { ArrowRight } from 'lucide-react';
import type { Phase5Result, TrendingCreator, ScenarioResult } from '@/api';

export default function Phase5Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };

  const [budgetLevel, setBudgetLevel] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<Phase5Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [creators, setCreators] = useState<TrendingCreator[]>([]);
  const [creatorsLoading, setCreatorsLoading] = useState(false);

  // Rationale panel
  const [rationaleOpen, setRationaleOpen] = useState(false);

  // What-if scenario
  const [scenarioAudience, setScenarioAudience] = useState<string>('');
  const [scenarioBudget, setScenarioBudget] = useState<string>('');
  const [scenarioResult, setScenarioResult] = useState<ScenarioResult | null>(null);
  const [scenarioRunning, setScenarioRunning] = useState(false);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (!result) return;
    setCreatorsLoading(true);
    fetchTrendingCreators()
      .then((res) => setCreators(res.creators))
      .catch(() => setCreators([]))
      .finally(() => setCreatorsLoading(false));
  }, [result]);

  const handleSubmit = async () => {
    if (!budgetLevel) return;
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const res = await submitPhase5(Number(projectId), budgetLevel);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to generate marketing plan');
    } finally {
      setSubmitting(false);
    }
  };

  const handleScenario = async () => {
    if (!result) return;
    setScenarioRunning(true);
    setScenarioResult(null);
    try {
      const res = await simulateScenario(
        Number(projectId),
        result.marketingBudgetLevel,
        scenarioAudience || undefined,
        scenarioBudget || undefined,
      );
      setScenarioResult(res.scenarioResult);
    } catch {
      // silently fail
    } finally {
      setScenarioRunning(false);
    }
  };

  const handleConfirmAndAdvance = async () => {
    setConfirming(true);
    try {
      await updateProjectPhase(Number(projectId), 6);
      navigate({ to: '/projects/$projectId', params: { projectId } });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to advance phase');
    } finally {
      setConfirming(false);
    }
  };

  const riskBadgeVariant = (risk: string) => {
    switch (risk.toUpperCase()) {
      case 'HIGH': return 'destructive' as const;
      case 'MEDIUM': return 'secondary' as const;
      case 'LOW': return 'default' as const;
      default: return 'outline' as const;
    }
  };

  const scoreColor = (score: number) => {
    if (score >= 70) return 'text-green-500';
    if (score >= 45) return 'text-yellow-500';
    return 'text-red-500';
  };

  const channelLabel = (ch: string) => {
    switch (ch) {
      case 'ADS': return 'Digital Ads';
      case 'INFLUENCER': return 'Influencer';
      case 'FESTIVAL': return 'Festival Circuit';
      case 'ORGANIC': return 'Organic / PR';
      default: return ch;
    }
  };

  const channelColor = (ch: string) => {
    switch (ch) {
      case 'ADS': return 'bg-blue-500';
      case 'INFLUENCER': return 'bg-purple-500';
      case 'FESTIVAL': return 'bg-amber-500';
      case 'ORGANIC': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const categoryVariant = (cat: string) => {
    switch (cat) {
      case 'Actor': return 'default' as const;
      case 'Musician': return 'secondary' as const;
      case 'Motivational Figure': return 'outline' as const;
      default: return 'outline' as const;
    }
  };

  /* ─── Right sidebar content ─── */
  const renderSidebar = () => (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Users className="h-4 w-4" />
            High-Reach YouTube Channels (Discovery Signals)
          </CardTitle>
          <CardDescription className="text-xs">
            Channels identified using public reach metrics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {creatorsLoading ? (
            <div className="flex items-center justify-center py-6 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              <span className="text-xs">Discovering channels…</span>
            </div>
          ) : creators.length === 0 ? (
            <p className="text-xs text-muted-foreground py-4 text-center">
              No channels meet the reach threshold at this time.
            </p>
          ) : (
            <>
              {creators.map((creator, idx) => (
                <div key={idx} className="flex items-start gap-3 p-2.5 border rounded-lg">
                  {/* Circular channel logo */}
                  <div className="shrink-0">
                    <img
                      src={creator.logoUrl}
                      alt={`${creator.name} channel logo`}
                      className="w-12 h-12 rounded-full object-cover border-2 border-border"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        if (target.parentElement) {
                          target.parentElement.classList.add('flex', 'items-center', 'justify-center', 'w-12', 'h-12', 'rounded-full', 'bg-muted', 'border-2', 'border-border');
                          const fallback = document.createElement('span');
                          fallback.textContent = creator.name.charAt(0);
                          fallback.className = 'text-lg font-bold text-muted-foreground';
                          target.parentElement.appendChild(fallback);
                        }
                      }}
                    />
                  </div>
                  {/* Channel info */}
                  <div className="flex-1 min-w-0 space-y-1">
                    <p className="font-medium text-sm leading-tight truncate">{creator.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {creator.subscribers >= 1_000_000
                        ? `${(creator.subscribers / 1_000_000).toFixed(1)}M subscribers`
                        : `${(creator.subscribers / 1_000).toFixed(0)}K subscribers`}
                    </p>
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <Badge variant="default" className="text-[10px] px-1.5 py-0">
                        {creator.reachTier}
                      </Badge>
                      <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                        YouTube
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
              <p className="text-[10px] text-muted-foreground text-center pt-2 leading-tight">
                Channels are identified using public reach metrics, not manual selection.
              </p>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <Button
        variant="ghost"
        onClick={() => navigate({ to: '/projects/$projectId', params: { projectId } })}
        className="mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Project Overview
      </Button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Phase 5: Marketing Strategy Planning</h1>
        <p className="text-muted-foreground text-lg">
          Simulate budget-constrained campaign allocation and discoverability
        </p>
      </div>

      {/* ─── Two-column layout when results exist ─── */}
      <div className={result ? 'grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6' : ''}>

        {/* ═══ LEFT COLUMN — primary content ═══ */}
        <div className="space-y-6">

          {/* Campaign Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Megaphone className="h-5 w-5" />
                Campaign Configuration
              </CardTitle>
              <CardDescription>
                Select a marketing budget level to generate an optimised channel allocation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="budget-level">Marketing Budget Level</Label>
                <Select value={budgetLevel} onValueChange={setBudgetLevel}>
                  <SelectTrigger id="budget-level">
                    <SelectValue placeholder="Select budget level…" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="LOW">Low Budget</SelectItem>
                    <SelectItem value="MEDIUM">Medium Budget</SelectItem>
                    <SelectItem value="HIGH">High Budget</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                className="w-full"
                disabled={!budgetLevel || submitting}
                onClick={handleSubmit}
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating Plan…
                  </>
                ) : (
                  <>
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Generate Marketing Plan
                  </>
                )}
              </Button>
              {error && (
                <div className="flex items-center gap-2 text-sm text-destructive mt-2">
                  <AlertTriangle className="h-4 w-4" />
                  {error}
                </div>
              )}
            </CardContent>
          </Card>

          {/* ─── Results ─── */}
          {result && (
            <>
              {/* Optimized Plan */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Optimized Plan
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Metrics Row */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="space-y-1">
                      <p className="text-sm text-muted-foreground">Primary Channel</p>
                      <Badge variant="default" className="text-sm">
                        {channelLabel(result.primaryMarketingChannel)}
                      </Badge>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-muted-foreground">Marketing Risk</p>
                      <Badge variant={riskBadgeVariant(result.marketingRisk)} className="text-sm">
                        {result.marketingRisk}
                      </Badge>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-muted-foreground">Discoverability</p>
                      <p className={`text-2xl font-bold ${scoreColor(result.discoverabilityScore)}`}>
                        {result.discoverabilityScore}
                        <span className="text-sm font-normal text-muted-foreground">/100</span>
                      </p>
                    </div>
                  </div>

                  {/* Discoverability Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Simulated Discoverability</span>
                      <span className={scoreColor(result.discoverabilityScore)}>
                        {result.discoverabilityScore}%
                      </span>
                    </div>
                    <Progress value={result.discoverabilityScore} className="h-2" />
                  </div>

                  <Separator />

                  {/* Budget Allocation */}
                  <div>
                    <p className="text-sm font-medium mb-3">Budget Allocation by Channel</p>
                    <div className="space-y-3">
                      {Object.entries(result.budgetAllocation)
                        .sort(([, a], [, b]) => b - a)
                        .map(([channel, pct]) => (
                          <div key={channel} className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span>{channelLabel(channel)}</span>
                              <span className="font-semibold">{pct}%</span>
                            </div>
                            <div className="w-full bg-muted rounded-full h-2.5">
                              <div
                                className={`h-2.5 rounded-full ${channelColor(channel)}`}
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>

                  <Separator />

                  {/* Risk Decomposition */}
                  <div>
                    <p className="text-sm font-medium mb-3">Risk Decomposition</p>
                    <div className="flex flex-wrap gap-3">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-muted-foreground">Budget</span>
                        <Badge variant={riskBadgeVariant(result.riskDecomposition.budgetRisk)} className="text-xs">
                          {result.riskDecomposition.budgetRisk}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-muted-foreground">Audience Fit</span>
                        <Badge variant={riskBadgeVariant(result.riskDecomposition.audienceFitRisk)} className="text-xs">
                          {result.riskDecomposition.audienceFitRisk}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-muted-foreground">Concentration</span>
                        <Badge variant={riskBadgeVariant(result.riskDecomposition.channelConcentrationRisk)} className="text-xs">
                          {result.riskDecomposition.channelConcentrationRisk}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Explanation */}
                  <div className="bg-muted/50 rounded-lg p-4">
                    <p className="text-sm leading-relaxed">{result.explanation}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Comparative Scenarios */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5" />
                    Comparative Scenarios
                  </CardTitle>
                  <CardDescription>
                    Budget-constrained trade-offs across alternative allocation strategies
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.alternativeScenarios.map((scenario) => (
                      <div key={scenario.name} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm">{scenario.name}</p>
                          <Badge variant={riskBadgeVariant(scenario.risk)} className="text-xs">
                            {scenario.risk} Risk
                          </Badge>
                        </div>
                        <div className="flex items-baseline gap-1">
                          <span className={`text-xl font-bold ${scoreColor(scenario.discoverabilityScore)}`}>
                            {scenario.discoverabilityScore}
                          </span>
                          <span className="text-xs text-muted-foreground">/100 discoverability</span>
                        </div>
                        <div className="space-y-1.5">
                          {Object.entries(scenario.budgetAllocation)
                            .sort(([, a], [, b]) => b - a)
                            .map(([ch, pct]) => (
                              <div key={ch} className="flex items-center gap-2 text-xs">
                                <div className={`w-2 h-2 rounded-full ${channelColor(ch)}`} />
                                <span className="text-muted-foreground flex-1">{channelLabel(ch)}</span>
                                <span className="font-medium">{pct}%</span>
                              </div>
                            ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Strategic Insights */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Info className="h-5 w-5" />
                    Strategic Insights
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-muted/50 rounded-lg p-4 space-y-1">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                      Marginal Efficiency
                    </p>
                    <p className="text-sm leading-relaxed">{result.diminishingReturnsInsight}</p>
                  </div>
                  <div className="bg-muted/50 rounded-lg p-4 space-y-1">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                      Channel Trade-Off
                    </p>
                    <p className="text-sm leading-relaxed">{result.channelDeprioritization}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Risk Flags */}
              {result.riskFlags.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ShieldAlert className="h-5 w-5" />
                      Risk Flags
                    </CardTitle>
                    <CardDescription>
                      Issues that may impact campaign effectiveness
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {result.riskFlags.map((flag, idx) => (
                        <li key={idx} className="flex gap-3 items-start">
                          <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{flag}</p>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* ── Why this decision? panel ── */}
              <Card>
                <CardHeader
                  className="cursor-pointer select-none"
                  onClick={() => setRationaleOpen(!rationaleOpen)}
                >
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-base">
                      <Info className="h-5 w-5" />
                      Why this marketing strategy?
                    </span>
                    {rationaleOpen ? (
                      <ChevronUp className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    )}
                  </CardTitle>
                </CardHeader>
                {rationaleOpen && (
                  <CardContent className="space-y-3 pt-0">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-muted/50 rounded-lg p-3">
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Audience</p>
                        <Badge variant="outline">{result.decisionRationale.audience}</Badge>
                      </div>
                      <div className="bg-muted/50 rounded-lg p-3">
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Budget</p>
                        <Badge variant="outline">{result.decisionRationale.budget}</Badge>
                      </div>
                    </div>
                    <div className="bg-muted/50 rounded-lg p-3 space-y-1">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Channel Selection</p>
                      <p className="text-sm">{result.decisionRationale.channelReason}</p>
                      <p className="text-xs text-muted-foreground">{result.decisionRationale.primaryAllocation}</p>
                    </div>
                    <div className="bg-muted/50 rounded-lg p-3 space-y-1">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Risk Assessment</p>
                      <p className="text-sm">{result.decisionRationale.riskReason}</p>
                    </div>
                    <div className="bg-muted/50 rounded-lg p-3 space-y-1">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Audience Interest</p>
                      <p className="text-sm">{result.decisionRationale.interestContext}</p>
                    </div>
                  </CardContent>
                )}
              </Card>

              {/* ── What if? scenario toggler ── */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <FlaskConical className="h-5 w-5" />
                    What If?
                  </CardTitle>
                  <CardDescription>
                    Override audience or budget to simulate an alternative scenario
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <Label className="text-xs">Audience Type</Label>
                      <Select value={scenarioAudience} onValueChange={setScenarioAudience}>
                        <SelectTrigger>
                          <SelectValue placeholder="Keep current" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="NICHE">Niche</SelectItem>
                          <SelectItem value="REGIONAL">Regional</SelectItem>
                          <SelectItem value="MASS">Mass</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1.5">
                      <Label className="text-xs">Budget Level</Label>
                      <Select value={scenarioBudget} onValueChange={setScenarioBudget}>
                        <SelectTrigger>
                          <SelectValue placeholder="Keep current" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="LOW">Low</SelectItem>
                          <SelectItem value="MEDIUM">Medium</SelectItem>
                          <SelectItem value="HIGH">High</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    className="w-full"
                    disabled={scenarioRunning || (!scenarioAudience && !scenarioBudget)}
                    onClick={handleScenario}
                  >
                    {scenarioRunning ? (
                      <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Simulating…</>
                    ) : (
                      <><FlaskConical className="h-4 w-4 mr-2" /> Simulate Scenario</>
                    )}
                  </Button>

                  {/* Scenario Result */}
                  {scenarioResult && (
                    <div className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">Simulated</Badge>
                        <span className="text-xs text-muted-foreground">vs. baseline</span>
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <p className="text-xs text-muted-foreground">Discoverability</p>
                          <p className="text-lg font-bold">{scenarioResult.discoverability}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Delta</p>
                          <p className={`text-lg font-bold flex items-center gap-1 ${scenarioResult.delta > 0 ? 'text-green-500' : scenarioResult.delta < 0 ? 'text-red-500' : 'text-muted-foreground'}`}>
                            {scenarioResult.delta > 0 ? (
                              <ArrowUpRight className="h-4 w-4" />
                            ) : scenarioResult.delta < 0 ? (
                              <ArrowDownRight className="h-4 w-4" />
                            ) : null}
                            {scenarioResult.delta > 0 ? '+' : ''}{scenarioResult.delta}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Primary Channel</p>
                          <Badge variant="outline" className="text-xs mt-1">
                            {channelLabel(scenarioResult.primaryChannel)}
                          </Badge>
                        </div>
                      </div>
                      <Separator />
                      <div className="space-y-1.5">
                        {Object.entries(scenarioResult.budgetAllocation)
                          .sort(([, a], [, b]) => b - a)
                          .map(([ch, pct]) => (
                            <div key={ch} className="flex items-center gap-2 text-xs">
                              <div className={`w-2 h-2 rounded-full ${channelColor(ch)}`} />
                              <span className="text-muted-foreground flex-1">{channelLabel(ch)}</span>
                              <span className="font-medium">{pct}%</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
          {/* Confirm & Advance */}
          {result && (
            <div className="flex justify-end mt-8">
              <Button
                onClick={handleConfirmAndAdvance}
                disabled={confirming}
                size="lg"
                className="bg-primary hover:bg-primary/90"
              >
                {confirming ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <ArrowRight className="h-4 w-4 mr-2" />}
                Confirm & Advance to Phase 6
              </Button>
            </div>
          )}
        </div>

        {/* ═══ RIGHT COLUMN — public figures sidebar ═══ */}
        {result && renderSidebar()}

      </div>
    </div>
  );
}
