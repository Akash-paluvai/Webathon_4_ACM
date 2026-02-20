import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useCreateProject } from '@/hooks/useQueries';
import { Scale, TalentStrategy, AudienceType, MarketingBudgetLevel, PrimaryMarketingChannel, ReleaseModel, DistributionConfidence } from '@/backend';
import type { BudgetLevel } from '@/lib/types';

interface CreateProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/**
 * Create Project Dialog
 * 
 * Form for creating new film projects with initial metadata.
 * Calls backend createFilmProject method with required fields.
 */
export default function CreateProjectDialog({ open, onOpenChange }: CreateProjectDialogProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const createProject = useCreateProject();

  const [formData, setFormData] = useState({
    title: '',
    genre: '',
    language: '',
    theme: '',
    scale: 'indie' as Scale,
    budgetLevel: 'low' as BudgetLevel,
    talentStrategy: 'emerging' as TalentStrategy,
    plannedShootDays: '30',
    audienceType: 'broad' as AudienceType,
    marketingBudgetLevel: 'low' as MarketingBudgetLevel,
    primaryMarketingChannel: 'digitalAds' as PrimaryMarketingChannel,
    releaseModel: 'hybrid' as ReleaseModel,
    distributionConfidence: 'medium' as DistributionConfidence,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const projectId = await createProject.mutateAsync({
        title: formData.title,
        genre: formData.genre,
        language: formData.language,
        theme: formData.theme,
        scale: formData.scale,
        budgetLevel: formData.budgetLevel,
        talentStrategy: formData.talentStrategy,
        plannedShootDays: BigInt(formData.plannedShootDays),
        audienceType: formData.audienceType,
        marketingBudgetLevel: formData.marketingBudgetLevel,
        primaryMarketingChannel: formData.primaryMarketingChannel,
        releaseModel: formData.releaseModel,
        distributionConfidence: formData.distributionConfidence,
      });

      queryClient.invalidateQueries({ queryKey: ['projects'] });
      onOpenChange(false);
      navigate({ to: '/projects/$projectId', params: { projectId: projectId.toString() } });
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Film Project</DialogTitle>
          <DialogDescription>
            Enter the initial details for your film project. You can update these later.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Label htmlFor="title">Project Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter project title"
                required
              />
            </div>

            <div>
              <Label htmlFor="genre">Genre *</Label>
              <Input
                id="genre"
                value={formData.genre}
                onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                placeholder="e.g., Drama, Action"
                required
              />
            </div>

            <div>
              <Label htmlFor="language">Language *</Label>
              <Input
                id="language"
                value={formData.language}
                onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                placeholder="e.g., English, Hindi"
                required
              />
            </div>

            <div className="col-span-2">
              <Label htmlFor="theme">Theme *</Label>
              <Input
                id="theme"
                value={formData.theme}
                onChange={(e) => setFormData({ ...formData, theme: e.target.value })}
                placeholder="Main theme or concept"
                required
              />
            </div>

            <div>
              <Label htmlFor="scale">Scale *</Label>
              <Select value={formData.scale} onValueChange={(value) => setFormData({ ...formData, scale: value as Scale })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="indie">Indie</SelectItem>
                  <SelectItem value="studio">Studio</SelectItem>
                  <SelectItem value="blockbuster">Blockbuster</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="budgetLevel">Budget Level *</Label>
              <Select value={formData.budgetLevel} onValueChange={(value) => setFormData({ ...formData, budgetLevel: value as BudgetLevel })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="talentStrategy">Talent Strategy *</Label>
              <Select value={formData.talentStrategy} onValueChange={(value) => setFormData({ ...formData, talentStrategy: value as TalentStrategy })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="unknown_">Unknown</SelectItem>
                  <SelectItem value="emerging">Emerging</SelectItem>
                  <SelectItem value="established">Established</SelectItem>
                  <SelectItem value="starDriven">Star Driven</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="plannedShootDays">Planned Shoot Days *</Label>
              <Input
                id="plannedShootDays"
                type="number"
                value={formData.plannedShootDays}
                onChange={(e) => setFormData({ ...formData, plannedShootDays: e.target.value })}
                min="1"
                required
              />
            </div>

            <div>
              <Label htmlFor="audienceType">Audience Type *</Label>
              <Select value={formData.audienceType} onValueChange={(value) => setFormData({ ...formData, audienceType: value as AudienceType })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="niche">Niche</SelectItem>
                  <SelectItem value="broad">Broad</SelectItem>
                  <SelectItem value="mainstream">Mainstream</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="releaseModel">Release Model *</Label>
              <Select value={formData.releaseModel} onValueChange={(value) => setFormData({ ...formData, releaseModel: value as ReleaseModel })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="theatre">Theatre</SelectItem>
                  <SelectItem value="ott">OTT</SelectItem>
                  <SelectItem value="hybrid">Hybrid</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createProject.isPending}>
              {createProject.isPending ? 'Creating...' : 'Create Project'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
