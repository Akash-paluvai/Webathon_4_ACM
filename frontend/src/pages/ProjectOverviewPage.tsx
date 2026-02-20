import { useNavigate, useParams } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, ChevronRight } from 'lucide-react';
import { useGetProject } from '@/hooks/useQueries';

/**
 * Project Overview Page
 * 
 * Displays comprehensive project details and provides navigation to all 8 phase pages.
 * This is the central hub for accessing phase-specific workflows.
 */
export default function ProjectOverviewPage() {
  const navigate = useNavigate();
  const { projectId } = useParams({ strict: false }) as { projectId: string };
  const { data: project, isLoading } = useGetProject(BigInt(projectId));

  const phases = [
    { number: 1, name: 'Script Selection & Concept Evaluation', path: `/projects/${projectId}/phase-1` },
    { number: 2, name: 'Packaging & Pre-Production Strategy', path: `/projects/${projectId}/phase-2` },
    { number: 3, name: 'Production Phase', path: `/projects/${projectId}/phase-3` },
    { number: 4, name: 'Post-Production & Market Testing', path: `/projects/${projectId}/phase-4` },
    { number: 5, name: 'Marketing Strategy Planning', path: `/projects/${projectId}/phase-5` },
    { number: 6, name: 'Distribution Strategy & Negotiation', path: `/projects/${projectId}/phase-6` },
    { number: 7, name: 'Release & Discoverability', path: `/projects/${projectId}/phase-7` },
    { number: 8, name: 'Post-Release Optimization & Monetization', path: `/projects/${projectId}/phase-8` },
  ];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Skeleton className="h-8 w-48 mb-8" />
        <div className="grid md:grid-cols-2 gap-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-16">
          <h2 className="text-2xl font-bold mb-2">Project not found</h2>
          <p className="text-muted-foreground mb-6">The project you're looking for doesn't exist.</p>
          <Button onClick={() => navigate({ to: '/projects' })}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Projects
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Button
        variant="ghost"
        onClick={() => navigate({ to: '/projects' })}
        className="mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Projects
      </Button>

      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold">{project.title}</h1>
          <Badge variant="default" className="text-base px-4 py-1">
            Phase {project.currentPhase.toString()}
          </Badge>
        </div>
        <p className="text-muted-foreground text-lg">{project.genre} • {project.language}</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Project Details</CardTitle>
            <CardDescription>Core project information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Theme:</span>
              <span className="font-medium">{project.theme}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Scale:</span>
              <span className="font-medium capitalize">{project.scale}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Budget Level:</span>
              <span className="font-medium capitalize">{project.budgetLevel}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Talent Strategy:</span>
              <span className="font-medium capitalize">{project.talentStrategy.replace('_', ' ')}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Production Status</CardTitle>
            <CardDescription>Current production metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Production Health:</span>
              <Badge variant={project.productionHealth === 'good' ? 'default' : 'destructive'}>
                {project.productionHealth}
              </Badge>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Planned Shoot Days:</span>
              <span className="font-medium">{project.plannedShootDays.toString()}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Audience Type:</span>
              <span className="font-medium capitalize">{project.audienceType}</span>
            </div>
            <Separator />
            <div className="flex justify-between">
              <span className="text-muted-foreground">Release Model:</span>
              <span className="font-medium capitalize">{project.releaseModel}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3 mb-2">
            <img src="/assets/generated/phases-icon.dim_256x256.png" alt="Phases" className="h-8 w-8" />
            <CardTitle>Film Production Phases</CardTitle>
          </div>
          <CardDescription>Navigate through the 8-phase production workflow</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {phases.map((phase) => (
              <Button
                key={phase.number}
                variant={Number(project.currentPhase) === phase.number ? 'default' : 'outline'}
                className="justify-between h-auto py-4 px-6"
                onClick={() => navigate({ to: phase.path as any })}
              >
                <div className="text-left">
                  <div className="font-semibold">Phase {phase.number}</div>
                  <div className="text-sm font-normal opacity-90">{phase.name}</div>
                </div>
                <ChevronRight className="h-5 w-5 ml-2 flex-shrink-0" />
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
