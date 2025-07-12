import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import DashboardPage from "./pages/DashboardPage";
import StudentsPage from "./pages/StudentsPage";
import PlanningPage from "./pages/PlanningPage";

import SettingsPage from "./pages/SettingsPage";
import ErrorBoundary from "./components/ErrorBoundary";
import {
  LayoutDashboard,
  Users,
  Calendar,
  Settings,
  GraduationCap,
  Brain,
} from "lucide-react";

function Navigation() {
  const location = useLocation();

  const navItems = [
    {
      path: "/",
      label: "Tableau de Bord",
      icon: LayoutDashboard,
      description: "Vue d'ensemble et statistiques",
    },
    {
      path: "/students",
      label: "Étudiants",
      icon: Users,
      description: "Gestion des étudiants et promotions",
    },
    {
      path: "/planning",
      label: "Planification",
      icon: Calendar,
      description: "Plannings et calendriers des stages",
    },

    {
      path: "/settings",
      label: "Configuration",
      icon: Settings,
      description: "Services, spécialités et paramètres",
    },
  ];

  return (
    <nav className="bg-background border-b border-border">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
              <GraduationCap className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">
                Gestion des Stages
              </h1>
              <p className="text-sm text-muted-foreground">
                Système de planification paramédicale
              </p>
            </div>
          </div>

          {/* Navigation Items */}
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link key={item.path} to={item.path}>
                  <Button
                    variant={isActive ? "default" : "ghost"}
                    className="flex items-center space-x-2 h-auto py-3 px-4"
                  >
                    <Icon className="h-4 w-4" />
                    <div className="flex flex-col items-start">
                      <span className="text-sm font-medium">{item.label}</span>
                      <span className="text-xs opacity-75">
                        {item.description}
                      </span>
                    </div>
                  </Button>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-background">
          <Navigation />
          <main className="max-w-7xl mx-auto py-8 px-4">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/students" element={<StudentsPage />} />
              <Route path="/planning" element={<PlanningPage />} />

              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<DashboardPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
