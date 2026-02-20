import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';

/**
 * Phase 4: Post-Production & Market Testing
 * 
 * ARCHITECTURE NOTE:
 * - This phase handles post-production workflow and audience testing
 * - Updates FilmProject fields: audienceType, audienceInterestScore, testStrategy
 * - Independent phase for parallel development
 */
export default function Phase4Page() {
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
        <h1 className="text-3xl font-bold mb-2">Phase 4: Post-Production & Market Testing</h1>
        <p className="text-muted-foreground text-lg">
          Manage post-production workflow and conduct market testing
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Post-Production & Testing Form</CardTitle>
          <CardDescription>
            This is a placeholder for Phase 4 functionality. Add post-production tracking inputs here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-muted-foreground">
            <p>
              <strong>TODO:</strong> Implement post-production tracking with the following fields:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Audience Type (NICHE, REGIONAL, MASS)</li>
              <li>Audience Interest Score</li>
              <li>Test Strategy (FESTIVAL, PRIVATE, DIGITAL)</li>
              <li>Feedback Collection</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
