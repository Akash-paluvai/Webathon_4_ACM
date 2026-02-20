import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Separator } from '@/components/ui/separator';
import {
  ArrowLeft, TrendingUp, TrendingDown, Globe2, Tv, BarChart3,
  Handshake, Zap, Shield, Target, Sparkles, Loader2, AlertCircle,
  ChevronRight, Gauge, Star, Download, Languages, Activity, PieChart
} from 'lucide-react';
import { getPhase6Analysis } from '@/api';

// Leaflet imports
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// ── Types ────────────────────────────────────────────────────

interface SignalData {
  region: string; lat?: number; lon?: number;
  youtube: number; twitter: number; trends: number;
  imdb: number; spotify: number; sentiment: number; RIS: number;
  engagement_velocity: number; trend_direction?: string; source?: string;
}

interface RegionScore {
  region: string; lat?: number; lon?: number;
  interest_score: number; normalized_score: number; tier: string;
  youtube?: number; twitter?: number; trends?: number; imdb?: number;
  spotify?: number; sentiment?: number; engagement_velocity?: number;
  trend_direction?: string; source?: string;
}

interface PlatformScore {
  platform: string; fit_score: number; confidence: [number, number]; reasoning: string[];
}

interface DealTerms {
  platform: string; minimum_guarantee_range: [number, number];
  revenue_share_pct: number; exclusivity_window_months: number; recommended_strategy: string;
}

interface LeverageBreakdown {
  platform_fit_contribution: number; hype_momentum_contribution: number;
  regional_dominance_contribution: number; dubbing_expansion_contribution: number;
}

interface LeverageResponse {
  leverage_score: number; level: string; strategy_hint: string; breakdown: LeverageBreakdown;
}

interface DubbingRecommendation {
  target_language: string; priority: string; estimated_roi_uplift: number; rationale: string;
}

interface DealBenchmark {
  platform: string; avg_advance_pct: number; avg_rev_share: number;
  min_guarantee_usd_k: number; exclusive_window_days: number; sample_count: number;
}

interface Phase6Data {
  project_id: number;
  platform_fit: {
    project_id: number; rankings: PlatformScore[];
    recommended_platform: string; recommended_score: number; distribution_model: string;
  };
  regional_hype: {
    project_id: number; regions: RegionScore[]; signals: SignalData[];
    top_region: string; hype_summary: string;
  };
  dubbing: {
    project_id: number; needs_dubbing: boolean;
    recommendations: DubbingRecommendation[]; estimated_total_cost_tier: string;
  };
  deal: {
    project_id: number; negotiation_leverage: string; leverage_score: number;
    leverage_detail: LeverageResponse; deal_options: DealTerms[];
    benchmarks?: DealBenchmark[];
  };
  leverage: LeverageResponse;
  release_mode: string;
  release_probabilities?: Record<string, number>;
  competition?: { cdi: number; genre_density: number; language_density: number; budget_crowd: number; same_genre_count: number; total_competitors: number };
  overall_readiness_score: number;
  summary: string;
}

// ── Helpers ──────────────────────────────────────────────────

