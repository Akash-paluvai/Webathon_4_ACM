import { createRouter, RouterProvider, createRoute, createRootRoute, Outlet } from '@tanstack/react-router';
import Navigation from './components/Navigation';
import LandingPage from './pages/LandingPage';
import ProjectListPage from './pages/ProjectListPage';
import ProjectOverviewPage from './pages/ProjectOverviewPage';
import Phase1Page from './pages/Phase1Page';
import Phase2Page from './pages/Phase2Page';
import Phase3Page from './pages/Phase3Page';
import Phase4Page from './pages/Phase4Page';
import Phase5Page from './pages/Phase5Page';
import Phase6Page from './pages/Phase6Page';
import Phase7Page from './pages/Phase7Page';
import Phase8Page from './pages/Phase8Page';

// Layout component that wraps all routes with navigation
function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-border bg-card py-6 mt-auto">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>
            © {new Date().getFullYear()} FilmFlow Studio. Built with love using{' '}
            <a
              href={`https://caffeine.ai/?utm_source=Caffeine-footer&utm_medium=referral&utm_content=${encodeURIComponent(
                typeof window !== 'undefined' ? window.location.hostname : 'filmflow-studio'
              )}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              caffeine.ai
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

// Root route with layout
const rootRoute = createRootRoute({
  component: Layout,
});

// Landing page route
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: LandingPage,
});

// Projects list route
const projectsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects',
  component: ProjectListPage,
});

// Project overview route
const projectOverviewRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId',
  component: ProjectOverviewPage,
});

// Phase routes
const phase1Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId/phase-1',
  component: Phase1Page,
});

const phase2Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId/phase-2',
  component: Phase2Page,
});

const phase3Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId/phase-3',
  component: Phase3Page,
});

const phase4Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId/phase-4',
  component: Phase4Page,
});

const phase5Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId/phase-5',
  component: Phase5Page,
});

const phase6Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId/phase-6',
  component: Phase6Page,
});

const phase7Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId/phase-7',
  component: Phase7Page,
});

const phase8Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/projects/$projectId/phase-8',
  component: Phase8Page,
});

// Create route tree
const routeTree = rootRoute.addChildren([
  indexRoute,
  projectsRoute,
  projectOverviewRoute,
  phase1Route,
  phase2Route,
  phase3Route,
  phase4Route,
  phase5Route,
  phase6Route,
  phase7Route,
  phase8Route,
]);

// Create router
const router = createRouter({ routeTree });

// Register router for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

export default function App() {
  return <RouterProvider router={router} />;
}
