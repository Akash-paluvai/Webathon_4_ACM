/**
 PHASE 4 — Post-Production & Market Testing
 */

import { useState, useRef } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Upload, Sparkles, Film, BarChart3, AlertTriangle, Loader2, ArrowRight } from 'lucide-react';
import { submitPhase4, generatePhase4Insights, updateProjectPhase } from '@/api';
import type { Phase4Result, AIInsights } from '@/api';

export default function Phase4Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };

  // ── Form state ──
  const fileRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [testStrategy, setTestStrategy] = useState<string>('');

  // ── Submission state ──
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<Phase4Result | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // ── Insight state ──
  const [insights, setInsights] = useState<AIInsights | null>(null);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [insightsError, setInsightsError] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);

  // ── Handlers ──

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setSelectedFile(file);
  };

  const handleSubmit = async () => {
    if (!selectedFile || !testStrategy) return;
    setSubmitting(true);
    setSubmitError(null);
    setResult(null);
    setInsights(null);
    setInsightsError(null);

    try {
      const res = await submitPhase4(Number(projectId), selectedFile, testStrategy);
      setResult(res);
    } catch (err: unknown) {
      setSubmitError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleGenerateInsights = async () => {
    if (!result) return;
    setInsightsLoading(true);
    setInsightsError(null);

    try {
      const res = await generatePhase4Insights(Number(projectId), {
        audienceType: result.audienceType,
        audienceInterestScore: result.audienceInterestScore,
        testStrategy: result.testStrategy,
        trailerFeatures: result.trailerFeatures,
      });
      setInsights(res);
    } catch (err: unknown) {
      setInsightsError(err instanceof Error ? err.message : 'Insight generation failed');
    } finally {
      setInsightsLoading(false);
    }
  };

  const handleConfirmAndAdvance = async () => {
    setConfirming(true);
    try {
      await updateProjectPhase(Number(projectId), 5);
      navigate({ to: '/projects/$projectId/phase-5', params: { projectId } });
    } catch (err: unknown) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to advance phase');
    } finally {
      setConfirming(false);
    }
  };

  // ── Helpers ──

  const audienceBadgeVariant = (type: string) => {
    switch (type.toLowerCase()) {
      case 'mass': return 'default' as const;
      case 'regional': return 'secondary' as const;
      case 'niche': return 'outline' as const;
      default: return 'outline' as const;
    }
  };

  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
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
        <h1 className="text-3xl font-bold mb-2">Phase 4: Post-Production & Market Testing</h1>
        <p className="text-muted-foreground text-lg">
          Upload your trailer to analyse audience fit and generate strategic insights
        </p>
      </div>

      {/* ── Trailer Upload Card ── */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Film className="h-5 w-5" />
            Trailer Analysis
          </CardTitle>
          <CardDescription>
            Upload an MP4 trailer and select a test strategy to begin analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* File Upload */}
          <div className="space-y-2">
            <Label htmlFor="trailer-upload">Trailer Video (MP4)</Label>
            <div
              className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => fileRef.current?.click()}
            >
              <input
                ref={fileRef}
                id="trailer-upload"
                type="file"
                accept="video/mp4,video/*"
                className="hidden"
                onChange={handleFileChange}
              />
              <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              {selectedFile ? (
                <p className="text-sm font-medium">{selectedFile.name}
                  <span className="text-muted-foreground ml-2">
                    ({(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)
                  </span>
                </p>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Click to select or drag & drop your trailer file
                </p>
              )}
            </div>
          </div>

          {/* Test Strategy Selector */}
          <div className="space-y-2">
            <Label htmlFor="test-strategy">Test Strategy</Label>
            <Select value={testStrategy} onValueChange={setTestStrategy}>
              <SelectTrigger id="test-strategy">
                <SelectValue placeholder="Select test strategy…" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="FESTIVAL">Festival Screening</SelectItem>
                <SelectItem value="PRIVATE">Private Screening</SelectItem>
                <SelectItem value="DIGITAL">Digital Testing</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Submit */}
          <Button
            className="w-full"
            disabled={!selectedFile || !testStrategy || submitting}
            onClick={handleSubmit}
          >
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analysing Trailer…
              </>
            ) : (
              <>
                <BarChart3 className="h-4 w-4 mr-2" />
                Analyse Trailer
              </>
            )}
          </Button>

          {submitError && (
            <div className="flex items-center gap-2 text-sm text-destructive mt-2">
              <AlertTriangle className="h-4 w-4" />
              {submitError}
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Results Card ── */}
      {result && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Analysis Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Audience Type</p>
                <Badge variant={audienceBadgeVariant(result.audienceType)} className="text-sm">
                  {result.audienceType.toUpperCase()}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Test Strategy</p>
                <Badge variant="secondary" className="text-sm">
                  {result.testStrategy}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Interest Score</p>
                <p className={`text-2xl font-bold ${scoreColor(result.audienceInterestScore)}`}>
                  {result.audienceInterestScore}
                  <span className="text-sm font-normal text-muted-foreground">/100</span>
                </p>
              </div>
            </div>

            {/* Score Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Audience Interest</span>
                <span className={scoreColor(result.audienceInterestScore)}>
                  {result.audienceInterestScore}%
                </span>
                {(result.enhancedAnalysisAvailable || insights?.enhancedAnalysisAvailable) && (
                  <Badge variant="outline" className="border-primary/50 text-primary bg-primary/5 animate-pulse flex items-center gap-1">
                    <Sparkles className="h-3 w-3" />
                    Enhanced Video Understanding Applied
                  </Badge>
                )}
              </div>
              <Progress value={result.audienceInterestScore} className="h-2" />
            </div>

            <Separator />

            {/* Advanced Signals Section */}
            {(result.enhancedSignals || insights?.enhancedSignals) && (
              <div>
                <p className="text-sm font-medium mb-3 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Advanced Behavioral Signals
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="bg-primary/5 border border-primary/10 rounded-lg p-3">
                    <p className="text-xs text-muted-foreground mb-1">Violence Likelihood</p>
                    <p className="text-sm font-bold flex items-center gap-2">
                      <AlertTriangle className={`h-4 w-4 ${(result.enhancedSignals || insights?.enhancedSignals)?.violenceLikelihood === 'HIGH' ? 'text-red-500' : 'text-muted-foreground'}`} />
                      {(result.enhancedSignals || insights?.enhancedSignals)?.violenceLikelihood}
                    </p>
                  </div>
                  <div className="bg-primary/5 border border-primary/10 rounded-lg p-3">
                    <p className="text-xs text-muted-foreground mb-1">Emotional Tone</p>
                    <p className="text-sm font-bold flex items-center gap-2">
                      <Film className="h-4 w-4 text-purple-500" />
                      {(result.enhancedSignals || insights?.enhancedSignals)?.emotionalTone}
                    </p>
                  </div>
                  <div className="bg-primary/5 border border-primary/10 rounded-lg p-3">
                    <p className="text-xs text-muted-foreground mb-1">Genre Inclination</p>
                    <p className="text-sm font-bold flex items-center gap-2">
                      <BarChart3 className="h-4 w-4 text-blue-500" />
                      {(result.enhancedSignals || insights?.enhancedSignals)?.genreInclination}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <Separator />

            {/* Trailer Features Summary */}
            <div>
              <p className="text-sm font-medium mb-3">Trailer Feature Summary</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {result.trailerFeatures.duration_sec != null && (
                  <div className="bg-muted/50 rounded-lg p-3 text-center">
                    <p className="text-xs text-muted-foreground">Duration</p>
                    <p className="text-sm font-semibold">{Number(result.trailerFeatures.duration_sec).toFixed(1)}s</p>
                  </div>
                )}
                {result.trailerFeatures.scene_change_count != null && (
                  <div className="bg-muted/50 rounded-lg p-3 text-center">
                    <p className="text-xs text-muted-foreground">Scene Changes</p>
                    <p className="text-sm font-semibold">{String(result.trailerFeatures.scene_change_count)}</p>
                  </div>
                )}
                {result.trailerFeatures.average_shot_length_sec != null && (
                  <div className="bg-muted/50 rounded-lg p-3 text-center">
                    <p className="text-xs text-muted-foreground">Avg Shot</p>
                    <p className="text-sm font-semibold">{Number(result.trailerFeatures.average_shot_length_sec).toFixed(1)}s</p>
                  </div>
                )}
                {result.trailerFeatures.average_brightness != null && (
                  <div className="bg-muted/50 rounded-lg p-3 text-center">
                    <p className="text-xs text-muted-foreground">Brightness</p>
                    <p className="text-sm font-semibold">{Number(result.trailerFeatures.average_brightness).toFixed(0)}/255</p>
                  </div>
                )}
              </div>
            </div>

            <Separator />

            {/* Generate Insights Button */}
            <Button
              variant="outline"
              className="w-full"
              onClick={handleGenerateInsights}
              disabled={insightsLoading}
            >
              {insightsLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating Insights…
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Strategic Insights
                </>
              )}
            </Button>

            {insightsError && (
              <div className="flex items-center gap-2 text-sm text-destructive">
                <AlertTriangle className="h-4 w-4" />
                {insightsError}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ── AI-Generated Insights Card ── */}
      {insights && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              AI-Generated Strategic Insights
            </CardTitle>
            <CardDescription>
              Powered by Cerebras AI — based on trailer analysis data and audience context
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="space-y-2">
              <h4 className="text-sm font-semibold flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-blue-500" />
                Market Read
              </h4>
              <p className="text-sm leading-relaxed text-muted-foreground pl-6">
                {insights.marketRead}
              </p>
            </div>
            <Separator />
            <div className="space-y-2">
              <h4 className="text-sm font-semibold flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" />
                Risk Signals
              </h4>
              <p className="text-sm leading-relaxed text-muted-foreground pl-6">
                {insights.riskSignals}
              </p>
            </div>
            <Separator />
            <div className="space-y-2">
              <h4 className="text-sm font-semibold flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-green-500" />
                Strategic Recommendations
              </h4>
              <p className="text-sm leading-relaxed text-muted-foreground pl-6">
                {insights.strategicRecommendations}
              </p>
            </div>
          </CardContent>
        </Card>
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
            Confirm & Advance to Phase 5
          </Button>
        </div>
      )}
    </div>
  );
}
