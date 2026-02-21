import { useState, useEffect } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ArrowLeft,
  TrendingUp,
  Globe,
  Users,
  DollarSign,
  Search,
  Loader2,
  CheckCircle2,
  AlertCircle,
  BarChart3,
  MessageSquare,
  Award,
  ExternalLink,
  Save
} from 'lucide-react';
import { getProject, getPhase8Report, updatePhase8Results, Phase8Report } from '@/api';
import { FilmProject } from '@/types';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';

export default function Phase8Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };

  const [project, setProject] = useState<FilmProject | null>(null);
  const [report, setReport] = useState<Phase8Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // For saving results
  const [learningSummary, setLearningSummary] = useState('');
  const [selectedResponse, setSelectedResponse] = useState<'WEAK' | 'MODERATE' | 'STRONG'>('MODERATE');

  useEffect(() => {
    async function loadData() {
      try {
        const p = await getProject(Number(projectId));
        setProject(p);
        setLearningSummary(p.learningSummary || '');
        if (p.audienceResponse) setSelectedResponse(p.audienceResponse as any);

        // Fetch Phase 8 report using project title
        const r = await getPhase8Report(p.title);
        setReport(r);
      } catch (err) {
        console.error("Failed to load Phase 8 data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [projectId]);

  const handleSave = async () => {
    if (!project) return;
    setSaving(true);
    try {
      await updatePhase8Results(Number(projectId), {
        audienceResponse: selectedResponse,
        monetizationOptions: report?.sections?.marketing_suggestions?.value?.join(', ') || '',
        learningSummary,
        currentPhase: 8
      });
      toast.success("Post-release results saved successfully!");
    } catch (err) {
      toast.error("Failed to save results");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-3 text-lg">Generating Global Performance Report...</span>
      </div>
    );
  }

  if (!project || !report) {
    return (
      <div className="container mx-auto p-8 text-center">
        <AlertCircle className="h-12 w-12 mx-auto text-destructive mb-4" />
        <h2 className="text-2xl font-bold">Failed to load Project details</h2>
        <Button onClick={() => navigate({ to: '/projects' })} className="mt-4">Back to Projects</Button>
      </div>
    );
  }

  const movie = report.movie;
  const sections = report.sections;
  const insights = report.insights;

  const formatCurrency = (val: any) => {
    if (typeof val === 'string') return val;
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <Button
            variant="ghost"
            onClick={() => navigate({ to: '/projects/$projectId', params: { projectId } })}
            className="mb-2 p-0 h-auto hover:bg-transparent text-muted-foreground hover:text-primary transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Project Overview
          </Button>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-600">
            Phase 8: Monitoring & Optimization
          </h1>
          <p className="text-muted-foreground text-lg mt-1">
            Real-time performance indexing for <span className="text-foreground font-semibold">"{movie.title}"</span>
          </p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="px-3 py-1 border-primary/20 bg-primary/5">
            <TrendingUp className="h-3 w-3 mr-2 text-primary" />
            {insights?.revenue_classification || "Live Tracking"}
          </Badge>
          <Badge variant="secondary" className="px-3 py-1">
            Released: {movie.release_date || "Unknown"}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Financial Performance Overview */}
        <Card className="lg:col-span-2 overflow-hidden border-primary/10 shadow-lg">
          <CardHeader className="bg-muted/30 pb-4">
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-xl flex items-center">
                  <DollarSign className="h-5 w-5 mr-2 text-green-500" />
                  Financial Performance Dashboard
                </CardTitle>
                <CardDescription>Consolidated Revenue Data (TMDb / Kaggle Hybrid)</CardDescription>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-bold">Worldwide Revenue</p>
                <p className="text-2xl font-black text-primary">{formatCurrency(movie.revenue || 0)}</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="space-y-1">
                <span className="text-sm text-muted-foreground">Lifetime Forecast</span>
                <p className="text-xl font-bold">{formatCurrency(sections.lifetime_revenue?.value)}</p>
                <div className="flex items-center text-xs text-muted-foreground">
                  <Badge variant="outline" className="p-0 h-auto font-normal text-[10px] uppercase border-none hover:bg-transparent">
                    Confidence: {(sections.lifetime_revenue?.confidence * 100).toFixed(0)}%
                  </Badge>
                </div>
              </div>
              <div className="space-y-1">
                <span className="text-sm text-muted-foreground">Net Profit/Loss</span>
                <p className={`text-xl font-bold ${typeof sections.net_profit?.value === 'number' && sections.net_profit.value >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {formatCurrency(sections.net_profit?.value)}
                </p>
                <Progress value={Math.min(100, Math.max(0, insights?.multiplier_percentile_overall || 50))} className="h-1" />
              </div>
              <div className="space-y-1">
                <span className="text-sm text-muted-foreground">Break-Even Point</span>
                <p className="text-xl font-bold text-orange-500">{sections.break_even_day?.value} Days</p>
                <p className="text-[10px] text-muted-foreground uppercase font-medium">Post-Release Target</p>
              </div>
            </div>

            <Separator className="my-6" />

            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="flex items-center font-medium">
                  <BarChart3 className="h-4 w-4 mr-2 text-blue-500" />
                  Market Position (Genre: {movie.genre || "N/A"})
                </span>
                <span className="text-muted-foreground">{insights?.revenue_percentile_in_genre}th Percentile</span>
              </div>
              <div className="relative h-10 w-full bg-muted rounded-full overflow-hidden flex items-center px-4">
                <div
                  className="absolute left-0 top-0 h-full bg-primary/20 border-r-2 border-primary transition-all duration-1000"
                  style={{ width: `${insights?.revenue_percentile_in_genre || 0}%` }}
                />
                <div className="relative w-full flex justify-between text-[10px] font-bold text-muted-foreground z-10">
                  <span className="uppercase">Underperformer</span>
                  <span className="uppercase">Average</span>
                  <span className="uppercase">Blockbuster</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Global Interest */}
        <Card className="border-primary/10 shadow-md">
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <Globe className="h-5 w-5 mr-2 text-blue-400" />
              Regional Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {sections.all_regions?.value?.map((reg: any, idx: number) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{reg.region}</span>
                  <span className="text-muted-foreground italic font-mono">{formatCurrency(reg.estimated_revenue)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Progress value={reg.interest_index} className="h-1.5 flex-1" />
                  <span className="text-[10px] font-bold w-6 text-right">{Math.round(reg.interest_index)}%</span>
                </div>
              </div>
            ))}
            <div className="mt-4 p-3 bg-muted/50 rounded-lg text-xs leading-relaxed text-muted-foreground italic border-l-2 border-primary/30">
              {sections.all_regions?.methodology}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Audience Sentiment & Buzz */}
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center">
              <MessageSquare className="h-5 w-5 mr-2 text-purple-500" />
              Sentiment Analysis & Buzz
            </CardTitle>
            <CardDescription>Aggregated feedback from Reddit & OMDb</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-full border-4 border-primary/20 flex items-center justify-center relative">
                  <span className="text-xl font-black">{sections.engagement_score?.value}</span>
                  <div
                    className="absolute inset-0 rounded-full border-4 border-t-primary border-r-transparent border-b-transparent border-l-transparent animate-spin-slow"
                    style={{ animationDuration: '3s' }}
                  />
                </div>
                <div>
                  <p className="text-sm font-bold uppercase tracking-tighter text-muted-foreground">Engagement Index</p>
                  <p className="text-lg font-bold">
                    {sections.engagement_score?.value >= 75 ? "Viral Breakout" :
                      sections.engagement_score?.value >= 40 ? "Steady Growth" : "Niche Interest"}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <Badge className="bg-purple-500/10 text-purple-600 hover:bg-purple-500/20 border-purple-500/20">
                  {report.diagnostics?.reddit_sentiment || "Neutral"} Buzz
                </Badge>
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-muted/30 rounded-xl">
                <h4 className="text-xs font-bold uppercase text-muted-foreground mb-2">Live Critiques (TMDb/OMDb)</h4>
                <div className="flex flex-wrap gap-2">
                  {sections.omdb_ratings?.value && typeof sections.omdb_ratings.value === 'object' &&
                    Object.entries(sections.omdb_ratings.value).map(([src, val]: [string, any]) => (
                      <Badge key={src} variant="secondary" className="px-2 py-0.5 text-[10px]">
                        {src.toUpperCase()}: {val}
                      </Badge>
                    ))
                  }
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase text-muted-foreground flex items-center">
                  <Users className="h-3 w-3 mr-1" /> Trending Trailers
                </h4>
                <div className="flex justify-between items-center text-sm p-3 border rounded-lg bg-card/50">
                  <span className="flex items-center">
                    Official Trailer Views
                    <ExternalLink className="h-3 w-3 ml-1 text-muted-foreground cursor-pointer" />
                  </span>
                  <span className="font-mono font-bold text-primary">{(sections.trailer_views?.value || 0).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Strategic Next Steps */}
        <Card className="border-primary/10 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Award className="h-5 w-5 mr-2 text-yellow-500" />
              Strategic Optimization
            </CardTitle>
            <CardDescription>Recommended actions based on current metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {sections.marketing_suggestions?.value?.slice(0, 4).map((s: string, i: number) => (
                <div key={i} className="flex gap-3 p-3 rounded-lg border bg-blue-50/50 dark:bg-blue-900/10 border-blue-200/50 dark:border-blue-900/30">
                  <div className="h-6 w-6 rounded-full bg-blue-500 flex items-center justify-center text-white text-[10px] font-bold shrink-0">
                    {i + 1}
                  </div>
                  <p className="text-xs leading-tight font-medium">{s}</p>
                </div>
              ))}
            </div>

            <div className="mt-4 space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Sequel Potential</span>
                <span className="font-bold">{sections.sequel_probability?.value}%</span>
              </div>
              <Progress value={sections.sequel_probability?.value} className="h-1 bg-muted" />

              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">IP Remake Feasibility</span>
                <span className="font-bold">{sections.remake_feasibility?.value}%</span>
              </div>
              <Progress value={sections.remake_feasibility?.value} className="h-1 bg-muted" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Persistence Controls */}
      <Card className="border-2 border-primary/20 bg-primary/5 shadow-xl">
        <CardHeader>
          <CardTitle className="flex items-center text-2xl font-black">
            <Save className="h-6 w-6 mr-3 text-primary" />
            Post-Release Finalization
          </CardTitle>
          <CardDescription>Archive production learnings and finalize the project metadata</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div>
                <label className="text-sm font-bold uppercase text-muted-foreground block mb-2">Audience Response Scorecard</label>
                <div className="flex gap-2">
                  {(['WEAK', 'MODERATE', 'STRONG'] as const).map((r) => (
                    <Button
                      key={r}
                      variant={selectedResponse === r ? 'default' : 'outline'}
                      className="flex-1 text-xs font-bold"
                      onClick={() => setSelectedResponse(r)}
                    >
                      {r === 'WEAK' ? 'Underperformed' : r === 'MODERATE' ? 'Met Expectation' : 'Exceeded Target'}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-muted/40 rounded-xl space-y-2 border border-dashed border-primary/20">
                <h4 className="text-xs font-bold uppercase text-primary flex items-center">
                  <CheckCircle2 className="h-4 w-4 mr-2" /> Monetization Strategy Locked
                </h4>
                <ul className="text-[10px] space-y-1 text-muted-foreground list-disc list-inside">
                  {sections.marketing_suggestions?.value?.map((s: string, i: number) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-bold uppercase text-muted-foreground block">Production Learning Summary</label>
              <textarea
                className="w-full min-h-[120px] bg-background border-2 border-muted focus:border-primary rounded-xl p-4 text-sm resize-none outline-none transition-all"
                placeholder="What did we learn from this production? (e.g., budget efficiency, talent impact, genre fit...)"
                value={learningSummary}
                onChange={(e) => setLearningSummary(e.target.value)}
              />
              <p className="text-[10px] text-muted-foreground italic">
                This summary will be indexed by the AI Assistant for future project planning insights.
              </p>
            </div>
          </div>

          <Separator />

          <div className="flex justify-between items-center bg-card p-4 rounded-2xl border">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500/10 rounded-full">
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              </div>
              <div>
                <h4 className="text-sm font-bold">Project Completion Status</h4>
                <p className="text-[10px] text-muted-foreground uppercase font-black tracking-widest">Phase 8 Ready for Finalization</p>
              </div>
            </div>
            <Button
              size="lg"
              className="px-8 font-black uppercase tracking-tighter shadow-lg shadow-primary/20"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
              {saving ? 'Processing...' : 'Finalize & Archive Project'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="mt-8 flex justify-center pb-12">
        <div className="flex items-center gap-6 text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">
          <span className="flex items-center"><Search className="h-3 w-3 mr-1" /> Data Source: Kaggle (BoxOffice)</span>
          <span>•</span>
          <span className="flex items-center"><Search className="h-3 w-3 mr-1" /> Engine: TMDb Global Index</span>
          <span>•</span>
          <span className="flex items-center"><Search className="h-3 w-3 mr-1" /> Social: Reddit Sentiment V1</span>
        </div>
      </div>
    </div>
  );
}
