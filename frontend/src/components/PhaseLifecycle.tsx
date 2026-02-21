import { useNavigate } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChevronRight, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Phase {
    number: number;
    name: string;
    path: string;
    subtitle: string;
}

interface PhaseLifecycleProps {
    projectId: string;
    currentPhase: number;
}

export function PhaseLifecycle({ projectId, currentPhase }: PhaseLifecycleProps) {
    const navigate = useNavigate();

    const phases: Phase[] = [
        { number: 1, name: 'Script Selection', path: `/projects/${projectId}/phase-1`, subtitle: 'Validated Script Fit' },
        { number: 2, name: 'Packaging', path: `/projects/${projectId}/phase-2`, subtitle: 'Optimal Talent Mix' },
        { number: 3, name: 'Production', path: `/projects/${projectId}/phase-3`, subtitle: 'Healthy Production KPI' },
        { number: 4, name: 'Post-Production', path: `/projects/${projectId}/phase-4`, subtitle: 'Audience Fit Analysis' },
        { number: 5, name: 'Marketing', path: `/projects/${projectId}/phase-5`, subtitle: 'High Discoverability' },
        { number: 6, name: 'Distribution', path: `/projects/${projectId}/phase-6`, subtitle: 'Maximum Platform Leverage' },
        { number: 7, name: 'Release', path: `/projects/${projectId}/phase-7`, subtitle: 'Peak Release Readiness' },
        { number: 8, name: 'Analysis', path: `/projects/${projectId}/phase-8`, subtitle: 'Revenue Maximize Path' },
    ];

    // Circular layout math
    const nodes = phases.map((phase, i) => {
        const angle = (i * 360) / 8 - 90; // Start from top
        const radius = 160;
        const x = 200 + radius * Math.cos((angle * Math.PI) / 180);
        const y = 200 + radius * Math.sin((angle * Math.PI) / 180);
        return { ...phase, x, y };
    });

    const getStatus = (num: number) => {
        if (num === currentPhase) return 'active';
        if (num < currentPhase) return 'completed';
        return 'upcoming';
    };

    return (
        <div className="w-full py-6">
            {/* Desktop Circular View */}
            <div className="hidden lg:flex justify-center items-center relative h-[480px] w-[480px] mx-auto scale-90 xl:scale-100">
                <svg viewBox="0 0 400 400" className="absolute inset-0 w-full h-full pointer-events-none overflow-visible">
                    {/* Main dashed circle */}
                    <circle cx="200" cy="200" r="160" fill="none" stroke="currentColor" strokeWidth="1" className="text-muted/20" strokeDasharray="4 4" />

                    {/* Connecting Arcs */}
                    {nodes.map((node, i) => {
                        const nextNode = nodes[(i + 1) % nodes.length];
                        // SVG Arc path: A rx ry x-axis-rotation large-arc-flag sweep-flag x y
                        const isIterative = i === 7;

                        return (
                            <g key={`arc-${i}`}>
                                <path
                                    d={`M ${node.x} ${node.y} A 160 160 0 0 1 ${nextNode.x} ${nextNode.y}`}
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth={isIterative ? "3" : "2"}
                                    className={cn(
                                        statusToColorClass(getStatus(node.number)),
                                        isIterative && "text-primary/40 stroke-[2] dash-iterative"
                                    )}
                                    strokeDasharray={isIterative ? "8,8" : "none"}
                                />
                                {isIterative && (
                                    <path
                                        d="M 195 48 L 205 40 L 195 32"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="3"
                                        className="text-primary/60"
                                    />
                                )}
                            </g>
                        );
                    })}
                </svg>

                {/* Phase Nodes */}
                {nodes.map((node) => {
                    const status = getStatus(node.number);
                    return (
                        <div
                            key={node.number}
                            className={cn(
                                "absolute -translate-x-1/2 -translate-y-1/2 z-10",
                                "cursor-pointer group flex flex-col items-center transition-all duration-300"
                            )}
                            style={{ left: node.x, top: node.y }}
                            onClick={() => navigate({ to: node.path as any })}
                        >
                            <div className={cn(
                                "w-14 h-14 rounded-full flex flex-col items-center justify-center border-2 transition-all duration-500",
                                status === 'active' && "bg-primary text-primary-foreground border-primary shadow-[0_0_30px_rgba(var(--primary),0.6)] scale-125 ring-4 ring-primary/20",
                                status === 'completed' && "bg-primary/5 text-primary border-primary/40",
                                status === 'upcoming' && "bg-background text-muted-foreground border-muted-foreground/20"
                            )}>
                                <span className="text-sm font-black italic">P{node.number}</span>
                            </div>

                            {/* Label that shows on hover or if active */}
                            <div className={cn(
                                "absolute top-16 w-32 text-center transition-all duration-300",
                                status === 'active' ? "opacity-100 translate-y-0" : "opacity-0 group-hover:opacity-100 -translate-y-2"
                            )}>
                                <p className="text-[11px] font-bold uppercase tracking-tight text-foreground leading-tight">
                                    {node.name}
                                </p>
                                <p className="text-[9px] text-muted-foreground mt-0.5 font-medium italic">
                                    {node.subtitle}
                                </p>
                            </div>
                        </div>
                    );
                })}

                {/* Center Indicator */}
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none group-active:scale-95 transition-transform">
                    <div className="bg-primary/5 p-8 rounded-full border border-primary/10 backdrop-blur-sm">
                        <RefreshCw className="h-10 w-10 text-primary/30 mx-auto animate-spin-slow" />
                        <p className="text-[9px] uppercase tracking-[0.2em] text-primary/40 mt-3 font-black">Iterate</p>
                    </div>
                </div>
            </div>

            {/* Mobile Vertical List View */}
            <div className="lg:hidden space-y-3">
                {phases.map((phase) => {
                    const status = getStatus(phase.number);
                    return (
                        <Button
                            key={phase.number}
                            variant={status === 'active' ? 'default' : 'outline'}
                            className={cn(
                                "w-full justify-between h-auto py-5 px-6 relative group border-2",
                                status === 'completed' && "border-primary/20 bg-primary/5 text-primary opacity-80",
                                status === 'active' && "shadow-lg shadow-primary/20 ring-2 ring-primary/10"
                            )}
                            onClick={() => navigate({ to: phase.path as any })}
                        >
                            <div className="text-left">
                                <div className="flex items-center gap-2 mb-1">
                                    <Badge variant={status === 'active' ? 'secondary' : 'outline'} className="text-[9px] font-black italic tracking-wider h-4">
                                        PHASE {phase.number}
                                    </Badge>
                                    {status === 'active' && <span className="text-[10px] font-bold text-white/80 uppercase animate-pulse">Live</span>}
                                </div>
                                <div className="font-bold text-base">{phase.name}</div>
                                <div className="text-[11px] opacity-70 mt-0.5 italic">{phase.subtitle}</div>
                            </div>
                            <ChevronRight className="h-5 w-5 opacity-40 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                        </Button>
                    );
                })}
                {/* Mobile Iterative Indicator */}
                <div className="flex flex-col items-center py-6 text-muted-foreground/40 italic">
                    <RefreshCw className="h-5 w-5 mb-2" />
                    <span className="text-[10px] uppercase tracking-widest font-bold">Infinite Loop</span>
                </div>
            </div>
        </div>
    );
}

function statusToColorClass(status: string) {
    switch (status) {
        case 'active': return 'text-primary';
        case 'completed': return 'text-primary/60';
        default: return 'text-muted/20';
    }
}