function tierColor(tier: string): string {
  return { very_high: 'bg-emerald-500', high: 'bg-green-500', medium: 'bg-amber-500', low: 'bg-orange-500', very_low: 'bg-red-500' }[tier] || 'bg-gray-400';
}
function tierBadge(tier: string): string {
  return { very_high: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30', high: 'bg-green-500/15 text-green-700 border-green-500/30', medium: 'bg-amber-500/15 text-amber-700 border-amber-500/30', low: 'bg-orange-500/15 text-orange-700 border-orange-500/30', very_low: 'bg-red-500/15 text-red-700 border-red-500/30' }[tier] || 'bg-gray-100 text-gray-600';
}
function levColor(level: string): string {
  return { VERY_HIGH: 'text-emerald-600', HIGH: 'text-green-600', MODERATE: 'text-amber-600', LOW: 'text-orange-600', VERY_LOW: 'text-red-600' }[level] || 'text-gray-600';
}
function levGradient(s: number): string {
  if (s >= 0.7) return 'from-emerald-500 to-green-400';
  if (s >= 0.5) return 'from-green-500 to-amber-400';
  if (s >= 0.3) return 'from-amber-500 to-orange-400';
  return 'from-orange-500 to-red-400';
}
const pct = (n: number) => `${Math.round(n * 100)}%`;

function risToColor(ris: number): string {
  if (ris >= 0.7) return '#10b981';
  if (ris >= 0.5) return '#f59e0b';
  if (ris >= 0.3) return '#f97316';
  return '#ef4444';
}

function SignalBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-16 text-muted-foreground truncate">{label}</span>
      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-700 ${color}`} style={{ width: `${Math.round(value * 100)}%` }} />
      </div>
      <span className="w-9 text-right font-mono text-muted-foreground">{pct(value)}</span>
    </div>
  );
}

// ── Leaflet Heatmap ──────────────────────────────────────────

function GeoHeatmap({ signals }: { signals: SignalData[] }) {
  const validSignals = useMemo(
    () => signals.filter(s => s.lat && s.lon && s.lat !== 0 && s.lon !== 0),
    [signals]
  );

  if (validSignals.length === 0) return null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Globe2 className="h-5 w-5 text-blue-500" />
          <CardTitle className="text-lg">Live Hype Map</CardTitle>
          <Badge variant="outline" className="text-[10px] ml-auto">
            {validSignals.filter(s => s.source === 'live').length > 0 ? '🟢 Live Data' : '🔵 Heuristic'}
          </Badge>
        </div>
        <CardDescription>Real-time audience signals — bubble size = RIS intensity</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-xl overflow-hidden border" style={{ height: 420 }}>
          <MapContainer
            center={[20, 0]}
            zoom={2}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={false}
            zoomControl={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {validSignals.map((sig) => {
              const radius = Math.max(12, sig.RIS * 45);
              const color = risToColor(sig.RIS);
              return (
                <CircleMarker
                  key={sig.region}
                  center={[sig.lat!, sig.lon!]}
                  radius={radius}
                  pathOptions={{
                    fillColor: color,
                    color: color,
                    weight: 2,
                    opacity: 0.8,
                    fillOpacity: 0.35,
                  }}
                >
                  <Popup>
                    <div className="text-xs space-y-1 min-w-[180px]">
                      <div className="font-bold text-sm flex items-center gap-1">
                        {sig.region}
                        {sig.trend_direction === 'up'
                          ? <span className="text-emerald-600">↑</span>
                          : <span className="text-red-500">↓</span>
                        }
                      </div>
                      <div className="font-semibold" style={{ color }}>RIS: {pct(sig.RIS)}</div>
                      <hr className="my-1" />
                      <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
                        <span className="text-gray-500">YouTube</span><span className="font-medium">{pct(sig.youtube)}</span>
                        <span className="text-gray-500">Twitter</span><span className="font-medium">{pct(sig.twitter)}</span>
                        <span className="text-gray-500">Trends</span><span className="font-medium">{pct(sig.trends)}</span>
                        <span className="text-gray-500">Sentiment</span><span className="font-medium">{pct(sig.sentiment)}</span>
                      </div>
                      {sig.source && (
                        <div className="text-[10px] text-gray-400 mt-1">Source: {sig.source}</div>
                      )}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Regional Cards ───────────────────────────────────────────

function RegionalCards({ regions, signals }: { regions: RegionScore[]; signals: SignalData[] }) {
  const sigMap = Object.fromEntries(signals.map(s => [s.region, s]));
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-purple-500" />
          <CardTitle className="text-lg">Regional Signal Cards</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {regions.map((r) => {
            const sig = sigMap[r.region];
            const vel = sig?.engagement_velocity ?? 0;
            const up = (sig?.trend_direction ?? (vel > 0.4 ? 'up' : 'down')) === 'up';
            const Icon = up ? TrendingUp : TrendingDown;
            return (
              <TooltipProvider key={r.region} delayDuration={100}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="relative rounded-xl border bg-card p-3.5 cursor-pointer hover:shadow-md hover:border-primary/30 transition-all duration-200 hover:-translate-y-0.5">
                      <div className="absolute top-0 left-0 right-0 h-1 rounded-t-xl overflow-hidden">
                        <div className={`h-full ${tierColor(r.tier)}`} style={{ width: `${Math.round(r.normalized_score * 100)}%` }} />
                      </div>
                      <div className="flex items-start justify-between mt-1">
                        <div>
                          <h4 className="font-semibold text-sm">{r.region}</h4>
                          <div className="flex items-center gap-1.5 mt-1">
                            <span className={`inline-flex items-center gap-0.5 text-xs font-medium px-1.5 py-0.5 rounded-md border ${tierBadge(r.tier)}`}>{r.tier.replace('_', ' ')}</span>
                            <Icon className={`h-3 w-3 ${up ? 'text-emerald-500' : 'text-red-400'}`} />
                            {sig?.source === 'live' && <span className="text-[8px] text-emerald-600 font-bold">LIVE</span>}
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-xl font-bold tabular-nums">{pct(r.interest_score)}</span>
                          <p className="text-[10px] text-muted-foreground">RIS</p>
                        </div>
                      </div>
                      <div className="mt-2.5 grid grid-cols-5 gap-0.5">
                        {['youtube', 'twitter', 'trends', 'imdb', 'spotify'].map((k) => (
                          <div key={k} className="h-1 rounded-full bg-muted overflow-hidden">
                            <div className="h-full bg-blue-500/60 rounded-full" style={{ width: `${Math.round(((r as any)[k] ?? (sig as any)?.[k] ?? 0) * 100)}%` }} />
                          </div>
                        ))}
                      </div>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="bottom" className="w-56 p-3">
                    <p className="font-semibold text-sm mb-2">{r.region} — Signal Breakdown</p>
                    <div className="space-y-1.5">
                      <SignalBar label="YouTube" value={sig?.youtube ?? 0} color="bg-red-500" />
                      <SignalBar label="Twitter" value={sig?.twitter ?? 0} color="bg-sky-500" />
                      <SignalBar label="Trends" value={sig?.trends ?? 0} color="bg-blue-500" />
                      <SignalBar label="IMDb" value={sig?.imdb ?? 0} color="bg-amber-500" />
                      <SignalBar label="Spotify" value={sig?.spotify ?? 0} color="bg-green-500" />
                      <Separator className="my-1" />
                      <div className="flex justify-between text-xs"><span className="text-muted-foreground">Sentiment</span><span className="font-medium">{pct(sig?.sentiment ?? 0)}</span></div>
                      <div className="flex justify-between text-xs"><span className="text-muted-foreground">Velocity</span><span className={`font-medium ${up ? 'text-emerald-600' : 'text-red-500'}`}>{up ? '↑' : '↓'} {pct(vel)}</span></div>
                    </div>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Platform Fit Cards ───────────────────────────────────────

function PlatformFitCards({ rankings, rec }: { rankings: PlatformScore[]; rec: string }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2"><Tv className="h-5 w-5 text-purple-500" /><CardTitle className="text-lg">Platform Fit Rankings</CardTitle></div>
        <CardDescription>Feature-driven scoring with confidence intervals and actionable insights</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rankings.map((p, idx) => {
            const isTop = p.platform === rec;
            const [ciL, ciH] = p.confidence;
            const reach = Math.round(p.fit_score * 120);
            return (
              <div key={p.platform} className={`relative rounded-xl border p-4 transition-all duration-200 hover:shadow-md ${isTop ? 'border-primary/40 bg-gradient-to-br from-primary/5 to-primary/10 ring-1 ring-primary/20' : 'bg-card hover:border-primary/20'}`}>
                {isTop && <div className="absolute -top-2.5 left-3"><span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-primary text-primary-foreground uppercase tracking-wider"><Star className="h-2.5 w-2.5" /> Recommended</span></div>}
                <div className="flex items-start justify-between mb-3">
                  <h4 className={`font-bold text-sm ${isTop ? 'text-primary' : ''}`}>#{idx + 1} {p.platform}</h4>
                  <div className="text-right"><span className="text-2xl font-bold tabular-nums">{pct(p.fit_score)}</span><p className="text-[10px] text-muted-foreground">fit score</p></div>
                </div>
                <div className="mb-3">
                  <div className="flex justify-between text-[10px] text-muted-foreground mb-0.5"><span>Confidence</span><span>{pct(ciL)} – {pct(ciH)}</span></div>
                  <div className="relative h-2 bg-muted rounded-full overflow-hidden">
                    <div className="absolute h-full bg-blue-200 rounded-full" style={{ left: `${Math.round(ciL * 100)}%`, width: `${Math.round((ciH - ciL) * 100)}%` }} />
                    <div className="absolute h-full w-1.5 bg-blue-600 rounded-full -translate-x-1/2" style={{ left: `${Math.round(p.fit_score * 100)}%` }} />
                  </div>
                </div>
                <div className="mb-3 flex items-center gap-2 text-xs text-muted-foreground">
                  <Target className="h-3 w-3 shrink-0" />
                  <span>Est. reach: <strong className="text-foreground">{reach}M</strong> viewers</span>
                </div>
                <div className="space-y-1">
                  {p.reasoning.slice(0, 3).map((reason, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                      <ChevronRight className="h-3 w-3 shrink-0 mt-0.5 text-primary/60" /><span>{reason}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Release Mode Probabilities ───────────────────────────────

function ReleaseModeProbabilities({ probs, bestMode }: { probs: Record<string, number>; bestMode: string }) {
  const modeLabels: Record<string, string> = { theatre: 'Theatre', ott: 'OTT', hybrid: 'Hybrid', festival_circuit: 'Festival' };
  const modeColors: Record<string, string> = { theatre: 'bg-purple-500', ott: 'bg-blue-500', hybrid: 'bg-cyan-500', festival_circuit: 'bg-amber-500' };
  const sorted = Object.entries(probs).sort((a, b) => b[1] - a[1]);
  return (
    <Card>
      <CardHeader className="pb-2"><div className="flex items-center gap-2"><PieChart className="h-5 w-5 text-cyan-500" /><CardTitle className="text-lg">Release Mode</CardTitle></div></CardHeader>
      <CardContent>
        <div className="space-y-2">
          {sorted.map(([mode, prob]) => (
            <div key={mode} className="flex items-center gap-3">
              <span className={`text-xs font-medium w-16 ${mode === bestMode ? 'text-foreground font-bold' : 'text-muted-foreground'}`}>{modeLabels[mode] || mode}</span>
              <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-700 ${modeColors[mode] || 'bg-gray-400'} ${mode === bestMode ? 'opacity-100' : 'opacity-50'}`} style={{ width: `${Math.round(prob * 100)}%` }} />
              </div>
              <span className={`text-xs font-mono w-10 text-right ${mode === bestMode ? 'font-bold' : 'text-muted-foreground'}`}>{pct(prob)}</span>
              {mode === bestMode && <Badge variant="outline" className="text-[10px] px-1.5 py-0">Best</Badge>}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Dubbing Panel ────────────────────────────────────────────

