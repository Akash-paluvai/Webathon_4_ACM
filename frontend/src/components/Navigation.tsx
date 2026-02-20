import { Link, useNavigate } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Film } from 'lucide-react';

/**
 * Navigation Component
 * 
 * Provides consistent navigation across the application.
 * 
 * ARCHITECTURE NOTE:
 * - This component provides access to the landing page and projects list
 * - Individual phase navigation (Phase 1-8) is available from project overview pages
 * - Each phase is independent and can be developed in parallel without modifying this core navigation
 * 
 * EXTENSION APPROACH:
 * - To add new top-level features, add links here
 * - Phase-specific features should be accessed through the project overview page
 * - Do NOT add phase-specific logic to this component
 */
export default function Navigation() {
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2 text-xl font-bold text-foreground hover:text-primary transition-colors">
              <Film className="h-6 w-6" />
              <span>FilmFlow Studio</span>
            </Link>
            <nav className="hidden md:flex items-center gap-6">
              <Link
                to="/"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Home
              </Link>
              <Link
                to="/projects"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Projects
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={() => navigate({ to: '/projects' })} variant="default">
              View Projects
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
