/**
 * PHASE 5 — Marketing Strategy Planning
 *
 * Inputs (user):
 *   - marketingBudgetLevel: LOW | MEDIUM | HIGH
 *
 * Reads from FilmProject:
 *   - audienceType, audienceInterestScore (via Phase 4)
 *   - scale, budgetLevel
 *
 * Persists:
 *   - marketingBudgetLevel
 *   - primaryMarketingChannel
 *
 * Returned in response only (NOT persisted):
 *   - budgetAllocation, discoverabilityScore, marketingRisk,
 *     riskFlags, explanation
 */

import { useState } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Megaphone, BarChart3, AlertTriangle, Loader2, ShieldAlert, TrendingUp } from 'lucide-react';
import { submitPhase5 } from '@/api';
import type { Phase5Result } from '@/api';

export default function Phase5Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };

  // ── Form state ──
  const [budgetLevel, setBudgetLevel] = useState<string>('');

  // ── Submission state ──
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<Phase5Result | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
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

      {/* ── Budget Input Card ── */}
      <Card className="mb-6">
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

      {/* ── Results ── */}
      {result && (
        <>
          {/* Key Metrics */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Marketing Plan
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

              {/* Explanation */}
              <div className="bg-muted/50 rounded-lg p-4">
                <p className="text-sm leading-relaxed">{result.explanation}</p>
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
        </>
      )}
    </div>
  );
}
