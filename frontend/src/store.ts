// ─── Film OS — Global State (Zustand) ───

import { create } from 'zustand';

interface AppState {
    // Navigation
    currentPhase: number;            // 1, 2, or 3
    unlockedPhases: number[];        // which phases are accessible
    projectId: number | null;        // set after Phase 1 confirm

    // Phase 1 results
    phase1Analysis: any | null;
    phase1Inputs: {
        scriptText: string;
        genre: string;
        theme: string;
        scale: string;
    };

    // Phase 2 results
    phase2Feasibility: any | null;
    phase2Packaging: any | null;
    phase2Inputs: {
        budgetLevel: string;
        talentStrategy: string;
    };

    // Phase 3 results
    phase3Analysis: any | null;
    phase3Inputs: {
        plannedShootDays: number;
        daysPerWeek: number;
        hoursPerDay: number;
        crewSize: number;
        complexityLevel: number;
        currentProgressPercent: number;
        actualShootDays: number | null;
    };

    // Loading
    loading: boolean;

    // Actions
    setCurrentPhase: (phase: number) => void;
    unlockPhase: (phase: number) => void;
    setProjectId: (id: number) => void;
    setPhase1Analysis: (data: any) => void;
    setPhase1Inputs: (inputs: Partial<AppState['phase1Inputs']>) => void;
    setPhase2Feasibility: (data: any) => void;
    setPhase2Packaging: (data: any) => void;
    setPhase2Inputs: (inputs: Partial<AppState['phase2Inputs']>) => void;
    setPhase3Analysis: (data: any) => void;
    setPhase3Inputs: (inputs: Partial<AppState['phase3Inputs']>) => void;
    setLoading: (loading: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
    currentPhase: 1,
    unlockedPhases: [1],
    projectId: null,

    phase1Analysis: null,
    phase1Inputs: {
        scriptText: '',
        genre: 'Drama',
        theme: '',
        scale: 'Studio',
    },

    phase2Feasibility: null,
    phase2Packaging: null,
    phase2Inputs: {
        budgetLevel: 'Medium',
        talentStrategy: 'Mixed',
    },

    phase3Analysis: null,
    phase3Inputs: {
        plannedShootDays: 40,
        daysPerWeek: 5,
        hoursPerDay: 8,
        crewSize: 30,
        complexityLevel: 2,
        currentProgressPercent: 0,
        actualShootDays: null,
    },

    loading: false,

    setCurrentPhase: (phase) => set({ currentPhase: phase }),
    unlockPhase: (phase) =>
        set((state) => ({
            unlockedPhases: state.unlockedPhases.includes(phase)
                ? state.unlockedPhases
                : [...state.unlockedPhases, phase],
        })),
    setProjectId: (id) => set({ projectId: id }),
    setPhase1Analysis: (data) => set({ phase1Analysis: data }),
    setPhase1Inputs: (inputs) =>
        set((state) => ({ phase1Inputs: { ...state.phase1Inputs, ...inputs } })),
    setPhase2Feasibility: (data) => set({ phase2Feasibility: data }),
    setPhase2Packaging: (data) => set({ phase2Packaging: data }),
    setPhase2Inputs: (inputs) =>
        set((state) => ({ phase2Inputs: { ...state.phase2Inputs, ...inputs } })),
    setPhase3Analysis: (data) => set({ phase3Analysis: data }),
    setPhase3Inputs: (inputs) =>
        set((state) => ({ phase3Inputs: { ...state.phase3Inputs, ...inputs } })),
    setLoading: (loading) => set({ loading }),
}));
