import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';

/**
 * Phase 7: Release & Discoverability
 * 
 * ARCHITECTURE NOTE:
 * - This phase manages release timing and discoverability optimization
 * - Updates FilmProject fields: releaseWindow, competitionLevel, discoverabilityRisk
 * - Independent phase for parallel development
 */
export default function Phase7Page() {
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
        <h1 className="text-3xl font-bold mb-2">Phase 7: Release & Discoverability</h1>
        <p className="text-muted-foreground text-lg">
          Optimize release timing and maximize discoverability
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Release Planning Form</CardTitle>
          <CardDescription>
            This is a placeholder for Phase 7 functionality. Add release planning inputs here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-muted-foreground">
            <p>
              <strong>TODO:</strong> Implement release planning with the following fields:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Release Window Selection</li>
              <li>Competition Level Assessment (LOW, MEDIUM, HIGH)</li>
              <li>Discoverability Risk (LOW, MEDIUM, HIGH)</li>
              <li>Launch Campaign Coordination</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