function DubbingPanel({ dubbing }: { dubbing: Phase6Data['dubbing'] }) {
  if (!dubbing.needs_dubbing || dubbing.recommendations.length === 0) return null;
  const maxUplift = Math.max(...dubbing.recommendations.map(r => r.estimated_roi_uplift), 1);
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2"><Languages className="h-5 w-5 text-cyan-500" /><CardTitle className="text-lg">Dubbing Recommendations</CardTitle></div>
        <CardDescription>Language demand analysis — cost tier: <strong className="capitalize">{dubbing.estimated_total_cost_tier}</strong></CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {dubbing.recommendations.map((rec) => {
            const barWidth = Math.round((rec.estimated_roi_uplift / maxUplift) * 100);
            return (
              <div key={rec.target_language} className="rounded-lg border p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm capitalize">{rec.target_language}</span>
                    <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${rec.priority === 'high' ? 'bg-emerald-500/15 text-emerald-700' : rec.priority === 'medium' ? 'bg-amber-500/15 text-amber-700' : 'bg-gray-100 text-gray-600'}`}>{rec.priority}</span>
                  </div>
                  <span className="text-sm font-bold text-primary">+{rec.estimated_roi_uplift}%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden mb-1.5">
                  <div className={`h-full rounded-full transition-all duration-700 ${rec.priority === 'high' ? 'bg-emerald-500' : 'bg-amber-400'}`} style={{ width: `${barWidth}%` }} />
                </div>
                <p className="text-xs text-muted-foreground">{rec.rationale}</p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Competition Density ──────────────────────────────────────

function CompetitionCard({ comp }: { comp: Phase6Data['competition'] }) {
  if (!comp) return null;
  return (
    <Card>
      <CardHeader className="pb-2"><div className="flex items-center gap-2"><Activity className="h-5 w-5 text-red-500" /><CardTitle className="text-lg">Competition Density</CardTitle></div></CardHeader>
      <CardContent>
        <div className="flex items-center gap-4 mb-3">
          <div className="text-center">
            <span className="text-3xl font-bold tabular-nums">{pct(comp.cdi)}</span>
            <p className="text-[10px] text-muted-foreground">CDI</p>
          </div>
          <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
            <div className={`h-full rounded-full bg-gradient-to-r ${comp.cdi > 0.6 ? 'from-red-500 to-orange-400' : comp.cdi > 0.3 ? 'from-amber-500 to-yellow-400' : 'from-green-500 to-emerald-400'}`} style={{ width: `${Math.round(comp.cdi * 100)}%` }} />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="rounded-lg bg-muted/50 p-2"><p className="text-muted-foreground">Genre</p><p className="font-semibold">{pct(comp.genre_density)}</p></div>
          <div className="rounded-lg bg-muted/50 p-2"><p className="text-muted-foreground">Language</p><p className="font-semibold">{pct(comp.language_density)}</p></div>
          <div className="rounded-lg bg-muted/50 p-2"><p className="text-muted-foreground">Competitors</p><p className="font-semibold">{comp.total_competitors}</p></div>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Negotiation Dashboard ────────────────────────────────────

function NegotiationDashboard({ leverage, dealOptions, negotiationLeverage, benchmarks }: {
  leverage: LeverageResponse; dealOptions: DealTerms[]; negotiationLeverage: string; benchmarks?: DealBenchmark[];
}) {
  const benchMap = Object.fromEntries((benchmarks || []).map(b => [b.platform, b]));
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3"><div className="flex items-center gap-2"><Gauge className="h-5 w-5 text-amber-500" /><CardTitle className="text-lg">Negotiation Leverage</CardTitle></div></CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className={`text-3xl font-bold ${levColor(leverage.level)}`}>{leverage.level}</span>
                <span className="text-4xl font-bold tabular-nums">{pct(leverage.leverage_score)}</span>
              </div>
              <div className="relative h-4 bg-muted rounded-full overflow-hidden mb-4">
                <div className={`h-full rounded-full bg-gradient-to-r ${levGradient(leverage.leverage_score)} transition-all duration-1000`} style={{ width: `${Math.round(leverage.leverage_score * 100)}%` }} />
                {[0.25, 0.5, 0.75].map(t => <div key={t} className="absolute top-0 h-full w-px bg-background/50" style={{ left: `${t * 100}%` }} />)}
              </div>
              <div className="space-y-2">
                {[
                  { label: 'Platform Fit', value: leverage.breakdown.platform_fit_contribution, w: '40%', icon: Tv },
                  { label: 'Hype Momentum', value: leverage.breakdown.hype_momentum_contribution, w: '25%', icon: Zap },
                  { label: 'Regional Dom.', value: leverage.breakdown.regional_dominance_contribution, w: '20%', icon: Globe2 },
                  { label: 'Dubbing Exp.', value: leverage.breakdown.dubbing_expansion_contribution, w: '15%', icon: Languages },
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-2 text-xs">
                    <item.icon className="h-3 w-3 text-muted-foreground shrink-0" />
                    <span className="w-24 text-muted-foreground">{item.label}</span>
                    <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-primary/50 rounded-full" style={{ width: `${Math.round((item.value / leverage.leverage_score) * 100)}%` }} />
                    </div>
                    <span className="w-10 text-right font-mono text-muted-foreground">{item.value.toFixed(3)}</span>
                    <span className="w-7 text-right text-muted-foreground/50 text-[10px]">{item.w}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex flex-col justify-between">
              <div className="rounded-xl bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20 p-4">
                <div className="flex items-center gap-2 mb-2"><Sparkles className="h-4 w-4 text-primary" /><span className="text-sm font-semibold text-primary">Strategy Recommendation</span></div>
                <p className="text-sm leading-relaxed">{leverage.strategy_hint}</p>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-lg bg-muted/50 p-2"><Shield className="h-4 w-4 mx-auto mb-1 text-muted-foreground" /><p className="text-[10px] text-muted-foreground">Leverage</p><p className="text-xs font-semibold capitalize">{negotiationLeverage}</p></div>
                <div className="rounded-lg bg-muted/50 p-2"><Target className="h-4 w-4 mx-auto mb-1 text-muted-foreground" /><p className="text-[10px] text-muted-foreground">Score</p><p className="text-xs font-semibold">{pct(leverage.leverage_score)}</p></div>
                <div className="rounded-lg bg-muted/50 p-2"><BarChart3 className="h-4 w-4 mx-auto mb-1 text-muted-foreground" /><p className="text-[10px] text-muted-foreground">Deals</p><p className="text-xs font-semibold">{dealOptions.length}</p></div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2"><Handshake className="h-5 w-5 text-green-500" /><CardTitle className="text-lg">Deal Terms vs Industry</CardTitle></div>
          <CardDescription>Your negotiated terms compared to industry benchmarks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b text-muted-foreground">
                  <th className="text-left py-2 pr-3 font-medium">Platform</th>
                  <th className="text-right py-2 px-2 font-medium">MG ($K)</th>
                  <th className="text-right py-2 px-2 font-medium">Share %</th>
                  <th className="text-right py-2 px-2 font-medium">Excl.</th>
                  <th className="text-center py-2 px-2 font-medium">Leverage</th>
                  <th className="text-left py-2 pl-2 font-medium">Industry Benchmark</th>
                </tr>
              </thead>
              <tbody>
                {dealOptions.map((deal) => {
                  const bench = benchMap[deal.platform];
                  return (
                    <tr key={deal.platform} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="py-2.5 pr-3 font-semibold">{deal.platform}</td>
                      <td className="py-2.5 px-2 text-right tabular-nums">${deal.minimum_guarantee_range[0].toFixed(0)}–{deal.minimum_guarantee_range[1].toFixed(0)}</td>
                      <td className="py-2.5 px-2 text-right tabular-nums">{deal.revenue_share_pct.toFixed(1)}%</td>
                      <td className="py-2.5 px-2 text-right tabular-nums">{deal.exclusivity_window_months}mo</td>
                      <td className="py-2.5 px-2 text-center">
                        <span className={`inline-block w-2 h-2 rounded-full ${negotiationLeverage === 'strong' ? 'bg-emerald-500' : negotiationLeverage === 'moderate' ? 'bg-amber-500' : 'bg-red-500'}`} />
                      </td>
                      <td className="py-2.5 pl-2 text-muted-foreground">
                        {bench ? <span>MG ${bench.min_guarantee_usd_k}K · Share {bench.avg_rev_share}% · {bench.exclusive_window_days}d</span> : <span className="text-muted-foreground/50">—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────

export default function Phase6Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };
  const [data, setData] = useState<Phase6Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    setLoading(true); setError(null);
    getPhase6Analysis(Number(projectId))
      .then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [projectId]);

  const handleExportPitchPack = async () => {
    setExporting(true);
    try {
      const res = await fetch(`/phase6/pitch-pack?project_id=${projectId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      const pack = await res.json();
      const blob = new Blob([JSON.stringify(pack, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = `pitch-pack-project-${projectId}.json`; a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ }
    setExporting(false);
  };

  if (loading) return (
    <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center gap-3 text-muted-foreground">
      <Loader2 className="h-8 w-8 animate-spin" /><p className="text-sm">Running live signal analysis…</p>
    </div>
  );

  if (error || !data) return (
    <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center gap-3">
      <AlertCircle className="h-8 w-8 text-destructive" />
      <p className="text-sm text-destructive">{error || 'Failed to load analysis'}</p>
      <Button variant="outline" size="sm" onClick={() => window.location.reload()}>Retry</Button>
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex items-center justify-between mb-6">
        <Button variant="ghost" onClick={() => navigate({ to: '/projects/$projectId', params: { projectId } })}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to Project Overview
        </Button>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleExportPitchPack} disabled={exporting}>
            {exporting ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <Download className="h-3.5 w-3.5 mr-1.5" />}
            Export Pitch Pack
          </Button>
        </div>
      </div>

      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Phase 6: Distribution Strategy & Negotiation</h1>
        <p className="text-muted-foreground text-lg mb-4">{data.summary}</p>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div className="rounded-xl border bg-card p-3 text-center"><p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Release Mode</p><p className="text-lg font-bold capitalize">{data.release_mode.replace('_', ' ')}</p></div>
          <div className="rounded-xl border bg-card p-3 text-center"><p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Best Platform</p><p className="text-lg font-bold">{data.platform_fit.recommended_platform}</p></div>
          <div className="rounded-xl border bg-card p-3 text-center"><p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Top Market</p><p className="text-lg font-bold">{data.regional_hype.top_region}</p></div>
          <div className="rounded-xl border bg-card p-3 text-center"><p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Leverage</p><p className={`text-lg font-bold ${levColor(data.leverage.level)}`}>{data.leverage.level}</p></div>
          <div className="rounded-xl border bg-card p-3 text-center"><p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Readiness</p><p className="text-lg font-bold">{pct(data.overall_readiness_score)}</p></div>
        </div>
      </div>

      <Tabs defaultValue="map" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 h-10">
          <TabsTrigger value="map" className="flex items-center gap-1.5 text-xs"><Globe2 className="h-3.5 w-3.5" /> Live Map</TabsTrigger>
          <TabsTrigger value="regional" className="flex items-center gap-1.5 text-xs"><BarChart3 className="h-3.5 w-3.5" /> Signals</TabsTrigger>
          <TabsTrigger value="platform" className="flex items-center gap-1.5 text-xs"><Tv className="h-3.5 w-3.5" /> Platforms</TabsTrigger>
          <TabsTrigger value="deals" className="flex items-center gap-1.5 text-xs"><Handshake className="h-3.5 w-3.5" /> Negotiation</TabsTrigger>
          <TabsTrigger value="dubbing" className="flex items-center gap-1.5 text-xs"><Languages className="h-3.5 w-3.5" /> Dubbing</TabsTrigger>
        </TabsList>

        <TabsContent value="map" className="space-y-4">
          <GeoHeatmap signals={data.regional_hype.signals || []} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {data.release_probabilities && <ReleaseModeProbabilities probs={data.release_probabilities} bestMode={data.release_mode} />}
            {data.competition && <CompetitionCard comp={data.competition} />}
          </div>
        </TabsContent>

        <TabsContent value="regional">
          <RegionalCards regions={data.regional_hype.regions} signals={data.regional_hype.signals || []} />
        </TabsContent>

        <TabsContent value="platform">
          <PlatformFitCards rankings={data.platform_fit.rankings} rec={data.platform_fit.recommended_platform} />
        </TabsContent>

        <TabsContent value="deals">
          <NegotiationDashboard leverage={data.leverage} dealOptions={data.deal.deal_options} negotiationLeverage={data.deal.negotiation_leverage} benchmarks={data.deal.benchmarks || []} />
        </TabsContent>

        <TabsContent value="dubbing" className="space-y-4">
          <DubbingPanel dubbing={data.dubbing} />
          {(!data.dubbing.needs_dubbing || data.dubbing.recommendations.length === 0) && (
            <Card><CardContent className="py-8 text-center text-muted-foreground"><Languages className="h-8 w-8 mx-auto mb-2 opacity-50" /><p>Dubbing not recommended for this project based on current audience signals.</p></CardContent></Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
