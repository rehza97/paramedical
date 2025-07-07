import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { useMessage } from "../contexts/MessageContext";
import Message from "../components/Message";
import {
  getPromotions,
  getServices,
  getSpecialities,
  healthCheck,
} from "../services/api";
import {
  Users,
  Building2,
  GraduationCap,
  Calendar,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Plus,
} from "lucide-react";
import { Link } from "react-router-dom";

const DashboardPage = () => {
  const [stats, setStats] = useState({
    promotions: 0,
    students: 0,
    services: 0,
    specialities: 0,
    activeRotations: 0,
  });
  const [loading, setLoading] = useState(true);
  const [systemHealth, setSystemHealth] = useState(null);
  const { message, type, showMessage } = useMessage();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [promotionsRes, servicesRes, specialitiesRes, healthRes] =
        await Promise.all([
          getPromotions(),
          getServices(),
          getSpecialities(),
          healthCheck(),
        ]);

      const promotions = promotionsRes.data || [];
      const totalStudents = promotions.reduce(
        (sum, promo) => sum + (promo.etudiants ? promo.etudiants.length : 0),
        0
      );

      setStats({
        promotions: promotions.length,
        students: totalStudents,
        services: servicesRes.data?.length || 0,
        specialities: specialitiesRes.data?.length || 0,
        activeRotations: 0, // We'll calculate this from planning data later
      });

      setSystemHealth(healthRes.data);
    } catch (error) {
      showMessage("Erreur lors du chargement du tableau de bord", "error");
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({
    title,
    value,
    description,
    icon: Icon,
    color = "blue",
  }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 text-${color}-600`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{loading ? "..." : value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );

  const QuickAction = ({
    title,
    description,
    icon: Icon,
    to,
    variant = "outline",
  }) => (
    <Link to={to}>
      <Button
        variant={variant}
        className="w-full h-auto p-4 flex flex-col items-start space-y-2"
      >
        <div className="flex items-center space-x-2">
          <Icon className="h-5 w-5" />
          <span className="font-medium">{title}</span>
        </div>
        <span className="text-sm text-muted-foreground text-left">
          {description}
        </span>
      </Button>
    </Link>
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Tableau de Bord
          </h1>
          <p className="text-muted-foreground">
            Vue d'ensemble de votre système de gestion des stages
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {systemHealth && (
            <Badge
              variant={
                systemHealth.status === "healthy" ? "default" : "destructive"
              }
            >
              {systemHealth.status === "healthy" ? (
                <CheckCircle className="h-3 w-3 mr-1" />
              ) : (
                <AlertCircle className="h-3 w-3 mr-1" />
              )}
              {systemHealth.status === "healthy"
                ? "Système OK"
                : "Problème détecté"}
            </Badge>
          )}
        </div>
      </div>

      <Message text={message} type={type} />

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Promotions"
          value={stats.promotions}
          description="Classes actives"
          icon={GraduationCap}
          color="blue"
        />
        <StatCard
          title="Étudiants"
          value={stats.students}
          description="Total inscrits"
          icon={Users}
          color="green"
        />
        <StatCard
          title="Services"
          value={stats.services}
          description="Lieux de stage"
          icon={Building2}
          color="purple"
        />
        <StatCard
          title="Spécialités"
          value={stats.specialities}
          description="Filières disponibles"
          icon={TrendingUp}
          color="orange"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Plus className="h-5 w-5" />
              <span>Actions Rapides</span>
            </CardTitle>
            <CardDescription>
              Accès direct aux tâches les plus courantes
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <QuickAction
              title="Nouvelle Promotion"
              description="Créer une nouvelle classe d'étudiants"
              icon={Users}
              to="/students"
              variant="default"
            />
            <QuickAction
              title="Générer Planning"
              description="Créer un nouveau planning de stages"
              icon={Calendar}
              to="/planning"
            />
            <QuickAction
              title="Gérer Services"
              description="Ajouter ou modifier les services"
              icon={Building2}
              to="/settings"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Activité Récente</span>
            </CardTitle>
            <CardDescription>
              Dernières modifications du système
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Système démarré</p>
                  <p className="text-xs text-muted-foreground">
                    Il y a quelques minutes
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">
                    Base de données connectée
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Statut: Opérationnel
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5" />
              <span>Alertes</span>
            </CardTitle>
            <CardDescription>Notifications importantes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.promotions === 0 && (
                <div className="flex items-center space-x-3">
                  <AlertCircle className="h-4 w-4 text-yellow-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Aucune promotion</p>
                    <p className="text-xs text-muted-foreground">
                      Commencez par créer une promotion
                    </p>
                  </div>
                </div>
              )}
              {stats.services === 0 && (
                <div className="flex items-center space-x-3">
                  <AlertCircle className="h-4 w-4 text-yellow-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Aucun service</p>
                    <p className="text-xs text-muted-foreground">
                      Ajoutez des services de stage
                    </p>
                  </div>
                </div>
              )}
              {stats.promotions > 0 && stats.services > 0 && (
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Système prêt</p>
                    <p className="text-xs text-muted-foreground">
                      Vous pouvez générer des plannings
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Getting Started Guide */}
      {stats.promotions === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>🚀 Premiers pas</CardTitle>
            <CardDescription>
              Guide rapide pour configurer votre système de gestion des stages
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                  1
                </div>
                <div>
                  <h4 className="font-medium">Configurer les spécialités</h4>
                  <p className="text-sm text-muted-foreground">
                    Définissez les filières d'études (Kinésithérapie,
                    Orthophonie, etc.)
                  </p>
                  <Link to="/settings">
                    <Button variant="link" className="p-0 h-auto text-sm">
                      Aller aux paramètres →
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                  2
                </div>
                <div>
                  <h4 className="font-medium">Ajouter des services</h4>
                  <p className="text-sm text-muted-foreground">
                    Créez les lieux de stage avec leurs capacités d'accueil
                  </p>
                  <Link to="/settings">
                    <Button variant="link" className="p-0 h-auto text-sm">
                      Gérer les services →
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                  3
                </div>
                <div>
                  <h4 className="font-medium">Créer des promotions</h4>
                  <p className="text-sm text-muted-foreground">
                    Ajoutez vos classes d'étudiants avec leurs informations
                  </p>
                  <Link to="/students">
                    <Button variant="link" className="p-0 h-auto text-sm">
                      Gérer les étudiants →
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                  4
                </div>
                <div>
                  <h4 className="font-medium">Générer les plannings</h4>
                  <p className="text-sm text-muted-foreground">
                    Créez automatiquement les plannings de stage optimisés
                  </p>
                  <Link to="/planning">
                    <Button variant="link" className="p-0 h-auto text-sm">
                      Aller à la planification →
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DashboardPage;
