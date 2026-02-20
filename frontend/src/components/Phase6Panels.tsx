import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import {
    Calendar, Activity, TrendingUp, TrendingDown, Shield,
    Zap, BarChart3, AlertTriangle, ChevronRight, ArrowLeftRight, Loader2,
} from 'lucide-react';

const pct = (n: number) => `${Math.round(n * 100)}%`;

const MONTHS = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// ── Release Timing Panel ─────────────────────────────────────

interface MonthlyScore {
    month: number; month_name: string; season: string;
    release_score: number; audience_demand: number; low_competition: number;
    hype_factor: number; festival_boost: number; genre_seasonality: number;
    festival_name?: string; risk: string;
}

interface ReleaseTiming {
    best_month: number; best_month_name: string; best_date: string; best_season: string;
    best_score: number; risk_level: string;
    alternate_windows: { month: number; month_name: string; season: string; score: number; risk: string; festival?: string }[];
    festival_advantage: { has_festival_window: boolean; best_festival?: string; festival_boost: number; festival_months: any[] };
    monthly_scores: MonthlyScore[];
}

function riskColor(r: string) {
    return { low: 'bg-emerald-500/15 text-emerald-700', moderate: 'bg-amber-500/15 text-amber-700', high: 'bg-orange-500/15 text-orange-700', very_high: 'bg-red-500/15 text-red-700' }[r] || 'bg-gray-100 text-gray-600';
}

function scoreGradient(s: number) {
    if (s >= 0.65) return 'bg-emerald-500';
    if (s >= 0.50) return 'bg-green-500';
    if (s >= 0.35) return 'bg-amber-500';
    return 'bg-orange-500';
}

