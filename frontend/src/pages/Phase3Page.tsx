import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';

/**
 * Phase 3: Production Phase
 * 
 * ARCHITECTURE NOTE:
 * - This phase tracks production execution and shoot days
 * - Updates FilmProject fields: plannedShootDays, actualShootDays, productionHealth
 * - Independent phase for parallel development
 */
export default function Phase3Page() {
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
        <h1 className="text-3xl font-bold mb-2">Phase 3: Production Phase</h1>
        <p className="text-muted-foreground text-lg">
          Track production progress, shoot days, and production health
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Production Tracking Form</CardTitle>
          <CardDescription>
            This is a placeholder for Phase 3 functionality. Add production tracking inputs here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-muted-foreground">
            <p>
              <strong>TODO:</strong> Implement production tracking with the following fields:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Planned Shoot Days</li>
              <li>Actual Shoot Days</li>
              <li>Production Health Status (STABLE, AT_RISK)</li>
              <li>Daily Progress Reports</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
