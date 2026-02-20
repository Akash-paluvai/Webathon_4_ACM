import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';

/**
 * Phase 5: Marketing Strategy Planning
 * 
 * ARCHITECTURE NOTE:
 * - This phase develops marketing strategy and budget allocation
 * - Updates FilmProject fields: marketingBudgetLevel, primaryMarketingChannel, marketingRisk
 * - Independent phase for parallel development
 */
export default function Phase5Page() {
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
        <h1 className="text-3xl font-bold mb-2">Phase 5: Marketing Strategy Planning</h1>
        <p className="text-muted-foreground text-lg">
          Develop marketing strategy, budget allocation, and channel selection
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Marketing Strategy Form</CardTitle>
          <CardDescription>
            This is a placeholder for Phase 5 functionality. Add marketing planning inputs here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-muted-foreground">
            <p>
              <strong>TODO:</strong> Implement marketing strategy planning with the following fields:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Marketing Budget Level (LOW, MEDIUM, HIGH)</li>
              <li>Primary Marketing Channel (INFLUENCER, FESTIVAL, ADS, PR)</li>
              <li>Marketing Risk Assessment (LOW, MEDIUM, HIGH)</li>
              <li>Campaign Planning</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
