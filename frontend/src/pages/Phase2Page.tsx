import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';

/**
 * Phase 2: Packaging & Pre-Production Strategy
 * 
 * ARCHITECTURE NOTE:
 * - This phase focuses on budget planning and talent strategy
 * - Updates FilmProject fields: budgetLevel, talentStrategy, productionFeasibility
 * - This is an INDEPENDENT phase that can be developed in parallel with other phases
 * 
 * EXTENSION POINTS:
 * - Add form inputs for budget and talent planning
 * - Integrate validation logic from backend (rules/phase2_rules.py)
 * - Call backend API to update phase data
 * 
 * DO NOT:
 * - Add database access logic here (backend only)
 * - Create separate schemas (use FilmProject model)
 */
export default function Phase2Page() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };

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
        <h1 className="text-3xl font-bold mb-2">Phase 2: Packaging & Pre-Production Strategy</h1>
        <p className="text-muted-foreground text-lg">
          Define budget levels, talent strategy, and assess production feasibility
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Pre-Production Planning Form</CardTitle>
          <CardDescription>
            This is a placeholder for Phase 2 functionality. Add form inputs and validation logic here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-muted-foreground">
            <p>
              <strong>TODO:</strong> Implement pre-production planning form with the following fields:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Budget Level (LOW, MEDIUM, HIGH)</li>
              <li>Talent Strategy (NEW, MIXED, STAR)</li>
              <li>Production Feasibility Assessment (GOOD, RISKY)</li>
              <li>Resource Planning</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
