import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';

/**
 * Phase 1: Script Selection & Concept Evaluation
 * 
 * ARCHITECTURE NOTE:
 * - This phase focuses on initial concept evaluation and risk assessment
 * - Updates FilmProject fields: conceptRisk, targetAudience, goDecision
 * - This is an INDEPENDENT phase that can be developed in parallel with other phases
 * 
 * EXTENSION POINTS:
 * - Add form inputs for concept evaluation criteria
 * - Integrate validation logic from backend (rules/phase1_rules.py)
 * - Call backend API to update phase data: updatePhase(projectId, 1, phaseData)
 * - Display AI-generated insights: generateInsights(projectId)
 * 
 * DO NOT:
 * - Add database access logic here (backend only)
 * - Create separate schemas (use FilmProject model)
 * - Mix business logic with UI (keep in backend rules)
 */
export default function Phase1Page() {
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
        <h1 className="text-3xl font-bold mb-2">Phase 1: Script Selection & Concept Evaluation</h1>
        <p className="text-muted-foreground text-lg">
          Evaluate script concepts, assess market viability, and make go/no-go decisions
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Concept Evaluation Form</CardTitle>
          <CardDescription>
            This is a placeholder for Phase 1 functionality. Add form inputs and validation logic here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-muted-foreground">
            <p>
              <strong>TODO:</strong> Implement concept evaluation form with the following fields:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Concept Risk Assessment (LOW, MEDIUM, HIGH)</li>
              <li>Target Audience Definition</li>
              <li>Go/No-Go Decision</li>
              <li>Market Viability Analysis</li>
            </ul>
            <p className="mt-6">
              <strong>Backend Integration:</strong> Call <code className="bg-muted px-2 py-1 rounded">updatePhase(projectId, 1, data)</code> to save phase data
            </p>
            <p>
              <strong>AI Integration:</strong> Call <code className="bg-muted px-2 py-1 rounded">generateInsights(projectId)</code> for recommendations
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
