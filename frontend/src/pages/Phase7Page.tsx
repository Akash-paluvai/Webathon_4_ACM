import { useState, useEffect } from 'react';
import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import {
  ArrowLeft, Loader2, AlertCircle, Gauge, Eye, TrendingUp, Wallet,
  ShieldAlert, Target, Trophy, Ticket, AlertTriangle, Activity,
  BarChart3, Zap, ChevronRight, Sparkles, Flame, ArrowUpRight,
  ArrowRight, ArrowDownRight, Globe, Lock, Star, Brain,
} from 'lucide-react';
import { getPhase7Timeline, getPhase7Demand } from '@/api';

const pct = (n: number) => `${Math.round(n * 100)}%`;

function gradeColor(g: string) {
  return { 'A+': 'text-emerald-600', 'A': 'text-emerald-500', 'B+': 'text-green-500', 'B': 'text-green-600', 'C': 'text-amber-600', 'D': 'text-orange-600', 'F': 'text-red-600' }[g] || 'text-gray-600';
}
function riskBadge(r: string) {
  return { HIGH: 'bg-red-500/15 text-red-700', MODERATE: 'bg-amber-500/15 text-amber-700', LOW: 'bg-emerald-500/15 text-emerald-700', STABLE: 'bg-emerald-500/15 text-emerald-700', CRITICAL: 'bg-red-700/20 text-red-800' }[r] || 'bg-gray-100 text-gray-600';
}

