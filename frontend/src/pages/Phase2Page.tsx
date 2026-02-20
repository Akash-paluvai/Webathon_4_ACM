import { useState } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import {
  ArrowLeft, Package, Loader2, ArrowRight, AlertTriangle, TrendingUp,
  DollarSign, Users, BarChart3,
} from 'lucide-react';
import { analyzeFeasibility, analyzePackaging, confirmPhase2, updateProjectPhase } from '@/api';
import { useGetProject } from '@/hooks/useQueries';

export default function Phase2Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };
  const pid = Number(projectId);
  const { data: project } = useGetProject(pid);

  const [budgetLevel, setBudgetLevel] = useState('Mid');
  const [talentStrategy, setTalentStrategy] = useState('Mixed');
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feasibility, setFeasibility] = useState<any>(null);
  const [packaging, setPackaging] = useState<any>(null);

  const handleFeasibility = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeFeasibility(pid, { budgetLevel, talentStrategy });
      setFeasibility(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handlePackaging = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await analyzePackaging(pid, { budgetLevel, talentStrategy });
      setPackaging(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handleConfirm = async () => {
    setConfirming(true);
    setError(null);
    try {
      await confirmPhase2(pid, { budgetLevel, talentStrategy });
      await updateProjectPhase(pid, 3);
      navigate({ to: '/projects/$projectId', params: { projectId } });
    } catch (e: any) { setError(e.message); }
    finally { setConfirming(false); }
  };

  const riskColor = (level: string) => {
    const l = level?.toLowerCase();
    if (l === 'low') return 'default' as const;
    if (l === 'high') return 'destructive' as const;
    return 'secondary' as const;
  };

  const budgetOptions = ['Low', 'Mid', 'High'];
  const talentOptions = ['Newcomers', 'Mixed', 'Stars'];

  return (
    <div className="container mx-auto px-4 py-8">
      <Button
        variant="ghost"
        onClick={() => navigate({ to: '/projects/$projectId', params: { projectId } })}
        className="mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Project Overview
      </Button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Phase 2: Packaging & Feasibility</h1>
        <p className="text-muted-foreground text-lg">
          Budget strategy, talent packaging, and production viability analysis
        </p>
      </div>

      {/* Input Controls */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-primary" />
              Budget Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-3">
              {budgetOptions.map(opt => (
                <Button
                  key={opt}
                  variant={budgetLevel === opt ? 'default' : 'outline'}
                  onClick={() => setBudgetLevel(opt)}
                  className="w-full"
                >
                  {opt}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-primary" />
              Talent Strategy
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-3">
              {talentOptions.map(opt => (
                <Button
                  key={opt}
                  variant={talentStrategy === opt ? 'default' : 'outline'}
                  onClick={() => setTalentStrategy(opt)}
                  className="w-full"
                >
                  {opt}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-6">
        <Button onClick={handleFeasibility} disabled={loading} size="lg">
          {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <BarChart3 className="h-4 w-4 mr-2" />}
          Analyze Feasibility
        </Button>
        <Button onClick={handlePackaging} disabled={loading || !feasibility} variant="outline" size="lg">
          <Package className="h-4 w-4 mr-2" />
          Compare Scenarios
        </Button>
      </div>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Feasibility Results */}
      {feasibility && !loading && (
        <div className="space-y-6">
          {/* Score Cards */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-4xl font-bold">{feasibility.feasibility_score ?? '—'}</p>
                <p className="text-sm text-muted-foreground mt-1">Feasibility Score</p>
                <Progress value={feasibility.feasibility_score ?? 0} className="mt-3" />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <Badge variant={riskColor(feasibility.risk_indicator)} className="text-lg px-4 py-1">
                  <AlertTriangle className="h-4 w-4 mr-1" />
                  {feasibility.risk_indicator ?? 'Unknown'}
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">Risk Level</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <Badge variant="outline" className="text-lg px-4 py-1">
                  {feasibility.cost_alignment ?? 'N/A'}
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">Cost Alignment</p>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Score Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Budget Score</span>
                  <span className="text-sm font-medium">{feasibility.metrics?.budget_score ?? 0}</span>
                </div>
                <Progress value={feasibility.metrics?.budget_score ?? 0} />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Talent Score</span>
                  <span className="text-sm font-medium">{feasibility.metrics?.talent_score ?? 0}</span>
                </div>
                <Progress value={feasibility.metrics?.talent_score ?? 0} />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Scale Score</span>
                  <span className="text-sm font-medium">{feasibility.metrics?.scale_score ?? 0}</span>
                </div>
                <Progress value={feasibility.metrics?.scale_score ?? 0} />
              </div>
              <Separator />
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Genre</span>
                <span className="font-medium">{feasibility.genre}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Audience</span>
                <span className="font-medium">{feasibility.audience}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Scale</span>
                <span className="font-medium">{feasibility.scale}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Packaging Scenarios */}
      {packaging && (
        <div className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5 text-primary" />
                Packaging Scenarios
              </CardTitle>
              <CardDescription>AI-generated packaging options compared side-by-side</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {(packaging.scenarios || []).map((s: any, i: number) => {
                  const isRec = packaging.recommended_option &&
                    s.budgetLevel === packaging.recommended_option.budgetLevel &&
                    s.talentStrategy === packaging.recommended_option.talentStrategy;
                  return (
                    <Card key={i} className={isRec ? 'border-primary border-2' : ''}>
                      <CardHeader className="pb-2">
                        {isRec && <Badge className="w-fit mb-2">★ Recommended</Badge>}
                        <CardTitle className="text-base">{s.budgetLevel} Budget</CardTitle>
                        <CardDescription>{s.talentStrategy} Strategy</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <div className="flex justify-between mb-1">
                            <span className="text-xs text-muted-foreground">Feasibility</span>
                            <span className="text-xs font-medium">{s.feasibility_score}</span>
                          </div>
                          <Progress value={s.feasibility_score ?? 0} />
                        </div>
                        <div>
                          <div className="flex justify-between mb-1">
                            <span className="text-xs text-muted-foreground">ROI Probability</span>
                            <span className="text-xs font-medium">{s.roi_probability}</span>
                          </div>
                          <Progress value={s.roi_probability ?? 0} />
                        </div>
                        <Badge variant={riskColor(s.risk_indicator)}>
                          {s.risk_indicator} Risk
                        </Badge>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Confirm & Advance */}
      {feasibility && (
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="outline" onClick={handleFeasibility}>
            Adjust Strategy
          </Button>
          <Button onClick={handleConfirm} disabled={confirming} size="lg">
            {confirming ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <ArrowRight className="h-4 w-4 mr-2" />}
            Confirm & Advance to Phase 3
          </Button>
        </div>
      )}
    </div>
  );
}
