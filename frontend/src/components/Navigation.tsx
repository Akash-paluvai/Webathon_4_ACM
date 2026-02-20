import { Link, useNavigate } from '@tanstack/react-router';
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import { Button } from '@/components/ui/button';
import { Film, LogIn, LogOut, UserPlus } from 'lucide-react';

export default function Navigation() {
  const navigate = useNavigate();
  const { login, register, logout, isAuthenticated, user, isLoading } = useKindeAuth();

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
          <div className="flex items-center gap-3">
            {isLoading ? (
              <div className="h-9 w-24 rounded-md bg-muted animate-pulse" />
            ) : isAuthenticated ? (
              <>
                {user?.givenName && (
                  <span className="text-sm text-muted-foreground hidden sm:inline">
                    Hi, <span className="font-medium text-foreground">{user.givenName}</span>
                  </span>
                )}
                <Button onClick={() => navigate({ to: '/projects' })} variant="default" size="sm">
                  Projects
                </Button>
                <Button
                  onClick={() => logout()}
                  variant="outline"
                  size="sm"
                  className="gap-1.5"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button
                  onClick={() => login()}
                  variant="outline"
                  size="sm"
                  className="gap-1.5"
                >
                  <LogIn className="h-4 w-4" />
                  Login
                </Button>
                <Button
                  onClick={() => register()}
                  variant="default"
                  size="sm"
                  className="gap-1.5"
                >
                  <UserPlus className="h-4 w-4" />
                  Sign Up
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
