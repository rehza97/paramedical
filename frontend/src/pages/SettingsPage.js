import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { useMessage } from "../contexts/MessageContext";
import Message from "../components/Message";
import Modal from "../components/Modal";
import {
  getSpecialities,
  createSpeciality,
  updateSpeciality,
  deleteSpeciality,
  getServices,
  createService,
  updateService,
  deleteService,
  healthCheck,
  getPlanningSettings,
  updatePlanningSettings,
} from "../services/api";
import {
  Settings,
  Plus,
  Edit,
  Trash2,
  Building2,
  GraduationCap,
  Search,
  CheckCircle,
  AlertCircle,
  Database,
  Calendar,
  Clock,
  Users,
} from "lucide-react";

const SettingsPage = () => {
  const [specialities, setSpecialities] = useState([]);
  const [services, setServices] = useState([]);
  const [planningSettings, setPlanningSettings] = useState(null);
  const [selectedTab, setSelectedTab] = useState("specialities");
  const [searchTerm, setSearchTerm] = useState("");
  const [systemHealth, setSystemHealth] = useState(null);

  // Speciality modal state
  const [specialityModalOpen, setSpecialityModalOpen] = useState(false);
  const [editingSpeciality, setEditingSpeciality] = useState(null);
  const [specialityForm, setSpecialityForm] = useState({
    nom: "",
    description: "",
    duree_annees: 3,
  });

  // Service modal state
  const [serviceModalOpen, setServiceModalOpen] = useState(false);
  const [editingService, setEditingService] = useState(null);
  const [serviceForm, setServiceForm] = useState({
    nom: "",
    places_disponibles: 1,
    duree_stage_jours: 14,
    speciality_id: "",
  });

  const { message, type, showMessage, loading, setLoading } = useMessage();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [specialitiesRes, servicesRes, healthRes, planningRes] =
        await Promise.all([
          getSpecialities(),
          getServices(),
          healthCheck(),
          getPlanningSettings(),
        ]);
      setSpecialities(specialitiesRes.data || []);
      setServices(servicesRes.data || []);
      setSystemHealth(healthRes.data);
      setPlanningSettings(planningRes.data);
    } catch (error) {
      showMessage("Erreur lors du chargement des données", "error");
    }
  };

  // Speciality functions
  const handleCreateSpeciality = async () => {
    try {
      setLoading(true);
      if (editingSpeciality) {
        await updateSpeciality(editingSpeciality.id, specialityForm);
        showMessage("Spécialité mise à jour avec succès");
      } else {
        await createSpeciality(specialityForm);
        showMessage("Spécialité créée avec succès");
      }
      setSpecialityModalOpen(false);
      setEditingSpeciality(null);
      setSpecialityForm({ nom: "", description: "", duree_annees: 3 });
      loadData();
    } catch (error) {
      showMessage("Erreur lors de la sauvegarde", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleEditSpeciality = (speciality) => {
    setEditingSpeciality(speciality);
    setSpecialityForm({
      nom: speciality.nom,
      description: speciality.description || "",
      duree_annees: speciality.duree_annees,
    });
    setSpecialityModalOpen(true);
  };

  const handleDeleteSpeciality = async (id) => {
    if (
      window.confirm("Êtes-vous sûr de vouloir supprimer cette spécialité ?")
    ) {
      try {
        setLoading(true);
        await deleteSpeciality(id);
        showMessage("Spécialité supprimée avec succès");
        loadData();
      } catch (error) {
        showMessage("Erreur lors de la suppression", "error");
      } finally {
        setLoading(false);
      }
    }
  };

  // Planning Settings functions
  const handleUpdatePlanningSettings = async (formData) => {
    try {
      setLoading(true);
      const response = await updatePlanningSettings(formData);
      setPlanningSettings(response.data);
      showMessage("Configuration de planification mise à jour avec succès");
    } catch (error) {
      showMessage("Erreur lors de la mise à jour de la configuration", "error");
    } finally {
      setLoading(false);
    }
  };

  // Service functions
  const handleCreateService = async () => {
    try {
      setLoading(true);
      if (editingService) {
        await updateService(editingService.id, serviceForm);
        showMessage("Service mis à jour avec succès");
      } else {
        await createService(serviceForm);
        showMessage("Service créé avec succès");
      }
      setServiceModalOpen(false);
      setEditingService(null);
      setServiceForm({
        nom: "",
        places_disponibles: 1,
        duree_stage_jours: 14,
        speciality_id: "",
      });
      loadData();
    } catch (error) {
      showMessage("Erreur lors de la sauvegarde", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleEditService = (service) => {
    setEditingService(service);
    setServiceForm({
      nom: service.nom,
      places_disponibles: service.places_disponibles,
      duree_stage_jours: service.duree_stage_jours,
      speciality_id: service.speciality_id,
    });
    setServiceModalOpen(true);
  };

  const handleDeleteService = async (id) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce service ?")) {
      try {
        setLoading(true);
        await deleteService(id);
        showMessage("Service supprimé avec succès");
        loadData();
      } catch (error) {
        showMessage("Erreur lors de la suppression", "error");
      } finally {
        setLoading(false);
      }
    }
  };

  const filteredSpecialities = specialities.filter(
    (spec) =>
      spec.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (spec.description || "").toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredServices = services.filter((service) =>
    service.nom.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const TabButton = ({ id, label, icon: Icon, count }) => (
    <Button
      variant={selectedTab === id ? "default" : "ghost"}
      onClick={() => setSelectedTab(id)}
      className="flex items-center space-x-2"
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
      {count !== undefined && (
        <Badge variant="secondary" className="ml-1">
          {count}
        </Badge>
      )}
    </Button>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Configuration</h1>
          <p className="text-muted-foreground">
            Gérez les spécialités, services et paramètres système
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
              {systemHealth.status === "healthy" ? "Système OK" : "Problème"}
            </Badge>
          )}
        </div>
      </div>

      <Message text={message} type={type} />

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>État du Système</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  systemHealth?.status === "healthy"
                    ? "bg-green-500"
                    : "bg-red-500"
                }`}
              ></div>
              <div>
                <p className="font-medium">Base de données</p>
                <p className="text-sm text-muted-foreground">
                  {systemHealth?.status === "healthy"
                    ? "Connectée"
                    : "Déconnectée"}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <div>
                <p className="font-medium">API</p>
                <p className="text-sm text-muted-foreground">Opérationnelle</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <div>
                <p className="font-medium">Version</p>
                <p className="text-sm text-muted-foreground">1.0.0</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="flex space-x-1 bg-muted p-1 rounded-lg w-fit">
        <TabButton
          id="specialities"
          label="Spécialités"
          icon={GraduationCap}
          count={specialities.length}
        />
        <TabButton
          id="services"
          label="Services"
          icon={Building2}
          count={services.length}
        />
        <TabButton id="planning" label="Planification" icon={Calendar} />
        <TabButton id="system" label="Système" icon={Settings} />
      </div>

      {/* Content */}
      {selectedTab === "specialities" && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Spécialités</CardTitle>
                <CardDescription>
                  Gérez les filières d'études disponibles
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Rechercher..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <Button
                  onClick={() => {
                    setEditingSpeciality(null);
                    setSpecialityForm({
                      nom: "",
                      description: "",
                      duree_annees: 3,
                    });
                    setSpecialityModalOpen(true);
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Nouvelle Spécialité
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {filteredSpecialities.length === 0 ? (
              <div className="text-center py-8">
                <GraduationCap className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">Aucune spécialité</h3>
                <p className="text-muted-foreground mb-4">
                  Commencez par créer votre première spécialité
                </p>
                <Button
                  onClick={() => {
                    setEditingSpeciality(null);
                    setSpecialityForm({
                      nom: "",
                      description: "",
                      duree_annees: 3,
                    });
                    setSpecialityModalOpen(true);
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Créer une spécialité
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredSpecialities.map((speciality) => (
                  <Card
                    key={speciality.id}
                    className="hover:shadow-md transition-shadow"
                  >
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">
                            {speciality.nom}
                          </CardTitle>
                          <CardDescription>
                            {speciality.duree_annees} an
                            {speciality.duree_annees > 1 ? "s" : ""}
                          </CardDescription>
                        </div>
                        <div className="flex space-x-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => handleEditSpeciality(speciality)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive"
                            onClick={() =>
                              handleDeleteSpeciality(speciality.id)
                            }
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    {speciality.description && (
                      <CardContent className="pt-0">
                        <p className="text-sm text-muted-foreground">
                          {speciality.description}
                        </p>
                      </CardContent>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {selectedTab === "services" && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Services</CardTitle>
                <CardDescription>
                  Gérez les lieux de stage et leurs capacités
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Rechercher..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <Button
                  onClick={() => {
                    setEditingService(null);
                    setServiceForm({
                      nom: "",
                      places_disponibles: 1,
                      duree_stage_jours: 14,
                      speciality_id: "",
                    });
                    setServiceModalOpen(true);
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Nouveau Service
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {filteredServices.length === 0 ? (
              <div className="text-center py-8">
                <Building2 className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">Aucun service</h3>
                <p className="text-muted-foreground mb-4">
                  Ajoutez vos premiers services de stage
                </p>
                <Button
                  onClick={() => {
                    setEditingService(null);
                    setServiceForm({
                      nom: "",
                      places_disponibles: 1,
                      duree_stage_jours: 14,
                      speciality_id: "",
                    });
                    setServiceModalOpen(true);
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Créer un service
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredServices.map((service) => (
                  <Card
                    key={service.id}
                    className="hover:shadow-md transition-shadow"
                  >
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">
                            {service.nom}
                          </CardTitle>
                          <CardDescription>
                            {service.places_disponibles} place
                            {service.places_disponibles > 1 ? "s" : ""}
                          </CardDescription>
                        </div>
                        <div className="flex space-x-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => handleEditService(service)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive"
                            onClick={() => handleDeleteService(service.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Durée</span>
                        <Badge variant="outline">
                          {service.duree_stage_jours} jours
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {selectedTab === "planning" && (
        <Card>
          <CardHeader>
            <CardTitle>Configuration de Planification</CardTitle>
            <CardDescription>
              Paramètres pour la génération automatique des plannings
            </CardDescription>
          </CardHeader>
          <CardContent>
            {planningSettings && (
              <PlanningSettingsForm
                settings={planningSettings}
                onUpdate={handleUpdatePlanningSettings}
                loading={loading}
              />
            )}
          </CardContent>
        </Card>
      )}

      {selectedTab === "system" && (
        <Card>
          <CardHeader>
            <CardTitle>Paramètres Système</CardTitle>
            <CardDescription>
              Configuration avancée et maintenance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">Sauvegarde des données</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Exportez toutes vos données pour sauvegarde
                </p>
                <Button variant="outline">
                  <Database className="h-4 w-4 mr-2" />
                  Exporter les données
                </Button>
              </div>

              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">Maintenance</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Outils de maintenance et diagnostic
                </p>
                <div className="flex space-x-2">
                  <Button variant="outline" onClick={loadData}>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Tester la connexion
                  </Button>
                  <Button variant="outline">
                    <Settings className="h-4 w-4 mr-2" />
                    Logs système
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Speciality Modal */}
      <Modal
        open={specialityModalOpen}
        onClose={() => setSpecialityModalOpen(false)}
        title={
          editingSpeciality ? "Modifier la spécialité" : "Nouvelle spécialité"
        }
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nom</label>
            <Input
              value={specialityForm.nom}
              onChange={(e) =>
                setSpecialityForm({ ...specialityForm, nom: e.target.value })
              }
              placeholder="Ex: Kinésithérapie"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Description
            </label>
            <textarea
              value={specialityForm.description}
              onChange={(e) =>
                setSpecialityForm({
                  ...specialityForm,
                  description: e.target.value,
                })
              }
              className="w-full px-3 py-2 border border-input rounded-md"
              rows="3"
              placeholder="Description optionnelle..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Durée (années)
            </label>
            <select
              value={specialityForm.duree_annees}
              onChange={(e) =>
                setSpecialityForm({
                  ...specialityForm,
                  duree_annees: parseInt(e.target.value),
                })
              }
              className="w-full px-3 py-2 border border-input rounded-md"
            >
              <option value={3}>3 ans</option>
              <option value={4}>4 ans</option>
              <option value={5}>5 ans</option>
            </select>
          </div>

          <div className="flex space-x-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setSpecialityModalOpen(false)}
              className="flex-1"
            >
              Annuler
            </Button>
            <Button
              onClick={handleCreateSpeciality}
              disabled={loading}
              className="flex-1"
            >
              {editingSpeciality ? "Mettre à jour" : "Créer"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Service Modal */}
      <Modal
        open={serviceModalOpen}
        onClose={() => setServiceModalOpen(false)}
        title={editingService ? "Modifier le service" : "Nouveau service"}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Nom du service
            </label>
            <Input
              value={serviceForm.nom}
              onChange={(e) =>
                setServiceForm({ ...serviceForm, nom: e.target.value })
              }
              placeholder="Ex: Service de cardiologie"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Places disponibles
            </label>
            <Input
              type="number"
              value={serviceForm.places_disponibles}
              onChange={(e) =>
                setServiceForm({
                  ...serviceForm,
                  places_disponibles: parseInt(e.target.value),
                })
              }
              min="1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Durée du stage (jours)
            </label>
            <Input
              type="number"
              value={serviceForm.duree_stage_jours}
              onChange={(e) =>
                setServiceForm({
                  ...serviceForm,
                  duree_stage_jours: parseInt(e.target.value),
                })
              }
              min="1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Spécialité</label>
            <select
              value={serviceForm.speciality_id}
              onChange={(e) =>
                setServiceForm({
                  ...serviceForm,
                  speciality_id: e.target.value,
                })
              }
              className="w-full px-3 py-2 border border-input rounded-md"
            >
              <option value="">Sélectionner une spécialité</option>
              {specialities.map((speciality) => (
                <option key={speciality.id} value={speciality.id}>
                  {speciality.nom}
                </option>
              ))}
            </select>
          </div>

          <div className="flex space-x-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setServiceModalOpen(false)}
              className="flex-1"
            >
              Annuler
            </Button>
            <Button
              onClick={handleCreateService}
              disabled={loading}
              className="flex-1"
            >
              {editingService ? "Mettre à jour" : "Créer"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

// Planning Settings Form Component
const PlanningSettingsForm = ({ settings, onUpdate, loading }) => {
  const [formData, setFormData] = useState({
    academic_year_start: settings.academic_year_start || "2025-01-01",
    total_duration_months: settings.total_duration_months || 6,
    max_concurrent_students: settings.max_concurrent_students || 2,
    break_days_between_rotations: settings.break_days_between_rotations || 2,
    is_active: settings.is_active !== undefined ? settings.is_active : true,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate(formData);
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            <Calendar className="h-4 w-4 inline mr-2" />
            Date de début de l'année académique
          </label>
          <Input
            type="date"
            value={formData.academic_year_start}
            onChange={(e) =>
              handleChange("academic_year_start", e.target.value)
            }
            className="w-full"
          />
          <p className="text-xs text-muted-foreground mt-1">
            Date par défaut pour le début des plannings
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            <Clock className="h-4 w-4 inline mr-2" />
            Durée totale des stages (mois)
          </label>
          <Input
            type="number"
            min="1"
            max="12"
            value={formData.total_duration_months}
            onChange={(e) =>
              handleChange("total_duration_months", parseInt(e.target.value))
            }
            className="w-full"
          />
          <p className="text-xs text-muted-foreground mt-1">
            Durée maximale pour tous les stages d'un étudiant
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            <Users className="h-4 w-4 inline mr-2" />
            Étudiants maximum par service
          </label>
          <Input
            type="number"
            min="1"
            max="100"
            value={formData.max_concurrent_students}
            onChange={(e) =>
              handleChange("max_concurrent_students", parseInt(e.target.value))
            }
            className="w-full"
          />
          <p className="text-xs text-muted-foreground mt-1">
            Nombre maximum d'étudiants simultanément dans un service
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            <Calendar className="h-4 w-4 inline mr-2" />
            Jours de pause entre rotations
          </label>
          <Input
            type="number"
            min="0"
            max="20"
            value={formData.break_days_between_rotations}
            onChange={(e) =>
              handleChange(
                "break_days_between_rotations",
                parseInt(e.target.value)
              )
            }
            className="w-full"
          />
          <p className="text-xs text-muted-foreground mt-1">
            Jours de repos entre deux stages consécutifs
          </p>
        </div>
      </div>

      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">
          💡 Comment ça marche ?
        </h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>
            • La <strong>date de début</strong> sera utilisée par défaut pour
            tous les nouveaux plannings
          </li>
          <li>
            • La <strong>durée totale</strong> limite la période d'affectation
            des stages
          </li>
          <li>
            • Le <strong>nombre maximum d'étudiants</strong> évite la surcharge
            des services
          </li>
          <li>
            • Les <strong>jours de pause</strong> permettent aux étudiants de se
            reposer entre les stages
          </li>
        </ul>
      </div>

      <div className="flex justify-end space-x-3">
        <Button
          type="button"
          variant="outline"
          onClick={() =>
            setFormData({
              academic_year_start: settings.academic_year_start || "2025-01-01",
              total_duration_months: settings.total_duration_months || 6,
              max_concurrent_students: settings.max_concurrent_students || 2,
              break_days_between_rotations:
                settings.break_days_between_rotations || 2,
              is_active:
                settings.is_active !== undefined ? settings.is_active : true,
            })
          }
        >
          Réinitialiser
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? "Mise à jour..." : "Sauvegarder"}
        </Button>
      </div>
    </form>
  );
};

export default SettingsPage;