// ── Discoverability Gauge ─────────────────────────────────
function DiscoverabilityGauge({ disco, confidence }: { disco: any; confidence: any }) {
  const score = disco.score;
  const angle = -90 + score * 180;
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><Gauge className="h-5 w-5 text-blue-500" /><CardTitle>Discoverability Score</CardTitle></div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-6">
          <div className="relative w-40 h-24 overflow-hidden">
            <svg viewBox="0 0 200 110" className="w-full h-full">
              <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="hsl(var(--muted))" strokeWidth="14" strokeLinecap="round" />
              <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#gauge-grad)" strokeWidth="14" strokeLinecap="round" strokeDasharray={`${score * 251} 251`} />
              <defs><linearGradient id="gauge-grad"><stop offset="0%" stopColor="#ef4444" /><stop offset="40%" stopColor="#f59e0b" /><stop offset="70%" stopColor="#22c55e" /><stop offset="100%" stopColor="#10b981" /></linearGradient></defs>
              <line x1="100" y1="100" x2={100 + 60 * Math.cos((angle * Math.PI) / 180)} y2={100 + 60 * Math.sin((angle * Math.PI) / 180)} stroke="currentColor" strokeWidth="2" className="text-foreground" />
              <circle cx="100" cy="100" r="4" fill="currentColor" className="text-foreground" />
            </svg>
          </div>
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-bold tabular-nums">{pct(score)}</span>
              <span className={`text-2xl font-bold ${gradeColor(disco.grade)}`}>{disco.grade}</span>
            </div>
            <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
              <span>Confidence: <strong className="text-foreground">{pct(confidence.confidence)}</strong> ({confidence.reliability_grade})</span>
              <span>|</span>
              <span>Band: {pct(confidence.confidence_band.low)}–{pct(confidence.confidence_band.high)}</span>
            </div>
            <p className="text-[10px] text-muted-foreground mt-1">Worst case: {pct(confidence.worst_case_discoverability)}</p>
          </div>
        </div>
        <Separator className="my-3" />
        <p className="text-xs font-medium text-muted-foreground mb-2">Score Breakdown</p>
        <div className="space-y-1.5">
          {Object.entries(disco.breakdown).map(([k, v]: [string, any]) => {
            const isNeg = v < 0;
            const absV = Math.abs(v);
            return (
              <div key={k} className="flex items-center gap-2 text-xs">
                <span className="w-36 text-muted-foreground capitalize">{k.replace(/_/g, ' ')}</span>
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${isNeg ? 'bg-red-500' : 'bg-blue-500'}`} style={{ width: `${Math.min(100, absV * 500)}%` }} />
                </div>
                <span className={`w-12 text-right font-mono ${isNeg ? 'text-red-600' : ''}`}>{v > 0 ? '+' : ''}{(v * 100).toFixed(1)}</span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Visibility Risk Card ──────────────────────────────────
function VisibilityRiskCard({ risk }: { risk: any }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><Eye className="h-5 w-5 text-orange-500" /><CardTitle>Algorithm Visibility Risk</CardTitle></div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-3 mb-3">
          <Badge className={`text-sm px-3 py-1 ${riskBadge(risk.visibility_risk)}`}>{risk.visibility_risk}</Badge>
          <span className="text-2xl font-bold tabular-nums">{pct(risk.risk_score)}</span>
        </div>
        <div className="space-y-2 mb-3">
          <p className="text-xs font-medium text-muted-foreground">Causes</p>
          {risk.primary_causes.map((c: string, i: number) => (
            <div key={i} className="flex items-start gap-2 text-xs"><AlertTriangle className="h-3 w-3 text-amber-500 mt-0.5 shrink-0" /><span>{c}</span></div>
          ))}
        </div>
        <Separator className="my-2" />
        <p className="text-xs font-medium text-muted-foreground mb-1">Fixes</p>
        {risk.suggested_fix.map((f: string, i: number) => (
          <div key={i} className="flex items-start gap-2 text-xs text-emerald-700"><Zap className="h-3 w-3 mt-0.5 shrink-0" /><span>{f}</span></div>
        ))}
      </CardContent>
    </Card>
  );
}

// ── Momentum Curve ────────────────────────────────────────
function MomentumCard({ momentum }: { momentum: any }) {
  const maxVal = Math.max(...momentum.momentum_curve, 0.01);
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><TrendingUp className="h-5 w-5 text-purple-500" /><CardTitle>Momentum Forecast</CardTitle></div>
        <CardDescription>4-week pre-release hype trajectory</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-4 gap-2 mb-4" style={{ minHeight: 100 }}>
          {momentum.momentum_curve.map((val: number, i: number) => {
            const h = Math.round((val / maxVal) * 80) + 15;
            return (
              <div key={i} className="flex flex-col items-center justify-end gap-1">
                <span className="text-[10px] font-mono">{pct(val)}</span>
                <div className="w-full rounded-t bg-purple-500" style={{ height: h, opacity: 0.5 + val * 0.5 }} />
                <span className="text-[10px] text-muted-foreground">W{i + 1}</span>
              </div>
            );
          })}
        </div>
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="rounded-lg bg-purple-500/10 p-2"><p className="text-muted-foreground">Viral</p><p className="font-bold">{pct(momentum.viral_probability)}</p></div>
          <div className="rounded-lg bg-blue-500/10 p-2"><p className="text-muted-foreground">Organic</p><p className="font-bold">{pct(momentum.organic_growth)}</p></div>
          <div className="rounded-lg bg-amber-500/10 p-2"><p className="text-muted-foreground">Talent</p><p className="font-bold">{pct(momentum.talent_factor)}</p></div>
        </div>
        {momentum.suggestions.length > 0 && (
          <>
            <Separator className="my-3" />
            <p className="text-xs font-medium text-muted-foreground mb-1">Suggestions</p>
            {momentum.suggestions.map((s: string, i: number) => (
              <div key={i} className="flex items-start gap-2 text-xs mt-1"><ChevronRight className="h-3 w-3 text-blue-500 mt-0.5 shrink-0" /><span>{s}</span></div>
            ))}
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ── Budget Allocation ─────────────────────────────────────
function BudgetCard({ budget }: { budget: any }) {
  const colors = ['bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-purple-500', 'bg-pink-500'];
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><Wallet className="h-5 w-5 text-green-500" /><CardTitle>Budget Efficiency</CardTitle></div>
        <CardDescription>Optimal allocation for ₹{budget.total_budget_lakhs}L budget</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex h-4 rounded-full overflow-hidden mb-3">
          {budget.channel_details.map((ch: any, i: number) => (
            <div key={i} className={`${colors[i]} transition-all`} style={{ width: `${ch.allocation_pct * 100}%` }} title={`${ch.channel}: ${pct(ch.allocation_pct)}`} />
          ))}
        </div>
        <div className="space-y-2">
          {budget.channel_details.map((ch: any, i: number) => (
            <div key={i} className="flex items-center gap-2 text-xs">
              <span className={`w-2 h-2 rounded-full ${colors[i]}`} />
              <span className="w-28 font-medium">{ch.channel}</span>
              <span className="w-12 text-center font-mono">{pct(ch.allocation_pct)}</span>
              <span className="text-muted-foreground">₹{ch.budget_lakhs}L</span>
              <span className="ml-auto text-[10px] text-muted-foreground hidden sm:block">{ch.rationale.slice(0, 50)}</span>
            </div>
          ))}
        </div>
        <div className="mt-3 flex gap-3 text-center text-xs">
          <div className="flex-1 rounded-lg bg-emerald-500/10 p-2"><p className="text-muted-foreground">Reach Gain</p><p className="font-bold text-emerald-600">{pct(budget.expected_reach_gain)}</p></div>
          <div className="flex-1 rounded-lg bg-blue-500/10 p-2"><p className="text-muted-foreground">Efficiency</p><p className="font-bold text-blue-600">{pct(budget.efficiency_score)}</p></div>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Barriers Card ─────────────────────────────────────────
function BarriersCard({ barriers }: { barriers: any }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><ShieldAlert className="h-5 w-5 text-red-500" /><CardTitle>Discovery Barriers</CardTitle></div>
      </CardHeader>
      <CardContent>
        {barriers.barrier_details.map((b: any, i: number) => (
          <div key={i} className="mb-3 last:mb-0">
            <div className="flex items-center justify-between text-sm">
              <span className="font-semibold">{b.barrier}</span>
              <span className="text-xs font-mono text-red-600">{pct(b.severity)}</span>
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">{b.impact}</p>
            <div className="flex items-start gap-1 mt-1 text-[11px] text-emerald-700"><Zap className="h-3 w-3 shrink-0 mt-0.5" /><span>{b.fix}</span></div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ── Conversion Card ───────────────────────────────────────
function ConversionCard({ conversion }: { conversion: any }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><Target className="h-5 w-5 text-cyan-500" /><CardTitle>Audience Conversion</CardTitle></div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-3 text-center mb-3">
          <div className="rounded-xl bg-cyan-500/10 p-3"><p className="text-[10px] text-muted-foreground uppercase">Conversion</p><p className="text-2xl font-bold">{pct(conversion.conversion_probability)}</p></div>
          <div className="rounded-xl bg-blue-500/10 p-3"><p className="text-[10px] text-muted-foreground uppercase">Depth</p><p className="text-2xl font-bold">{pct(conversion.engagement_depth)}</p></div>
          <div className="rounded-xl bg-purple-500/10 p-3"><p className="text-[10px] text-muted-foreground uppercase">Word of Mouth</p><p className="text-2xl font-bold">{pct(conversion.word_of_mouth)}</p></div>
        </div>
        <div className="text-center"><Badge variant="outline" className="text-xs">{conversion.audience_quality}</Badge></div>
      </CardContent>
    </Card>
  );
}

// ── Festival Impact Card ──────────────────────────────────
function FestivalCard({ festival }: { festival: any }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><Trophy className="h-5 w-5 text-amber-500" /><CardTitle>Festival & Award Impact</CardTitle></div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-2 text-center mb-3">
          <div className="rounded-lg bg-amber-500/10 p-2"><p className="text-[10px] text-muted-foreground">Best Festival</p><p className="font-bold text-sm">{festival.best_festival || '—'}</p></div>
          <div className="rounded-lg bg-amber-500/10 p-2"><p className="text-[10px] text-muted-foreground">Acceptance</p><p className="font-bold text-sm">{pct(festival.festival_probability)}</p></div>
          <div className="rounded-lg bg-amber-500/10 p-2"><p className="text-[10px] text-muted-foreground">Boost</p><p className="font-bold text-sm">{pct(festival.discoverability_boost)}</p></div>
        </div>
        <div className="space-y-1.5">
          {festival.festival_recommendations?.slice(0, 4).map((f: any, i: number) => (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="font-medium">{f.festival}</span>
              <div className="flex items-center gap-2">
                {f.genre_match && <Badge className="bg-emerald-500/15 text-emerald-700 text-[9px]">genre ✓</Badge>}
                <span className="font-mono">{pct(f.acceptance_probability)}</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Ticket Pricing Card ───────────────────────────────────
function TicketCard({ pricing }: { pricing: any }) {
  if (!pricing.recommended_price) {
    return (
      <Card>
        <CardHeader className="pb-2"><div className="flex items-center gap-2"><Ticket className="h-5 w-5 text-pink-500" /><CardTitle>Ticket Pricing</CardTitle></div></CardHeader>
        <CardContent><p className="text-sm text-muted-foreground">{pricing.strategy}</p></CardContent>
      </Card>
    );
  }
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><Ticket className="h-5 w-5 text-pink-500" /><CardTitle>Ticket Pricing</CardTitle></div>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-4xl font-bold">₹{pricing.recommended_price}</span>
          <span className="text-sm text-muted-foreground">recommended</span>
        </div>
        <p className="text-xs text-muted-foreground mb-3">{pricing.strategy}</p>
        <div className="grid grid-cols-3 gap-2 text-center text-xs mb-3">
          <div className="rounded-lg bg-muted/50 p-2"><p className="text-muted-foreground">Elasticity</p><p className="font-bold">{pricing.elasticity}</p></div>
          <div className="rounded-lg bg-emerald-500/10 p-2"><p className="text-muted-foreground">Revenue ↑</p><p className="font-bold text-emerald-600">{pct(pricing.revenue_gain)}</p></div>
          <div className="rounded-lg bg-red-500/10 p-2"><p className="text-muted-foreground">Reach ↓</p><p className="font-bold text-red-600">{pct(pricing.reach_loss)}</p></div>
        </div>
        {pricing.festival_pricing && (
          <div className="text-xs text-muted-foreground">Festival premium: ₹{pricing.festival_pricing.festival_premium}</div>
        )}
      </CardContent>
    </Card>
  );
}

// ── Market Shock Card ─────────────────────────────────────
function ShocksCard({ shocks }: { shocks: any }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-red-500" /><CardTitle>Market Shocks</CardTitle></div>
      </CardHeader>
      <CardContent>
        <Badge className={`mb-3 ${riskBadge(shocks.overall_risk)}`}>{shocks.overall_risk}</Badge>
        {shocks.shock_list.length === 0 ? (
          <p className="text-sm text-muted-foreground">No market shocks detected — conditions stable.</p>
        ) : (
          <div className="space-y-2">
            {shocks.shock_list.map((s: any, i: number) => (
              <div key={i} className="rounded-lg border p-2.5">
                <div className="flex items-center justify-between text-xs mb-1">
                  <Badge className={riskBadge(s.severity)} variant="outline">{s.type.replace(/_/g, ' ')}</Badge>
                  <span className="font-mono text-red-600">{(s.impact_on_discoverability * 100).toFixed(1)}%</span>
                </div>
                <p className="text-[11px] text-muted-foreground">{s.description}</p>
              </div>
            ))}
          </div>
        )}
        {shocks.auto_adjustments.length > 0 && (
          <>
            <Separator className="my-3" />
            <p className="text-xs font-medium text-muted-foreground mb-1">Auto-Adjustments</p>
            {shocks.auto_adjustments.map((a: string, i: number) => (
              <div key={i} className="flex items-start gap-2 text-xs mt-1"><Zap className="h-3 w-3 text-emerald-500 mt-0.5 shrink-0" /><span>{a}</span></div>
            ))}
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ── Recovery Card ─────────────────────────────────────────
function RecoveryCard({ recovery }: { recovery: any }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2"><Activity className="h-5 w-5 text-blue-500" /><CardTitle>Recovery Plan</CardTitle></div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2 mb-3">
          <Badge className={riskBadge(recovery.severity)}>{recovery.severity}</Badge>
          {recovery.recovery_trigger && <span className="text-xs text-red-600 font-medium">⚠ Recovery triggered</span>}
          <span className="ml-auto text-xs text-emerald-600 font-medium">+{pct(recovery.expected_recovery_gain)} potential</span>
        </div>
        <div className="space-y-2">
          {recovery.actions.map((a: any, i: number) => (
            <div key={i} className="rounded-lg border p-2.5 flex items-start gap-2">
              <Badge className={riskBadge(a.priority)} variant="outline">{a.priority}</Badge>
              <div className="flex-1">
                <p className="text-xs font-medium">{a.action}</p>
                <div className="flex gap-3 mt-1 text-[10px] text-muted-foreground">
                  <span>Gain: +{pct(a.expected_gain)}</span>
                  <span>Cost: {a.cost}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// ── DSI Gauge Component ───────────────────────────────────
function DSIGauge({ dsi }: { dsi: any }) {
  const score = dsi?.score ?? 50;
  const grade = dsi?.grade ?? 'C';
  const pctVal = score / 100;
  const circumference = 2 * Math.PI * 52;
  const dashOffset = circumference * (1 - pctVal * 0.75); // 270deg arc
  const color = score >= 75 ? '#22c55e' : score >= 55 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#ef4444';

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2"><Brain className="h-5 w-5" /> Demand Strength Index</CardTitle>
        <CardDescription>Pre-release audience demand score</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-4">
        <div className="relative w-36 h-36">
          <svg viewBox="0 0 120 120" className="w-full h-full -rotate-[135deg]">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" strokeWidth="10" strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} />
            <circle cx="60" cy="60" r="52" fill="none" stroke={color} strokeWidth="10" strokeLinecap="round" strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} strokeDashoffset={dashOffset} className="transition-all duration-1000" />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold" style={{ color }}>{score}</span>
            <Badge variant="outline" className="text-xs mt-1" style={{ borderColor: color, color }}>{grade}</Badge>
          </div>
        </div>
        {/* Breakdown */}
        <div className="w-full space-y-2">
          {dsi?.breakdown && Object.entries(dsi.breakdown).map(([k, v]: [string, any]) => (
            <div key={k} className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground w-32 capitalize">{k.replace(/_/g, ' ')}</span>
              <div className="flex-1 bg-muted rounded-full h-2">
                <div className="h-2 rounded-full transition-all" style={{ width: `${Math.min(100, (v / 30) * 100)}%`, backgroundColor: color }} />
              </div>
              <span className="font-medium w-10 text-right">{typeof v === 'number' ? v.toFixed(1) : v}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Demand Trend Card ─────────────────────────────────────
function DemandTrendCard({ trend, hypeQuality }: { trend: any; hypeQuality: any }) {
  const icon = trend?.trend === 'rising' ? <ArrowUpRight className="h-5 w-5 text-green-500" />
    : trend?.trend === 'declining' ? <ArrowDownRight className="h-5 w-5 text-red-500" />
      : <ArrowRight className="h-5 w-5 text-yellow-500" />;
  const trendColor = trend?.trend === 'rising' ? 'text-green-600' : trend?.trend === 'declining' ? 'text-red-600' : 'text-yellow-600';
  const hypeColor = hypeQuality?.classification === 'genuine' ? 'bg-green-500/10 text-green-700 border-green-200'
    : hypeQuality?.classification === 'manufactured' ? 'bg-red-500/10 text-red-700 border-red-200'
      : 'bg-yellow-500/10 text-yellow-700 border-yellow-200';

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2"><TrendingUp className="h-5 w-5" /> Demand Trend & Hype Quality</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          {icon}
          <div>
            <p className={`font-semibold capitalize ${trendColor}`}>{trend?.trend ?? 'stable'}</p>
            <p className="text-sm text-muted-foreground">{trend?.description}</p>
          </div>
        </div>
        <Separator />
        <div className="flex items-center gap-3">
          <Flame className="h-5 w-5 text-orange-500" />
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Hype Quality:</span>
              <Badge className={hypeColor}>{hypeQuality?.classification ?? 'mixed'}</Badge>
              <span className="text-xs text-muted-foreground">{pct(hypeQuality?.confidence ?? 0.5)} confidence</span>
            </div>
            <p className="text-sm text-muted-foreground mt-1">{hypeQuality?.description}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Forecast Panel ────────────────────────────────────────
function ForecastPanel({ forecast }: { forecast: any }) {
  const curve = forecast?.demand_curve_30d ?? [];
  const maxDemand = Math.max(...curve.map((p: any) => p.demand), 0.01);
  const revenueColor = forecast?.revenue_class === 'blockbuster' ? 'text-green-500' : forecast?.revenue_class === 'hit' ? 'text-blue-500' : forecast?.revenue_class === 'average' ? 'text-yellow-500' : 'text-red-500';

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2"><BarChart3 className="h-5 w-5" /> Demand Forecast</CardTitle>
        <CardDescription>30-day demand projection &amp; revenue prediction</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Mini bar chart */}
        <div className="flex items-end gap-[2px] h-24 bg-muted/30 rounded-lg p-2">
          {curve.map((p: any, i: number) => (
            <div key={i} className="flex-1 flex flex-col items-center justify-end h-full">
              <div
                className="w-full rounded-t-sm bg-primary/80 hover:bg-primary transition-colors"
                style={{ height: `${(p.demand / maxDemand) * 100}%`, minHeight: '2px' }}
                title={`Day ${p.day}: ${pct(p.demand)}`}
              />
            </div>
          ))}
        </div>
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Day 1</span><span>Day 15</span><span>Day 30</span>
        </div>

        <Separator />

        <div className="grid grid-cols-3 gap-3">
          <div className="text-center">
            <p className="text-[10px] text-muted-foreground uppercase">Revenue Class</p>
            <p className={`text-lg font-bold capitalize ${revenueColor}`}>{forecast?.revenue_class ?? 'N/A'}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-muted-foreground uppercase">Opening Week</p>
            <p className="text-lg font-bold">{pct(forecast?.opening_week_engagement ?? 0.5)}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-muted-foreground uppercase">Confidence</p>
            <p className="text-lg font-bold">{pct(forecast?.forecast_confidence ?? 0.5)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Regional Demand Card ──────────────────────────────────
function RegionalDemandCard({ regions }: { regions: any[] }) {
  const tierColor = (t: string) => t === 'high' ? 'bg-green-500/10 text-green-700 border-green-200' : t === 'medium' ? 'bg-yellow-500/10 text-yellow-700 border-yellow-200' : 'bg-red-500/10 text-red-700 border-red-200';

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2"><Globe className="h-5 w-5" /> Regional Demand</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {(regions ?? []).map((r: any, i: number) => (
            <div key={i} className="flex items-center gap-3">
              <span className="text-sm w-32 truncate">{r.region}</span>
              <div className="flex-1 bg-muted rounded-full h-2.5">
                <div className="h-2.5 rounded-full bg-primary/70 transition-all" style={{ width: `${(r.demand_strength ?? 0) * 100}%` }} />
              </div>
              <Badge variant="outline" className={`text-[10px] ${tierColor(r.tier)}`}>{r.tier}</Badge>
            </div>
          ))}
          {(!regions || regions.length === 0) && <p className="text-sm text-muted-foreground">No regional data available</p>}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Piracy & Recommendations Card ─────────────────────────
function PiracyAndRecsCard({ piracy, recommendations }: { piracy: any; recommendations: any[] }) {
  const piracyColor = piracy?.level === 'high' ? 'bg-red-500/10 text-red-700 border-red-200' : piracy?.level === 'medium' ? 'bg-yellow-500/10 text-yellow-700 border-yellow-200' : 'bg-green-500/10 text-green-700 border-green-200';
  const priorityIcon = (p: string) => p === 'high' ? <AlertTriangle className="h-3.5 w-3.5 text-red-500" /> : <Star className="h-3.5 w-3.5 text-yellow-500" />;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2"><Lock className="h-5 w-5" /> Piracy Risk & Recommendations</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          <ShieldAlert className="h-5 w-5" />
          <Badge className={piracyColor}>{piracy?.level ?? 'unknown'} risk</Badge>
          <span className="text-sm text-muted-foreground">Score: {pct(piracy?.score ?? 0.5)}</span>
        </div>

        {piracy?.mitigations?.length > 0 && (
          <div className="text-xs text-muted-foreground space-y-1">
            {piracy.mitigations.map((m: string, i: number) => <p key={i}>• {m}</p>)}
          </div>
        )}

        <Separator />

        <div className="space-y-2">
          {(recommendations ?? []).map((r: any, i: number) => (
            <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-muted/40">
              {priorityIcon(r.priority)}
              <div>
                <Badge variant="outline" className="text-[9px] mb-0.5">{r.category?.replace(/_/g, ' ')}</Badge>
                <p className="text-sm">{r.action}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Full Demand Tab ───────────────────────────────────────
function DemandTab({ projectId }: { projectId: string }) {
  const [demand, setDemand] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getPhase7Demand(Number(projectId))
      .then(setDemand)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
      <p className="text-sm text-muted-foreground">Computing demand intelligence...</p>
    </div>
  );

  if (error || !demand) return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <AlertCircle className="h-6 w-6 text-destructive" />
      <p className="text-sm text-destructive">{error || 'Failed to load demand data'}</p>
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <DSIGauge dsi={demand.dsi} />
        <DemandTrendCard trend={demand.demand_trend} hypeQuality={demand.hype_quality} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ForecastPanel forecast={demand.forecast} />
        <RegionalDemandCard regions={demand.regional_demand} />
      </div>
      <PiracyAndRecsCard piracy={demand.piracy_risk} recommendations={demand.recommendations} />
    </div>
  );
}


// ══════════════════════════════════════════════════════════════
// MAIN PAGE
// ══════════════════════════════════════════════════════════════

export default function Phase7Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getPhase7Timeline(Number(projectId))
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return (
    <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center gap-3">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <p className="text-sm text-muted-foreground">Running Phase 7 intelligence engines...</p>
    </div>
  );

  if (error || !data) return (
    <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center gap-3">
      <AlertCircle className="h-8 w-8 text-destructive" />
      <p className="text-sm text-destructive">{error || 'Failed to load'}</p>
      <Button variant="outline" size="sm" onClick={() => window.location.reload()}>Retry</Button>
    </div>
  );

  const { discoverability: disco, confidence, visibility_risk: vis, momentum, budget_allocation: budget, barriers, conversion, festival_impact: festival, ticket_pricing: pricing, market_shocks: shocks, recovery, sensitivity } = data;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex items-center justify-between mb-6">
        <Button variant="ghost" onClick={() => navigate({ to: '/projects/$projectId', params: { projectId } })}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to Project Overview
        </Button>
      </div>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold">Phase 7: Release & Discoverability Engine</h1>
          {data.demand_intelligence && (
            <Badge variant="outline" className="text-xs flex items-center gap-1.5 border-green-300 text-green-700 bg-green-50">
              <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" /><span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" /></span>
              Live Signals
            </Badge>
          )}
        </div>
        <p className="text-muted-foreground text-lg mb-4">Predict, optimize, and recover discoverability with data-driven intelligence.</p>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div className="rounded-xl border bg-card p-3 text-center">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Discoverability</p>
            <p className={`text-xl font-bold ${gradeColor(disco.grade)}`}>{pct(disco.score)} {disco.grade}</p>
          </div>
          <div className="rounded-xl border bg-card p-3 text-center">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Confidence</p>
            <p className="text-xl font-bold">{pct(confidence.confidence)} {confidence.reliability_grade}</p>
          </div>
          <div className="rounded-xl border bg-card p-3 text-center">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Visibility Risk</p>
            <p className="text-xl font-bold"><Badge className={riskBadge(vis.visibility_risk)}>{vis.visibility_risk}</Badge></p>
          </div>
          <div className="rounded-xl border bg-card p-3 text-center">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Market</p>
            <p className="text-xl font-bold"><Badge className={riskBadge(shocks.overall_risk)}>{shocks.overall_risk}</Badge></p>
          </div>
          <div className="rounded-xl border bg-card p-3 text-center">
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">Conversion</p>
            <p className="text-xl font-bold">{pct(conversion.conversion_probability)}</p>
          </div>
          {data.demand_intelligence && (
            <div className="rounded-xl border bg-card p-3 text-center border-primary/20">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-0.5">DSI</p>
              <p className="text-xl font-bold text-primary">{data.demand_intelligence.dsi_score} <span className="text-sm">{data.demand_intelligence.dsi_grade}</span></p>
            </div>
          )}
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4 md:grid-cols-7 h-10">
          <TabsTrigger value="overview" className="text-xs"><Gauge className="h-3.5 w-3.5 mr-1" /> Overview</TabsTrigger>
          <TabsTrigger value="demand" className="text-xs"><Brain className="h-3.5 w-3.5 mr-1" /> Demand</TabsTrigger>
          <TabsTrigger value="momentum" className="text-xs"><TrendingUp className="h-3.5 w-3.5 mr-1" /> Momentum</TabsTrigger>
          <TabsTrigger value="budget" className="text-xs"><Wallet className="h-3.5 w-3.5 mr-1" /> Budget</TabsTrigger>
          <TabsTrigger value="risks" className="text-xs"><AlertTriangle className="h-3.5 w-3.5 mr-1" /> Risks</TabsTrigger>
          <TabsTrigger value="audience" className="text-xs"><Target className="h-3.5 w-3.5 mr-1" /> Audience</TabsTrigger>
          <TabsTrigger value="strategy" className="text-xs"><Sparkles className="h-3.5 w-3.5 mr-1" /> Strategy</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <DiscoverabilityGauge disco={disco} confidence={confidence} />
            <VisibilityRiskCard risk={vis} />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ShocksCard shocks={shocks} />
            <BarriersCard barriers={barriers} />
          </div>
        </TabsContent>

        <TabsContent value="demand" className="space-y-4">
          <DemandTab projectId={projectId} />
        </TabsContent>

        <TabsContent value="momentum" className="space-y-4">
          <MomentumCard momentum={momentum} />
          <FestivalCard festival={festival} />
        </TabsContent>

        <TabsContent value="budget" className="space-y-4">
          <BudgetCard budget={budget} />
          <TicketCard pricing={pricing} />
        </TabsContent>

        <TabsContent value="risks" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ShocksCard shocks={shocks} />
            <VisibilityRiskCard risk={vis} />
          </div>
          <RecoveryCard recovery={recovery} />
        </TabsContent>

        <TabsContent value="audience" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ConversionCard conversion={conversion} />
            <FestivalCard festival={festival} />
          </div>
        </TabsContent>

        <TabsContent value="strategy" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <BudgetCard budget={budget} />
            <RecoveryCard recovery={recovery} />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <TicketCard pricing={pricing} />
            <BarriersCard barriers={barriers} />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
