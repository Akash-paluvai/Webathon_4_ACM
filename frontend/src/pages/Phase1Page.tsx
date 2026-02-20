import { useState } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Sparkles, Loader2, ArrowRight, AlertTriangle, Users } from 'lucide-react';
import { analyzePhase1, updateProjectPhase } from '@/api';
import { useGetProject } from '@/hooks/useQueries';

export default function Phase1Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };
  const { data: project } = useGetProject(Number(projectId));

  const [scriptText, setScriptText] = useState('');
  const [genre, setGenre] = useState('Drama');
  const [theme, setTheme] = useState('');
  const [scale, setScale] = useState('studio');
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!scriptText.trim()) {
      setError('Please enter script text to analyze.');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const result = await analyzePhase1({
        scriptText,
        genre,
        theme: theme || project?.theme || '',
        scale,
      });
      setAnalysis(result);
    } catch (err: any) {
      setError(err.message || 'Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmAndAdvance = async () => {
    setConfirming(true);
    setError(null);
    try {
      await updateProjectPhase(Number(projectId), 2);
      navigate({ to: '/projects/$projectId', params: { projectId } });
    } catch (err: any) {
      setError(err.message || 'Failed to advance phase.');
    } finally {
      setConfirming(false);
    }
  };

  const riskColor = (level: string) => {
    const l = level?.toLowerCase();
    if (l === 'low') return 'default' as const;
    if (l === 'high') return 'destructive' as const;
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
        <h1 className="text-3xl font-bold mb-2">Phase 1: Script Selection & Concept Evaluation</h1>
        <p className="text-muted-foreground text-lg">
          Analyze your script with AI to assess market viability and audience alignment
        </p>
      </div>

      {/* Input Section */}
      <div className="grid lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Script Upload
              </CardTitle>
              <CardDescription>Paste your script or synopsis for AI-powered analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                value={scriptText}
                onChange={(e) => setScriptText(e.target.value)}
                placeholder="Paste your script / synopsis here for AI analysis…"
                className="min-h-[200px] font-mono text-sm"
              />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Parameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Genre</Label>
                <Select value={genre} onValueChange={setGenre}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {['Drama', 'Action', 'Comedy', 'Thriller', 'Horror', 'Romance', 'Sci-Fi', 'Documentary'].map(g => (
                      <SelectItem key={g} value={g}>{g}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Theme</Label>
                <Input
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                  placeholder="e.g. Redemption, Coming of Age"
                />
              </div>
              <div>
                <Label>Scale</Label>
                <Select value={scale} onValueChange={setScale}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="indie">Indie</SelectItem>
                    <SelectItem value="studio">Studio</SelectItem>
                    <SelectItem value="blockbuster">Blockbuster</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Button onClick={handleAnalyze} disabled={loading} className="w-full" size="lg">
            {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Sparkles className="h-4 w-4 mr-2" />}
            {loading ? 'Analyzing…' : 'Analyze Script'}
          </Button>
        </div>
      </div>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Loading skeleton */}
      {loading && !analysis && (
        <div className="grid lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2"><CardContent className="pt-6 space-y-4">
            <div className="h-6 w-48 bg-muted rounded animate-pulse" />
            <div className="h-4 w-full bg-muted rounded animate-pulse" />
            <div className="h-4 w-2/3 bg-muted rounded animate-pulse" />
          </CardContent></Card>
          <Card><CardContent className="pt-6 space-y-4">
            <div className="h-20 w-20 bg-muted rounded-full mx-auto animate-pulse" />
            <div className="h-4 w-24 bg-muted rounded mx-auto animate-pulse" />
          </CardContent></Card>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !loading && (
        <div className="space-y-6">
          {/* Metrics Row */}
          <div className="grid md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-4xl font-bold">{analysis.feasibility_score ?? '—'}</p>
                <p className="text-sm text-muted-foreground mt-1">Feasibility Score</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <Badge variant={riskColor(analysis.risk_level)} className="text-lg px-4 py-1">
                  <AlertTriangle className="h-4 w-4 mr-1" />
                  {analysis.risk_level ?? 'Unknown'}
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">Concept Risk</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-4xl font-bold">{analysis.audience?.audience_match_score ?? '—'}%</p>
                <p className="text-sm text-muted-foreground mt-1">Audience Match</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-4xl font-bold">{analysis.audience?.engagement_potential ?? '—'}%</p>
                <p className="text-sm text-muted-foreground mt-1">Engagement Potential</p>
              </CardContent>
            </Card>
          </div>

          {/* Detail Cards */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Audience Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  Audience Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Target Segment</span>
                  <Badge>{analysis.audience?.recommended_segment ?? 'N/A'}</Badge>
                </div>
                <Separator />
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Generation</span>
                  <span className="font-medium">{analysis.audience?.generation ?? 'N/A'}</span>
                </div>
                <Separator />
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Genre Demand</span>
                  <Badge variant="outline">{analysis.genre_demand_band ?? 'N/A'}</Badge>
                </div>
                <Separator />
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-muted-foreground text-sm">Audience Match</span>
                    <span className="text-sm font-medium">{analysis.audience?.audience_match_score ?? 0}%</span>
                  </div>
                  <Progress value={analysis.audience?.audience_match_score ?? 0} />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-muted-foreground text-sm">Engagement</span>
                    <span className="text-sm font-medium">{analysis.audience?.engagement_potential ?? 0}%</span>
                  </div>
                  <Progress value={analysis.audience?.engagement_potential ?? 0} />
                </div>
              </CardContent>
            </Card>

            {/* Sentiment & Emotion Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  NLP Insights
                </CardTitle>
                <CardDescription>Transformer-powered script analysis</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sentiment</span>
                  <Badge variant={analysis.audience?.sentiment_label === 'POSITIVE' ? 'default' : analysis.audience?.sentiment_label === 'NEGATIVE' ? 'destructive' : 'secondary'}>
                    {analysis.audience?.sentiment_label ?? 'N/A'}
                  </Badge>
                </div>
                <Separator />
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Dominant Emotion</span>
                  <span className="font-medium capitalize">{analysis.audience?.dominant_emotion ?? 'N/A'}</span>
                </div>
                <Separator />
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-muted-foreground text-sm">Sentiment Positivity</span>
                    <span className="text-sm font-medium">{Math.round((analysis.audience?.sentiment_score ?? 0.5) * 100)}%</span>
                  </div>
                  <Progress value={Math.round((analysis.audience?.sentiment_score ?? 0.5) * 100)} />
                </div>
                {analysis.metrics?.top_themes && analysis.metrics.top_themes.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <span className="text-muted-foreground text-sm block mb-2">Detected Themes</span>
                      <div className="flex flex-wrap gap-2">
                        {analysis.metrics.top_themes.map((t: string, i: number) => (
                          <Badge key={i} variant="outline" className="capitalize">{t}</Badge>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* AI Summary */}
          <Card>
            <CardHeader>
              <CardTitle>AI Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {analysis.summary || 'No summary available.'}
              </p>
            </CardContent>
          </Card>

          {/* Confirm & Advance */}
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={handleAnalyze}>
              Re-run Analysis
            </Button>
            <Button onClick={handleConfirmAndAdvance} disabled={confirming} size="lg">
              {confirming ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <ArrowRight className="h-4 w-4 mr-2" />}
              Confirm & Advance to Phase 2
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