export function ReleaseTimingPanel({ timing }: { timing: ReleaseTiming }) {
    if (!timing) return null;
    const maxScore = Math.max(...timing.monthly_scores.map(s => s.release_score), 0.01);

    return (
        <div className="space-y-4">
            {/* Best Window */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Card className="md:col-span-2">
                    <CardHeader className="pb-2">
                        <div className="flex items-center gap-2"><Calendar className="h-5 w-5 text-blue-500" /><CardTitle className="text-lg">Best Release Window</CardTitle></div>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-baseline gap-3 mb-4">
                            <span className="text-4xl font-bold">{timing.best_date}</span>
                            <Badge variant="outline" className="capitalize">{timing.best_season}</Badge>
                            <Badge className={riskColor(timing.risk_level)}>{timing.risk_level} risk</Badge>
                        </div>
                        <div className="flex gap-2 items-center text-sm text-muted-foreground mb-3">
                            <Zap className="h-3.5 w-3.5 text-amber-500" />
                            Release Score: <strong className="text-foreground">{pct(timing.best_score)}</strong>
                            {timing.festival_advantage.best_festival && (
                                <span className="ml-2">🎉 {timing.festival_advantage.best_festival} boost</span>
                            )}
                        </div>
                        <Separator className="my-3" />
                        <p className="text-xs text-muted-foreground font-medium mb-2">Alternate Windows</p>
                        <div className="grid grid-cols-3 gap-2">
                            {timing.alternate_windows.map(w => (
                                <div key={w.month} className="rounded-lg border p-2.5 text-center text-sm">
                                    <p className="font-semibold">{w.month_name}</p>
                                    <p className="text-xs text-muted-foreground capitalize">{w.season}</p>
                                    <p className="font-bold mt-1">{pct(w.score)}</p>
                                    <Badge className={`text-[9px] mt-1 ${riskColor(w.risk)}`}>{w.risk}</Badge>
                                    {w.festival && <p className="text-[9px] text-blue-600 mt-0.5">🎉 {w.festival}</p>}
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Festival Advantage */}
                <Card>
                    <CardHeader className="pb-2"><CardTitle className="text-sm">Festival Advantage</CardTitle></CardHeader>
                    <CardContent>
                        {timing.festival_advantage.has_festival_window ? (
                            <div className="space-y-2">
                                {timing.festival_advantage.festival_months.map((fm: any, i: number) => (
                                    <div key={i} className="flex items-center justify-between text-xs">
                                        <span className="font-medium">{fm.month_name}</span>
                                        <div className="flex items-center gap-1.5">
                                            <span className="text-blue-600 text-[10px]">{fm.festival}</span>
                                            <span className="font-mono font-bold">{pct(fm.boost)}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-xs text-muted-foreground">No festival windows align with target markets.</p>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Monthly Heatmap */}
            <Card>
                <CardHeader className="pb-2">
                    <div className="flex items-center gap-2"><BarChart3 className="h-5 w-5 text-purple-500" /><CardTitle className="text-lg">Monthly Release Score Heatmap</CardTitle></div>
                    <CardDescription>Higher bars = better release windows. Components: Demand · Competition · Hype · Festival · Genre</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-12 gap-1.5 mb-6" style={{ minHeight: 180 }}>
                        {timing.monthly_scores.map(ms => {
                            const h = Math.round((ms.release_score / maxScore) * 140) + 20;
                            const isBest = ms.month === timing.best_month;
                            return (
                                <div key={ms.month} className="flex flex-col items-center justify-end gap-1">
                                    <span className="text-[9px] font-mono text-muted-foreground">{pct(ms.release_score)}</span>
                                    <div className={`w-full rounded-t transition-all duration-500 ${isBest ? 'ring-2 ring-primary' : ''} ${scoreGradient(ms.release_score)}`}
                                        style={{ height: h, opacity: isBest ? 1 : 0.7 }}
                                        title={`${ms.month_name}: ${pct(ms.release_score)}`} />
                                    <span className={`text-[10px] font-medium ${isBest ? 'text-primary font-bold' : 'text-muted-foreground'}`}>{MONTHS[ms.month]}</span>
                                    {ms.festival_name && <span className="text-[8px] text-blue-600">🎉</span>}
                                </div>
                            );
                        })}
                    </div>
                    <div className="flex gap-4 text-[10px] text-muted-foreground">
                        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500" /> ≥65% Ideal</span>
                        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> ≥50% Good</span>
                        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500" /> ≥35% Moderate</span>
                        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-500" /> &lt;35% Risky</span>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

// ── Competition Panel ────────────────────────────────────────

interface CompetitorEntry {
    title: string; genre: string; month?: number; star_power: number; platform: string;
}

interface CompHeatmapEntry {
    month: number; month_name: string; density: number; avg_star_power: number;
    cdi: number; competitor_count: number; competitors: string[];
}

interface CompetitionIntel {
    cdi: number; genre_density: number; language_density: number; budget_crowd: number;
    total_competitors: number; same_genre_count: number;
    competitors: CompetitorEntry[];
    competition_heatmap: CompHeatmapEntry[];
    risk_by_month: { month: number; month_name: string; risk: string; cdi: number }[];
    safest_months: string[];
}

export function CompetitionPanel({ intel }: { intel: CompetitionIntel }) {
    if (!intel) return null;
    const maxDensity = Math.max(...intel.competition_heatmap.map(h => h.cdi), 0.01);

    return (
        <div className="space-y-4">
            {/* CDI Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Card>
                    <CardHeader className="pb-2"><div className="flex items-center gap-2"><Activity className="h-5 w-5 text-red-500" /><CardTitle className="text-lg">CDI</CardTitle></div></CardHeader>
                    <CardContent>
                        <div className="text-center">
                            <span className="text-5xl font-bold tabular-nums">{pct(intel.cdi)}</span>
                            <p className="text-xs text-muted-foreground mt-1">Competition Density Index</p>
                        </div>
                        <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs">
                            <div className="rounded-lg bg-muted/50 p-2"><p className="text-muted-foreground">Genre</p><p className="font-semibold">{pct(intel.genre_density)}</p></div>
                            <div className="rounded-lg bg-muted/50 p-2"><p className="text-muted-foreground">Language</p><p className="font-semibold">{pct(intel.language_density)}</p></div>
                            <div className="rounded-lg bg-muted/50 p-2"><p className="text-muted-foreground">Budget</p><p className="font-semibold">{pct(intel.budget_crowd)}</p></div>
                        </div>
                        <div className="mt-3 text-center">
                            <p className="text-xs text-muted-foreground">{intel.total_competitors} competitors · {intel.same_genre_count} same genre</p>
                            <p className="text-xs font-medium mt-1 text-emerald-600">Safest: {intel.safest_months.join(', ')}</p>
                        </div>
                    </CardContent>
                </Card>

                {/* Competition Heatmap */}
                <Card className="md:col-span-2">
                    <CardHeader className="pb-2">
                        <div className="flex items-center gap-2"><BarChart3 className="h-5 w-5 text-orange-500" /><CardTitle className="text-lg">Competition Density by Month</CardTitle></div>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-12 gap-1.5 mb-4" style={{ minHeight: 150 }}>
                            {intel.competition_heatmap.map(hm => {
                                const h = Math.round((hm.cdi / maxDensity) * 120) + 20;
                                const isSafe = intel.safest_months.includes(hm.month_name);
                                const color = hm.cdi > 0.6 ? 'bg-red-500' : hm.cdi > 0.3 ? 'bg-amber-500' : 'bg-emerald-500';
                                return (
                                    <div key={hm.month} className="flex flex-col items-center justify-end gap-1" title={`${hm.month_name}: CDI ${pct(hm.cdi)} · ${hm.competitor_count} films`}>
                                        <span className="text-[8px] font-mono text-muted-foreground">{hm.competitor_count}</span>
                                        <div className={`w-full rounded-t transition-all ${color} ${isSafe ? 'ring-2 ring-emerald-400' : ''}`} style={{ height: h, opacity: isSafe ? 1 : 0.65 }} />
                                        <span className={`text-[10px] ${isSafe ? 'font-bold text-emerald-600' : 'text-muted-foreground'}`}>{MONTHS[hm.month]}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Competitor Timeline */}
            <Card>
                <CardHeader className="pb-2">
                    <div className="flex items-center gap-2"><Shield className="h-5 w-5 text-blue-500" /><CardTitle className="text-lg">Competitor Timeline</CardTitle></div>
                    <CardDescription>Films competing for audience attention</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full text-xs">
                            <thead>
                                <tr className="border-b text-muted-foreground">
                                    <th className="text-left py-2 pr-3 font-medium">Film</th>
                                    <th className="text-left py-2 px-2 font-medium">Genre</th>
                                    <th className="text-center py-2 px-2 font-medium">Month</th>
                                    <th className="text-center py-2 px-2 font-medium">⭐ Star</th>
                                    <th className="text-left py-2 pl-2 font-medium">Platform</th>
                                </tr>
                            </thead>
                            <tbody>
                                {intel.competitors.slice(0, 12).map((c, i) => (
                                    <tr key={i} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                                        <td className="py-2 pr-3 font-semibold">{c.title}</td>
                                        <td className="py-2 px-2">{c.genre}</td>
                                        <td className="py-2 px-2 text-center">{c.month ? MONTHS[c.month] : '—'}</td>
                                        <td className="py-2 px-2 text-center">
                                            <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                                                <div className={`h-full rounded-full ${c.star_power > 0.7 ? 'bg-amber-500' : 'bg-blue-400'}`} style={{ width: `${Math.round(c.star_power * 100)}%` }} />
                                            </div>
                                        </td>
                                        <td className="py-2 pl-2 text-muted-foreground">{c.platform}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

// ── Simulation Controls ──────────────────────────────────────

interface SimResult {
    original_month: string; original_score: number; original_risk: string;
    new_month: string; new_score: number; new_risk: string;
    delta: number; recommendation: string;
}

export function SimulationPanel({
    projectId, bestMonth, timing
}: {
    projectId: number; bestMonth: number; timing: ReleaseTiming;
}) {
    const [from, setFrom] = useState(bestMonth.toString());
    const [to, setTo] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<SimResult | null>(null);

    const runSim = async () => {
        if (!to || from === to) return;
        setLoading(true); setResult(null);
        try {
            const r = await fetch(`/phase6/simulate-release?project_id=${projectId}&current_month=${from}&new_month=${to}`, { method: 'POST' });
            setResult(await r.json());
        } catch { /* ignore */ }
        setLoading(false);
    };

    return (
        <Card>
            <CardHeader className="pb-3">
                <div className="flex items-center gap-2"><ArrowLeftRight className="h-5 w-5 text-cyan-500" /><CardTitle className="text-lg">Release Date Simulator</CardTitle></div>
                <CardDescription>Compare what happens if you shift from one release month to another</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="flex items-end gap-3 mb-4">
                    <div className="space-y-1">
                        <label className="text-xs text-muted-foreground font-medium">Current Month</label>
                        <Select value={from} onValueChange={setFrom}>
                            <SelectTrigger className="w-[140px]"><SelectValue /></SelectTrigger>
                            <SelectContent>{timing.monthly_scores.map(ms => <SelectItem key={ms.month} value={ms.month.toString()}>{ms.month_name}</SelectItem>)}</SelectContent>
                        </Select>
                    </div>
                    <ChevronRight className="h-5 w-5 text-muted-foreground mb-2" />
                    <div className="space-y-1">
                        <label className="text-xs text-muted-foreground font-medium">New Month</label>
                        <Select value={to} onValueChange={setTo}>
                            <SelectTrigger className="w-[140px]"><SelectValue placeholder="Pick..." /></SelectTrigger>
                            <SelectContent>{timing.monthly_scores.map(ms => <SelectItem key={ms.month} value={ms.month.toString()}>{ms.month_name}</SelectItem>)}</SelectContent>
                        </Select>
                    </div>
                    <Button onClick={runSim} disabled={loading || !to || from === to} size="sm">
                        {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" /> : <Zap className="h-3.5 w-3.5 mr-1" />}
                        Simulate
                    </Button>
                </div>

                {result && (
                    <div className={`rounded-xl border p-4 ${result.delta > 0 ? 'border-emerald-500/30 bg-emerald-500/5' : result.delta < -0.03 ? 'border-red-500/30 bg-red-500/5' : 'border-amber-500/30 bg-amber-500/5'}`}>
                        <div className="grid grid-cols-3 gap-4 mb-3">
                            <div className="text-center">
                                <p className="text-xs text-muted-foreground">Original</p>
                                <p className="text-xl font-bold">{result.original_month}</p>
                                <p className="text-sm">{pct(result.original_score)}</p>
                                <Badge className={`text-[9px] ${riskColor(result.original_risk)}`}>{result.original_risk}</Badge>
                            </div>
                            <div className="flex items-center justify-center">
                                <div className="text-center">
                                    {result.delta > 0 ? <TrendingUp className="h-6 w-6 text-emerald-500 mx-auto" /> : <TrendingDown className="h-6 w-6 text-red-500 mx-auto" />}
                                    <span className={`text-lg font-bold ${result.delta > 0 ? 'text-emerald-600' : 'text-red-600'}`}>{result.delta > 0 ? '+' : ''}{pct(result.delta)}</span>
                                </div>
                            </div>
                            <div className="text-center">
                                <p className="text-xs text-muted-foreground">New</p>
                                <p className="text-xl font-bold">{result.new_month}</p>
                                <p className="text-sm">{pct(result.new_score)}</p>
                                <Badge className={`text-[9px] ${riskColor(result.new_risk)}`}>{result.new_risk}</Badge>
                            </div>
                        </div>
                        <div className="flex items-start gap-2 text-sm">
                            <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5 text-amber-500" />
                            <p>{result.recommendation}</p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
