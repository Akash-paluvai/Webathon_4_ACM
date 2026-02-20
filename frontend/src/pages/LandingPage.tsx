import { useNavigate } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Film, TrendingUp, Users, Award } from 'lucide-react';

/**
 * Landing Page
 * 
 * Entry point for the Film Producer Decision Support Platform.
 * Introduces the platform's value proposition and guides users to start working with projects.
 */
export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: 'url(/assets/generated/hero-bg.dim_1920x1080.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/70 to-background" />
        </div>
        
        <div className="relative z-10 container mx-auto px-4 py-24 md:py-32">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
              Data-Driven Film Production Decisions
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed">
              Navigate every phase of your film project with confidence. From script selection to post-release optimization, 
              make informed decisions backed by insights and analytics.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                onClick={() => navigate({ to: '/projects' })}
                className="text-lg px-8"
              >
                Get Started
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={() => navigate({ to: '/projects' })}
                className="text-lg px-8"
              >
                View Projects
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Complete Film Lifecycle Management
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Track and optimize every phase of your film project from concept to monetization
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Film className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">8-Phase Framework</h3>
              <p className="text-muted-foreground">
                Structured approach covering script selection, production, marketing, distribution, and post-release optimization.
              </p>
            </div>
            
            <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Data-Driven Insights</h3>
              <p className="text-muted-foreground">
                Make informed decisions with AI-powered recommendations and risk assessments at every stage.
              </p>
            </div>
            
            <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Award className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Unified Project Model</h3>
              <p className="text-muted-foreground">
                Single comprehensive project model that evolves through all phases, maintaining consistency and clarity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center bg-gradient-to-br from-primary/10 to-primary/5 rounded-2xl p-12 border border-primary/20">
            <Users className="h-12 w-12 text-primary mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">
              Ready to Transform Your Film Production?
            </h2>
            <p className="text-muted-foreground mb-8 text-lg">
              Start managing your film projects with a structured, data-driven approach today.
            </p>
            <Button
              size="lg"
              onClick={() => navigate({ to: '/projects' })}
              className="text-lg px-8"
            >
              Start Your First Project
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
