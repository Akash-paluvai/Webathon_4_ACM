/**
 * Frontend Type Definitions
 * 
 * This file contains type definitions that are used in the frontend but not exported by the backend.
 * These types mirror the backend's internal types to maintain type safety.
 */

// BudgetLevel is used in FilmProject but not exported by backend
// Define it here to match backend's internal enum
export type BudgetLevel = 'low' | 'medium' | 'high';
