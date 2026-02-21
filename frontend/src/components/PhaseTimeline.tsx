import { useNavigate } from '@tanstack/react-router';
import { cn } from '@/lib/utils';
import {
    FileText, Users, Film, PlayCircle, Megaphone,
    Globe, Zap, BarChart, CheckCircle2, Circle
} from 'lucide-react';

interface Phase {
    number: number;
    name: string;
    path: string;
}

interface PhaseTimelineProps {
    projectId: string;
    currentPhase: number;
}

export function PhaseTimeline({ projectId, currentPhase }: PhaseTimelineProps) {
    const navigate = useNavigate();

    const phases = [
        { number: 1, name: 'Script Selection', icon: FileText, path: `/projects/${projectId}/phase-1` },
        { number: 2, name: 'Packaging', icon: Users, path: `/projects/${projectId}/phase-2` },
        { number: 3, name: 'Production', icon: Film, path: `/projects/${projectId}/phase-3` },
        { number: 4, name: 'Post-Production', icon: PlayCircle, path: `/projects/${projectId}/phase-4` },
        { number: 5, name: 'Marketing', icon: Megaphone, path: `/projects/${projectId}/phase-5` },
        { number: 6, name: 'Distribution', icon: Globe, path: `/projects/${projectId}/phase-6` },
        { number: 7, name: 'Release', icon: Zap, path: `/projects/${projectId}/phase-7` },
        { number: 8, name: 'Analysis', icon: BarChart, path: `/projects/${projectId}/phase-8` },
    ];

    return (
        <div className="w-full py-8 overflow-x-auto no-scrollbar">
            <div className="flex items-center min-w-[800px] px-4">
                {phases.map((phase, index) => {
                    const isCompleted = phase.number < currentPhase;
                    const isActive = phase.number === currentPhase;
                    const Icon = phase.icon;

                    return (
                        <div key={phase.number} className="flex-1 flex items-center group">
                            <div className="relative flex flex-col items-center">
                                {/* Node */}
                                <button
                                    onClick={() => navigate({ to: phase.path as any })}
                                    className={cn(
                                        "w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 border-2 z-10",
                                        isActive && "bg-primary border-primary text-primary-foreground shadow-lg scale-110",
                                        isCompleted && "bg-primary/20 border-primary text-primary",
                                        !isActive && !isCompleted && "bg-background border-muted text-muted-foreground"
                                    )}
                                >
                                    {isCompleted ? (
                                        <CheckCircle2 className="h-5 w-5" />
                                    ) : (
                                        <Icon className={cn("h-5 w-5", isActive && "animate-pulse")} />
                                    )}
                                </button>

                                {/* Label */}
                                <div className="absolute top-12 text-center w-24 left-1/2 -translate-x-1/2">
                                    <p className={cn(
                                        "text-[10px] font-bold uppercase tracking-wider transition-colors",
                                        isActive ? "text-primary" : "text-muted-foreground"
                                    )}>
                                        {phase.name}
                                    </p>
                                </div>
                            </div>

                            {/* Connector */}
                            {index < phases.length - 1 && (
                                <div className="flex-1 h-[2px] mx-2 relative top-[-10px]">
                                    <div className={cn(
                                        "absolute inset-0 transition-all duration-500",
                                        phase.number < currentPhase ? "bg-primary" : "bg-muted"
                                    )} />
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
