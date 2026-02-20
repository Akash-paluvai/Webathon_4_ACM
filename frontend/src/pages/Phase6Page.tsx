import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';

/**
 * Phase 6: Distribution Strategy & Negotiation
 * 
 * ARCHITECTURE NOTE:
 * - This phase handles distribution planning and deal negotiation
 * - Updates FilmProject fields: releaseModel, distributionConfidence
 * - Independent phase for parallel development
 */
export default function Phase6Page() {
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
        <h1 className="text-3xl font-bold mb-2">Phase 6: Distribution Strategy & Negotiation</h1>
        <p className="text-muted-foreground text-lg">
          Plan distribution strategy and manage deal negotiations
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Distribution Strategy Form</CardTitle>
          <CardDescription>
            This is a placeholder for Phase 6 functionality. Add distribution planning inputs here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-muted-foreground">
            <p>
              <strong>TODO:</strong> Implement distribution strategy with the following fields:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Release Model (THEATRE, OTT, HYBRID)</li>
              <li>Distribution Confidence (LOW, MEDIUM, HIGH)</li>
              <li>Deal Negotiation Tracking</li>
              <li>Territory Planning</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
