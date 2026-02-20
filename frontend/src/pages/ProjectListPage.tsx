import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, Film } from 'lucide-react';
import { useGetAllProjects } from '@/hooks/useQueries';
import CreateProjectDialog from '@/components/CreateProjectDialog';
import { Scale } from '@/backend';
import type { BudgetLevel } from '@/lib/types';

/**
 * Project List Page
 * 
 * Displays all film projects in a grid layout with key metadata.
 * Provides access to create new projects and navigate to project details.
 */
export default function ProjectListPage() {
  const navigate = useNavigate();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const { data: projects, isLoading } = useGetAllProjects();

  const getScaleLabel = (scale: Scale): string => {
    switch (scale) {
      case 'indie': return 'Indie';
      case 'studio': return 'Studio';
      case 'blockbuster': return 'Blockbuster';
      default: return 'Unknown';
    }
  };

  const getBudgetLabel = (budget: BudgetLevel): string => {
    switch (budget) {
      case 'low': return 'Low';
      case 'medium': return 'Medium';
      case 'high': return 'High';
      default: return 'Unknown';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Film Projects</h1>
          <p className="text-muted-foreground">
            Manage and track all your film projects across their lifecycle
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)} size="lg">
          <Plus className="h-5 w-5 mr-2" />
          New Project
        </Button>
      </div>

      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4 mb-2" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : projects && projects.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Card
              key={project.id.toString()}
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => navigate({ to: '/projects/$projectId', params: { projectId: project.id.toString() } })}
            >
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <Film className="h-5 w-5 text-primary" />
                  <Badge variant="outline">Phase {project.currentPhase.toString()}</Badge>
                </div>
                <CardTitle className="line-clamp-1">{project.title}</CardTitle>
                <CardDescription className="line-clamp-1">{project.genre}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Scale:</span>
                    <span className="font-medium">{getScaleLabel(project.scale)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Budget:</span>
                    <span className="font-medium">{getBudgetLabel(project.budgetLevel as BudgetLevel)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Language:</span>
                    <span className="font-medium">{project.language}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <Film className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No projects yet</h3>
          <p className="text-muted-foreground mb-6">
            Create your first film project to get started
          </p>
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="h-5 w-5 mr-2" />
            Create Project
          </Button>
        </div>
      )}

      <CreateProjectDialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen} />
    </div>
  );
}
