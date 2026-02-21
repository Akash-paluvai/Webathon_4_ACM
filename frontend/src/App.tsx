import { createRouter, RouterProvider, createRoute, createRootRouteWithContext, Outlet, redirect } from '@tanstack/react-router';
import { useKindeAuth } from '@kinde-oss/kinde-auth-react';
import Navigation from './components/Navigation';
import ChatBot from './components/ChatBot';
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
import { Loader2 } from 'lucide-react';

// Define context type for the router
interface RouterContext {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => void;
}

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
            © 2026 Webathon 4.0. All rights reserved.
          </p>
        </div>
      </footer>
      <ChatBot />
    </div>
  );
}

// Root route with layout and context
const rootRoute = createRootRouteWithContext<RouterContext>()({
  component: Layout,
});

// Landing page route (public)
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: LandingPage,
});

// Authenticated parent route
const authenticatedRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'authenticated',
  beforeLoad: ({ context }) => {
    if (context.isLoading) return;
    if (!context.isAuthenticated) {
      context.login();
      throw redirect({ to: '/' });
    }
  },
});

// Protected project routes
const projectsRoute = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects',
  component: ProjectListPage,
});

const projectOverviewRoute = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId',
  component: ProjectOverviewPage,
});

// Phase routes (all protected)
const phase1Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId/phase-1',
  component: Phase1Page,
});

const phase2Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId/phase-2',
  component: Phase2Page,
});

const phase3Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId/phase-3',
  component: Phase3Page,
});

const phase4Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId/phase-4',
  component: Phase4Page,
});

const phase5Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId/phase-5',
  component: Phase5Page,
});

const phase6Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId/phase-6',
  component: Phase6Page,
});

const phase7Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId/phase-7',
  component: Phase7Page,
});

const phase8Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/projects/$projectId/phase-8',
  component: Phase8Page,
});

// Create route tree
const routeTree = rootRoute.addChildren([
  indexRoute,
  authenticatedRoute.addChildren([
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
  ]),
]);

// Create router
const router = createRouter({
  routeTree,
  context: {
    isAuthenticated: false,
    isLoading: true,
    login: () => { },
  },
});

// Register router for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

export default function App() {
  const { isAuthenticated, isLoading, login } = useKindeAuth();

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-background">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <RouterProvider
      router={router}
      context={{ isAuthenticated, isLoading, login }}
    />
  );
}
