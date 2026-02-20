import { useState } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import {
  ArrowLeft, Loader2, ArrowRight, AlertTriangle, Calendar,
  Clock, Users, BarChart3, Activity, Shield,
} from 'lucide-react';
import { analyzePhase3, confirmPhase3 as apiConfirmPhase3, updateProjectPhase } from '@/api';
import { useGetProject } from '@/hooks/useQueries';

export default function Phase3Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };
  const pid = Number(projectId);
  const { data: project } = useGetProject(pid);

  const [inputs, setInputs] = useState({
    plannedShootDays: project?.plannedShootDays ?? 40,
    daysPerWeek: 5,
    hoursPerDay: 8,
    crewSize: 30,
    complexityLevel: 2,
    currentProgressPercent: 0,
    actualShootDays: null as number | null,
  });

  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await analyzePhase3({ ...inputs, projectId: pid });
      setAnalysis(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handleConfirm = async () => {
    setConfirming(true);
    setError(null);
    try {
      const health = analysis?.analysis?.productionHealth || 'good';
      await apiConfirmPhase3(pid, {
        plannedShootDays: inputs.plannedShootDays,
        actualShootDays: inputs.actualShootDays,
        productionHealth: health,
      });
      await updateProjectPhase(pid, 4);
      navigate({ to: '/projects/$projectId', params: { projectId } });
    } catch (e: any) { setError(e.message); }
    finally { setConfirming(false); }
  };

  const a = analysis?.analysis || {};
  const explain = analysis?.explainability || {};

  const riskColor = (level: string) => {
    const l = level?.toLowerCase();
    if (l === 'low') return 'default' as const;
    if (l === 'high') return 'destructive' as const;
    return 'secondary' as const;
  };

  const healthColor = (h: string) => {
    if (h === 'good') return 'default' as const;
    if (h === 'critical') return 'destructive' as const;
    return 'secondary' as const;
  };

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
        <h1 className="text-3xl font-bold mb-2">Phase 3: Production Intelligence</h1>
        <p className="text-muted-foreground text-lg">
          Schedule prediction, delay risk analysis, and production health tracking
        </p>
      </div>

      {/* Input Grid */}
      <div className="grid lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-primary" />
              Schedule Parameters
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Planned Shoot Days</Label>
                <Input
                  type="number" min={1} max={200}
                  value={inputs.plannedShootDays}
                  onChange={e => setInputs({ ...inputs, plannedShootDays: parseInt(e.target.value) || 40 })}
                />
              </div>
              <div>
                <Label>Days Per Week</Label>
                <Input
                  type="number" min={1} max={7}
                  value={inputs.daysPerWeek}
                  onChange={e => setInputs({ ...inputs, daysPerWeek: parseInt(e.target.value) || 5 })}
                />
              </div>
              <div>
                <Label>Hours Per Day</Label>
                <Input
                  type="number" min={4} max={16}
                  value={inputs.hoursPerDay}
                  onChange={e => setInputs({ ...inputs, hoursPerDay: parseInt(e.target.value) || 8 })}
                />
              </div>
              <div>
                <Label>Crew Size</Label>
                <Input
                  type="number" min={5} max={500}
                  value={inputs.crewSize}
                  onChange={e => setInputs({ ...inputs, crewSize: parseInt(e.target.value) || 30 })}
                />
              </div>
            </div>

            <div>
              <Label>Complexity Level: {inputs.complexityLevel}</Label>
              <Slider
                value={[inputs.complexityLevel]}
                onValueChange={([v]) => setInputs({ ...inputs, complexityLevel: v })}
                min={1} max={5} step={1}
                className="mt-2"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Simple</span><span>Complex</span>
              </div>
            </div>

            <div>
              <Label>Current Progress: {inputs.currentProgressPercent}%</Label>
              <Slider
                value={[inputs.currentProgressPercent]}
                onValueChange={([v]) => setInputs({ ...inputs, currentProgressPercent: v })}
                min={0} max={100} step={5}
                className="mt-2"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Production Tracking
            </CardTitle>
            <CardDescription>Optional: enter actual shoot days to compare against plan</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Actual Shoot Days (optional)</Label>
              <Input
                type="number" min={0}
                value={inputs.actualShootDays ?? ''}
                onChange={e => setInputs({
                  ...inputs,
                  actualShootDays: e.target.value ? parseInt(e.target.value) : null
                })}
                placeholder="Leave blank if not started"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analyze Button */}
      <Button onClick={handleAnalyze} disabled={loading} size="lg" className="mb-6">
        {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <BarChart3 className="h-4 w-4 mr-2" />}
        {loading ? 'Analyzing…' : 'Analyze Schedule'}
      </Button>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {analysis && !loading && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6 text-center">
                <Calendar className="h-6 w-6 mx-auto mb-2 text-primary" />
                <p className="text-3xl font-bold">{a.recommendedTotalDays ?? '—'}</p>
                <p className="text-sm text-muted-foreground mt-1">Predicted Days</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <Shield className="h-6 w-6 mx-auto mb-2 text-primary" />
                <p className="text-3xl font-bold">{Math.round((a.delayProbability ?? 0) * 100)}%</p>
                <p className="text-sm text-muted-foreground mt-1">Delay Probability</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <Badge variant={riskColor(a.scheduleRisk)} className="text-lg px-4 py-1">
                  <AlertTriangle className="h-4 w-4 mr-1" />
                  {a.scheduleRisk ?? 'N/A'}
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">Schedule Risk</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <Badge variant={healthColor(a.productionHealth)} className="text-lg px-4 py-1">
                  {a.productionHealth ?? 'good'}
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">Production Health</p>
              </CardContent>
            </Card>
          </div>

          {/* Variance & Progress */}
          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Progress vs Plan</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Current Progress</span>
                    <span className="text-sm font-medium">{inputs.currentProgressPercent}%</span>
                  </div>
                  <Progress value={inputs.currentProgressPercent} />
                </div>
                {inputs.actualShootDays && (
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Actual / Predicted</span>
                      <span className="text-sm font-medium">
                        {Math.round((inputs.actualShootDays / (a.recommendedTotalDays || inputs.plannedShootDays)) * 100)}%
                      </span>
                    </div>
                    <Progress value={(inputs.actualShootDays / (a.recommendedTotalDays || inputs.plannedShootDays)) * 100} />
                  </div>
                )}
                <Separator />
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Variance</span>
                  <span className={`font-bold ${(a.variance ?? 0) > 0 ? 'text-destructive' : 'text-green-600'}`}>
                    {a.variance > 0 ? '+' : ''}{a.variance ?? 0} days
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Weekly Target</span>
                  <span className="font-medium">{a.weeklyPlan ?? '—'} days/week</span>
                </div>
              </CardContent>
            </Card>

            {/* XAI Explanation */}
            <Card>
              <CardHeader>
                <CardTitle>AI Explanation</CardTitle>
                <CardDescription>Explainable AI — feature importance analysis</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {explain.explanation && (
                  <p className="text-sm text-muted-foreground leading-relaxed">{explain.explanation}</p>
                )}
                {explain.featureImportance && (
                  <div className="space-y-3">
                    {Object.entries(explain.featureImportance).map(([feat, val]) => (
                      <div key={feat}>
                        <div className="flex justify-between mb-1">
                          <span className="text-xs text-muted-foreground">{feat.replace(/([A-Z])/g, ' $1')}</span>
                          <span className="text-xs font-medium">{Math.round(((val as number) ?? 0) * 100)}%</span>
                        </div>
                        <Progress value={((val as number) ?? 0) * 100} />
                      </div>
                    ))}
                  </div>
                )}
                {!explain.explanation && !explain.featureImportance && (
                  <p className="text-sm text-muted-foreground italic">No explainability data available.</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Confirm */}
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={handleAnalyze}>
              Re-run Analysis
            </Button>
            <Button onClick={handleConfirm} disabled={confirming} size="lg">
              {confirming ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <ArrowRight className="h-4 w-4 mr-2" />}
              Confirm Production Phase
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
