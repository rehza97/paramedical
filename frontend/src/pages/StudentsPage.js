import React, { useEffect, useState } from "react";
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
  getPromotions,
  createPromotion,
  updatePromotion,
  deletePromotion,
  getSpecialities,
  getServices,
  getPromotionYears,
  getActivePromotionYear,
  activatePromotionYear,
  getPromotionYearServices,
  assignServiceToPromotionYear,
  removeServiceFromPromotionYear,
} from "../services/api";
import {
  Users,
  Plus,
  Search,
  GraduationCap,
  Calendar,
  Trash2,
  Edit,
  UserPlus,
  Settings,
  Building2,
  ChevronRight,
  Check,
  X,
} from "lucide-react";

const StudentsPage = () => {
  const [promotions, setPromotions] = useState([]);
  const [specialities, setSpecialities] = useState([]);
  const [services, setServices] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [studentsModalOpen, setStudentsModalOpen] = useState(false);
  const [yearServicesModalOpen, setYearServicesModalOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [promotionToDelete, setPromotionToDelete] = useState(null);
  const [selectedPromotionForStudents, setSelectedPromotionForStudents] =
    useState(null);
  const [planningSettings, setPlanningSettings] = useState({
    total_duration_months: 6, // Default fallback
  });

  // Missing state variables
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);
  const [newPromotion, setNewPromotion] = useState({
    nom: "",
    annee: new Date().getFullYear(),
    speciality_id: "",
    etudiants: [],
    yearServices: {},
  });
  const [newEtudiant, setNewEtudiant] = useState({ nom: "", prenom: "" });
  const [editingPromotion, setEditingPromotion] = useState(null);
  const [editEtudiant, setEditEtudiant] = useState({ nom: "", prenom: "" });
  const [selectedPromotion, setSelectedPromotion] = useState(null);
  const [promotionYears, setPromotionYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [yearServices, setYearServices] = useState([]);
  const [availableServices, setAvailableServices] = useState([]);
  const [serviceSearchTerms, setServiceSearchTerms] = useState({});
  const [showMoreServices, setShowMoreServices] = useState({});

  // Message context
  const { showMessage, message, type } = useMessage();

  // Computed values
  const filteredPromotions = promotions.filter(
    (promo) =>
      promo.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (promo.speciality &&
        promo.speciality.nom.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const totalStudents = promotions.reduce(
    (sum, promo) => sum + (promo.etudiants ? promo.etudiants.length : 0),
    0
  );

  // Load planning settings
  const loadPlanningSettings = async () => {
    try {
      console.log("Loading planning settings...");
      const response = await fetch(
        "http://localhost:8001/api/planning-settings/"
      );
      console.log("Planning settings response status:", response.status);

      if (response.ok) {
        const settings = await response.json();
        console.log("Loaded planning settings:", settings);
        setPlanningSettings(settings);
      } else {
        console.error("Failed to load planning settings:", response.status);
        // Keep default settings if API fails
        console.log("Using default planning settings");
      }
    } catch (error) {
      console.error("Erreur lors du chargement des paramètres:", error);
      // Keep default settings if API fails
      console.log("Using default planning settings due to error");
    }
  };

  useEffect(() => {
    loadPromotions();
    loadSpecialities();
    loadServices();
    loadPlanningSettings(); // Load planning settings on component mount
  }, []);

  const loadPromotions = async () => {
    try {
      const { data } = await getPromotions();
      setPromotions(data);
    } catch (error) {
      showMessage("Erreur lors du chargement des promotions", "error");
    }
  };

  const loadSpecialities = async () => {
    try {
      const { data } = await getSpecialities();
      setSpecialities(data);
    } catch (error) {
      showMessage("Erreur lors du chargement des spécialités", "error");
    }
  };

  const loadServices = async () => {
    try {
      const { data } = await getServices();
      setServices(data);
    } catch (error) {
      showMessage("Erreur lors du chargement des services", "error");
    }
  };

  const handleCreatePromotion = async () => {
    if (!newPromotion.nom.trim() || newPromotion.etudiants.length === 0) {
      showMessage(
        "Veuillez remplir le nom et ajouter au moins un étudiant",
        "error"
      );
      return;
    }

    try {
      setLoading(true);

      // Create the promotion first
      const promotionResponse = await createPromotion({
        nom: newPromotion.nom,
        annee: newPromotion.annee,
        speciality_id: newPromotion.speciality_id || null,
        etudiants: newPromotion.etudiants,
      });

      // If services were selected, assign them to the appropriate years
      if (Object.keys(newPromotion.yearServices).length > 0) {
        // Get the created promotion's years
        const yearsResponse = await getPromotionYears(
          promotionResponse.data.id
        );
        const promotionYears = yearsResponse.data;

        // Assign services to each year
        for (const [yearIndex, serviceIds] of Object.entries(
          newPromotion.yearServices
        )) {
          const yearNumber = parseInt(yearIndex);
          const targetYear = promotionYears.find(
            (year) => year.annee_niveau === yearNumber
          );

          if (targetYear && serviceIds.length > 0) {
            // Assign each service to this year
            for (const serviceId of serviceIds) {
              try {
                await assignServiceToPromotionYear(targetYear.id, serviceId);
              } catch (error) {
                console.warn(
                  `Failed to assign service ${serviceId} to year ${yearNumber}:`,
                  error
                );
              }
            }
          }
        }
      }

      showMessage("Promotion créée avec succès avec les services assignés");
      setNewPromotion({
        nom: "",
        annee: new Date().getFullYear(),
        speciality_id: "",
        etudiants: [],
        yearServices: {},
      });
      setModalOpen(false);
      loadPromotions();
    } catch (error) {
      showMessage("Erreur lors de la création de la promotion", "error");
    } finally {
      setLoading(false);
    }
  };

  const ajouterEtudiant = () => {
    if (!newEtudiant.nom.trim() || !newEtudiant.prenom.trim()) {
      showMessage("Veuillez remplir le nom et prénom de l'étudiant", "error");
      return;
    }
    const etudiant = {
      id: Date.now().toString(),
      nom: newEtudiant.nom.trim(),
      prenom: newEtudiant.prenom.trim(),
    };
    setNewPromotion((prev) => ({
      ...prev,
      etudiants: [...prev.etudiants, etudiant],
    }));
    setNewEtudiant({ nom: "", prenom: "" });
  };

  const supprimerEtudiant = (id) => {
    setNewPromotion((prev) => ({
      ...prev,
      etudiants: prev.etudiants.filter((e) => e.id !== id),
    }));
  };

  const handleDeletePromotion = async (id) => {
    setPromotionToDelete(id);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!promotionToDelete) return;

    try {
      setLoading(true);
      await deletePromotion(promotionToDelete);
      showMessage("Promotion supprimée avec succès");
      loadPromotions();
    } catch (error) {
      showMessage("Erreur lors de la suppression", "error");
    } finally {
      setLoading(false);
      setDeleteConfirmOpen(false);
      setPromotionToDelete(null);
    }
  };

  const openEditModal = (promotion) => {
    setEditingPromotion({
      id: promotion.id,
      nom: promotion.nom,
      annee: promotion.annee,
      speciality_id: promotion.speciality_id || "",
      etudiants: promotion.etudiants || [],
    });
    setEditEtudiant({ nom: "", prenom: "" });
    setEditModalOpen(true);
  };

  const handleEditPromotion = async () => {
    if (!editingPromotion.nom.trim()) {
      showMessage("Veuillez remplir le nom de la promotion", "error");
      return;
    }

    try {
      setLoading(true);
      await updatePromotion(editingPromotion.id, editingPromotion);
      showMessage("Promotion mise à jour avec succès");
      setEditModalOpen(false);
      loadPromotions();
    } catch (error) {
      showMessage("Erreur lors de la mise à jour", "error");
    } finally {
      setLoading(false);
    }
  };

  const ajouterEtudiantEdit = () => {
    if (!editEtudiant.nom.trim() || !editEtudiant.prenom.trim()) {
      showMessage("Veuillez remplir le nom et prénom de l'étudiant", "error");
      return;
    }
    const etudiant = {
      id: Date.now().toString(),
      nom: editEtudiant.nom.trim(),
      prenom: editEtudiant.prenom.trim(),
    };
    setEditingPromotion((prev) => ({
      ...prev,
      etudiants: [...prev.etudiants, etudiant],
    }));
    setEditEtudiant({ nom: "", prenom: "" });
  };

  const supprimerEtudiantEdit = (id) => {
    setEditingPromotion((prev) => ({
      ...prev,
      etudiants: prev.etudiants.filter((e) => e.id !== id),
    }));
  };

  const openStudentsModal = (promotion) => {
    setSelectedPromotionForStudents(promotion);
    setStudentsModalOpen(true);
  };

  const openModal = () => {
    setNewPromotion({
      nom: "",
      annee: new Date().getFullYear(),
      speciality_id: "",
      etudiants: [],
      yearServices: {},
    });
    setNewEtudiant({ nom: "", prenom: "" });
    setShowMoreServices({});
    setServiceSearchTerms({});
    setModalOpen(true);
  };

  // Service selection for years during creation
  const toggleServiceForYear = (yearNumber, serviceId) => {
    setNewPromotion((prev) => {
      const yearServices = { ...prev.yearServices };
      if (!yearServices[yearNumber]) {
        yearServices[yearNumber] = [];
      }

      const serviceIndex = yearServices[yearNumber].indexOf(serviceId);
      if (serviceIndex > -1) {
        // Remove service
        yearServices[yearNumber] = yearServices[yearNumber].filter(
          (id) => id !== serviceId
        );
        if (yearServices[yearNumber].length === 0) {
          delete yearServices[yearNumber];
        }
      } else {
        // Add service
        yearServices[yearNumber] = [...yearServices[yearNumber], serviceId];
      }

      return { ...prev, yearServices };
    });
  };

  const isServiceSelectedForYear = (yearNumber, serviceId) => {
    return newPromotion.yearServices[yearNumber]?.includes(serviceId) || false;
  };

  const getYearNumbers = () => {
    const selectedSpeciality = specialities.find(
      (s) => s.id === newPromotion.speciality_id
    );
    if (selectedSpeciality) {
      return Array.from(
        { length: selectedSpeciality.duree_annees },
        (_, i) => i + 1
      );
    }
    return [1]; // Default to 1 year if no speciality selected
  };

  const calculateTotalDuration = (yearNumber) => {
    const selectedServiceIds = newPromotion.yearServices[yearNumber] || [];
    return selectedServiceIds.reduce((total, serviceId) => {
      const service = services.find((s) => s.id === serviceId);
      return total + (service ? service.duree_stage_jours : 0);
    }, 0);
  };

  const calculateOverallTotalDuration = () => {
    const allYears = getYearNumbers();
    return allYears.reduce((total, yearNumber) => {
      return total + calculateTotalDuration(yearNumber);
    }, 0);
  };

  const formatDuration = (days) => {
    if (days === 0) return "0 jour";
    const months = Math.floor(days / 30);
    const remainingDays = days % 30;

    let result = "";
    if (months > 0) {
      result += `${months} mois`;
    }
    if (remainingDays > 0) {
      if (result) result += " ";
      result += `${remainingDays} jour${remainingDays > 1 ? "s" : ""}`;
    }
    return result;
  };

  // Promotion Years Management (existing functionality)
  const openYearServicesModal = async (promotion) => {
    setSelectedPromotion(promotion);
    try {
      setLoading(true);
      const yearsResponse = await getPromotionYears(promotion.id);
      setPromotionYears(yearsResponse.data);

      if (yearsResponse.data.length > 0) {
        const firstYear = yearsResponse.data[0];
        setSelectedYear(firstYear);
        const servicesResponse = await getPromotionYearServices(firstYear.id);
        setYearServices(servicesResponse.data);
      }

      setYearServicesModalOpen(true);
    } catch (error) {
      showMessage("Erreur lors du chargement des années de promotion", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectYear = async (year) => {
    setSelectedYear(year);
    try {
      setLoading(true);
      const { data } = await getPromotionYearServices(year.id);
      setYearServices(data);
    } catch (error) {
      showMessage("Erreur lors du chargement des services de l'année", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleAssignYearService = async (serviceId) => {
    if (!selectedYear) return;
    try {
      setLoading(true);
      await assignServiceToPromotionYear(selectedYear.id, serviceId);
      showMessage("Service assigné à l'année avec succès");
      const { data } = await getPromotionYearServices(selectedYear.id);
      setYearServices(data);
    } catch (error) {
      showMessage("Erreur lors de l'assignation du service", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveYearService = async (serviceId) => {
    if (!selectedYear) return;
    try {
      setLoading(true);
      await removeServiceFromPromotionYear(selectedYear.id, serviceId);
      showMessage("Service retiré de l'année avec succès");
      const { data } = await getPromotionYearServices(selectedYear.id);
      setYearServices(data);
    } catch (error) {
      showMessage("Erreur lors du retrait du service", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleActivateYear = async (yearId) => {
    try {
      setLoading(true);
      await activatePromotionYear(yearId);
      showMessage("Année activée avec succès");
      const yearsResponse = await getPromotionYears(selectedPromotion.id);
      setPromotionYears(yearsResponse.data);
    } catch (error) {
      showMessage("Erreur lors de l'activation de l'année", "error");
    } finally {
      setLoading(false);
    }
  };

  const isServiceSelectedInOtherYears = (yearNumber, serviceId) => {
    const allYears = getYearNumbers();
    return allYears.some((year) => {
      if (year !== yearNumber) {
        return newPromotion.yearServices[year]?.includes(serviceId) || false;
      }
      return false;
    });
  };

  const getServiceSelectionWarning = (yearNumber, serviceId) => {
    if (isServiceSelectedInOtherYears(yearNumber, serviceId)) {
      const yearWithService = getYearNumbers().find(
        (year) =>
          year !== yearNumber &&
          newPromotion.yearServices[year]?.includes(serviceId)
      );
      return `⚠️ Ce service est déjà sélectionné pour l'année ${yearWithService}`;
    }
    return null;
  };

  const toggleStudentStatus = async (promotionId, studentId) => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8001/api/promotions/${promotionId}/students/${studentId}/toggle-status`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const result = await response.json();
        // Reload promotions to get updated student status
        await loadPromotions();
        // Update the selected promotion for students modal
        const updatedPromotion = promotions.find((p) => p.id === promotionId);
        setSelectedPromotionForStudents(updatedPromotion);

        // Update editing promotion if it's the same one
        if (editingPromotion && editingPromotion.id === promotionId) {
          const updatedEditingPromotion = promotions.find(
            (p) => p.id === promotionId
          );
          setEditingPromotion(updatedEditingPromotion);
        }

        // Show success message
        console.log("Success:", result.message);
      } else {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Erreur lors du changement de statut"
        );
      }
    } catch (error) {
      console.error("Erreur:", error);
      alert(
        `Erreur lors du changement de statut de l'étudiant: ${error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const isDurationExcessive = (yearNumber) => {
    const duration = calculateTotalDuration(yearNumber);
    // Use dynamic planning settings instead of hardcoded 180 days
    const maxDurationDays = planningSettings.total_duration_months * 30; // Convert months to days

    console.log(`Duration check for year ${yearNumber}:`, {
      duration,
      maxDurationDays,
      planningSettings,
      isExcessive: duration > maxDurationDays,
    });

    return duration > maxDurationDays;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Gestion des Étudiants
          </h1>
          <p className="text-muted-foreground">
            Gérez vos promotions, étudiants et leurs services par année
          </p>
        </div>
        <Button onClick={openModal} className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Nouvelle Promotion</span>
        </Button>
      </div>

      <Message text={message} type={type} />

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Promotions
            </CardTitle>
            <GraduationCap className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{promotions.length}</div>
            <p className="text-xs text-muted-foreground">Classes actives</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Étudiants
            </CardTitle>
            <Users className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStudents}</div>
            <p className="text-xs text-muted-foreground">Étudiants inscrits</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Année Courante
            </CardTitle>
            <Calendar className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{new Date().getFullYear()}</div>
            <p className="text-xs text-muted-foreground">Année académique</p>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher une promotion ou spécialité..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Promotions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPromotions.map((promo) => (
          <Card key={promo.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{promo.nom}</CardTitle>
                  <div className="text-sm text-muted-foreground">
                    <span>Année {promo.annee}</span>
                    {promo.speciality && (
                      <Badge variant="secondary" className="ml-2">
                        {promo.speciality.nom}
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="flex space-x-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => openEditModal(promo)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive"
                    onClick={() => handleDeletePromotion(promo.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Étudiants</span>
                  <Badge variant="outline">
                    {promo.etudiants ? promo.etudiants.length : 0}
                  </Badge>
                </div>

                {promo.speciality && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Durée</span>
                    <span className="text-sm text-muted-foreground">
                      {promo.speciality.duree_annees} ans
                    </span>
                  </div>
                )}

                <div className="pt-2 border-t">
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => openStudentsModal(promo)}
                    >
                      <Users className="h-4 w-4 mr-1" />
                      Voir Étudiants
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => openYearServicesModal(promo)}
                    >
                      <Settings className="h-4 w-4 mr-1" />
                      Modifier Services
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredPromotions.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <GraduationCap className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">
              {searchTerm ? "Aucune promotion trouvée" : "Aucune promotion"}
            </h3>
            <p className="text-muted-foreground text-center mb-4">
              {searchTerm
                ? "Essayez de modifier votre recherche"
                : "Commencez par créer votre première promotion d'étudiants"}
            </p>
            {!searchTerm && (
              <Button
                onClick={openModal}
                className="flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>Créer une promotion</span>
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Create Promotion Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Créer une nouvelle promotion"
        size="large"
      >
        <div className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Nom de la promotion
              </label>
              <Input
                value={newPromotion.nom}
                onChange={(e) =>
                  setNewPromotion({ ...newPromotion, nom: e.target.value })
                }
                placeholder="Ex: Kinésithérapie 2024"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Année</label>
              <Input
                type="number"
                value={newPromotion.annee}
                onChange={(e) =>
                  setNewPromotion({ ...newPromotion, annee: e.target.value })
                }
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Spécialité</label>
            <select
              value={newPromotion.speciality_id}
              onChange={(e) =>
                setNewPromotion({
                  ...newPromotion,
                  speciality_id: e.target.value,
                  yearServices: {}, // Reset services when speciality changes
                })
              }
              className="w-full px-3 py-2 border border-input rounded-md"
            >
              <option value="">Sélectionner une spécialité (optionnel)</option>
              {specialities.map((speciality) => (
                <option key={speciality.id} value={speciality.id}>
                  {speciality.nom} ({speciality.duree_annees} ans)
                </option>
              ))}
            </select>
          </div>

          {/* Students Section */}
          <div className="border-t pt-4">
            <h4 className="font-medium mb-3 flex items-center">
              <UserPlus className="h-4 w-4 mr-2" />
              Ajouter des étudiants
            </h4>

            <div className="grid grid-cols-2 gap-2 mb-3">
              <Input
                placeholder="Nom"
                value={newEtudiant.nom}
                onChange={(e) =>
                  setNewEtudiant({ ...newEtudiant, nom: e.target.value })
                }
              />
              <Input
                placeholder="Prénom"
                value={newEtudiant.prenom}
                onChange={(e) =>
                  setNewEtudiant({ ...newEtudiant, prenom: e.target.value })
                }
              />
            </div>

            <Button
              onClick={ajouterEtudiant}
              variant="outline"
              className="w-full mb-3"
            >
              <Plus className="h-4 w-4 mr-2" />
              Ajouter l'étudiant
            </Button>

            <div className="max-h-32 overflow-y-auto border rounded-md">
              {newPromotion.etudiants.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">
                  Aucun étudiant ajouté
                </div>
              ) : (
                <div className="divide-y">
                  {newPromotion.etudiants.map((etudiant) => (
                    <div
                      key={etudiant.id}
                      className="flex items-center justify-between p-3"
                    >
                      <span className="text-sm">
                        {etudiant.nom} {etudiant.prenom}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => supprimerEtudiant(etudiant.id)}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Services Selection by Year */}
          {newPromotion.speciality_id && (
            <div className="border-t pt-4">
              <h4 className="font-medium mb-3 flex items-center">
                <Building2 className="h-4 w-4 mr-2" />
                Services par année de formation
              </h4>
              <p className="text-sm text-muted-foreground mb-4">
                Sélectionnez quelques services clés pour chaque année (vous
                pourrez en ajouter d'autres plus tard)
              </p>

              <div className="space-y-6">
                {getYearNumbers().map((yearNumber) => {
                  const searchTerm = serviceSearchTerms[yearNumber] || "";
                  const showMore = showMoreServices[yearNumber] || false;

                  const filteredServices = services.filter(
                    (service) =>
                      !isServiceSelectedForYear(yearNumber, service.id) &&
                      service.nom
                        .toLowerCase()
                        .includes(searchTerm.toLowerCase())
                  );

                  const displayedServices = showMore
                    ? filteredServices
                    : filteredServices.slice(0, 6);
                  const hasMoreServices = filteredServices.length > 6;

                  return (
                    <Card
                      key={yearNumber}
                      className={`border-l-4 ${
                        isDurationExcessive(yearNumber)
                          ? "border-l-red-500 bg-red-50"
                          : "border-l-blue-500"
                      }`}
                    >
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base flex items-center gap-2">
                          Année {yearNumber}
                          {isDurationExcessive(yearNumber) && (
                            <Badge variant="destructive" className="text-xs">
                              ⚠️ Durée excessive
                            </Badge>
                          )}
                        </CardTitle>
                        <CardDescription>
                          {newPromotion.yearServices[yearNumber]?.length || 0}{" "}
                          service(s) sélectionné(s) -{" "}
                          <span
                            className={
                              isDurationExcessive(yearNumber)
                                ? "text-red-600 font-medium"
                                : ""
                            }
                          >
                            {formatDuration(calculateTotalDuration(yearNumber))}
                          </span>
                          {isDurationExcessive(yearNumber) && (
                            <span className="text-red-600 text-xs block mt-1">
                              ⚠️ Plus de{" "}
                              {planningSettings.total_duration_months} mois pour
                              cette année
                            </span>
                          )}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        {/* Search for services */}
                        <div className="mb-4">
                          <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                              placeholder="Rechercher un service..."
                              className="pl-10"
                              value={searchTerm}
                              onChange={(e) => {
                                setServiceSearchTerms((prev) => ({
                                  ...prev,
                                  [yearNumber]: e.target.value,
                                }));
                              }}
                            />
                          </div>
                        </div>

                        {/* Selected services summary */}
                        {newPromotion.yearServices[yearNumber]?.length > 0 && (
                          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <p className="text-sm font-medium text-green-800 mb-2">
                              Services sélectionnés pour l'année {yearNumber}:
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {newPromotion.yearServices[yearNumber].map(
                                (serviceId) => {
                                  const service = services.find(
                                    (s) => s.id === serviceId
                                  );
                                  return service ? (
                                    <Badge
                                      key={serviceId}
                                      variant="secondary"
                                      className="text-xs bg-green-100 text-green-800 flex items-center gap-1"
                                    >
                                      {service.nom}
                                      <X
                                        className="h-3 w-3 cursor-pointer hover:text-red-600"
                                        onClick={() =>
                                          toggleServiceForYear(
                                            yearNumber,
                                            serviceId
                                          )
                                        }
                                      />
                                    </Badge>
                                  ) : null;
                                }
                              )}
                            </div>
                          </div>
                        )}

                        {/* Service selection grid */}
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                          {displayedServices.map((service) => {
                            const warningMessage = getServiceSelectionWarning(
                              yearNumber,
                              service.id
                            );
                            return (
                              <div
                                key={service.id}
                                className={`p-3 border rounded-lg cursor-pointer hover:border-primary hover:bg-primary/5 transition-all relative ${
                                  warningMessage
                                    ? "border-yellow-400 bg-yellow-50"
                                    : ""
                                }`}
                                onClick={() =>
                                  toggleServiceForYear(yearNumber, service.id)
                                }
                                title={warningMessage || ""}
                              >
                                <div className="flex items-center justify-between">
                                  <div className="flex-1">
                                    <p className="font-medium text-sm flex items-center gap-2">
                                      {service.nom}
                                      {warningMessage && (
                                        <span className="text-yellow-600 text-xs">
                                          ⚠️
                                        </span>
                                      )}
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                      {service.places_disponibles} places
                                      disponibles • {service.duree_stage_jours}{" "}
                                      jours
                                    </p>
                                    {warningMessage && (
                                      <p className="text-xs text-yellow-600 mt-1">
                                        {warningMessage}
                                      </p>
                                    )}
                                  </div>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    className="ml-2"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toggleServiceForYear(
                                        yearNumber,
                                        service.id
                                      );
                                    }}
                                  >
                                    <Plus className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>
                            );
                          })}
                        </div>

                        {/* Show more button */}
                        {hasMoreServices && !showMore && (
                          <div className="mt-3 text-center">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setShowMoreServices((prev) => ({
                                  ...prev,
                                  [yearNumber]: true,
                                }));
                              }}
                            >
                              Voir plus de services (
                              {filteredServices.length - 6} autres)
                            </Button>
                          </div>
                        )}

                        {/* Show less button */}
                        {showMore && (
                          <div className="mt-3 text-center">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setShowMoreServices((prev) => ({
                                  ...prev,
                                  [yearNumber]: false,
                                }));
                              }}
                            >
                              Voir moins de services
                            </Button>
                          </div>
                        )}

                        {/* Quick selection buttons */}
                        <div className="mt-4 pt-3 border-t">
                          <p className="text-xs text-muted-foreground mb-2">
                            Actions rapides:
                          </p>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                // Select first 3 available services
                                const availableServices = services.filter(
                                  (service) =>
                                    !isServiceSelectedForYear(
                                      yearNumber,
                                      service.id
                                    )
                                );
                                availableServices
                                  .slice(0, 3)
                                  .forEach((service) => {
                                    toggleServiceForYear(
                                      yearNumber,
                                      service.id
                                    );
                                  });
                              }}
                            >
                              Sélectionner 3 premiers
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                // Clear all selections for this year
                                setNewPromotion((prev) => {
                                  const yearServices = { ...prev.yearServices };
                                  delete yearServices[yearNumber];
                                  return { ...prev, yearServices };
                                });
                              }}
                            >
                              Tout effacer
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Overall summary */}
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h5 className="font-medium text-blue-900 mb-2">
                  Résumé de la sélection
                </h5>
                <div className="text-sm text-blue-800 space-y-2">
                  {getYearNumbers().map((yearNumber) => {
                    const count =
                      newPromotion.yearServices[yearNumber]?.length || 0;
                    const duration = calculateTotalDuration(yearNumber);
                    const isExcessive = isDurationExcessive(yearNumber);
                    return (
                      <div
                        key={yearNumber}
                        className={`flex justify-between items-center ${
                          isExcessive ? "text-red-700" : ""
                        }`}
                      >
                        <span className="flex items-center gap-2">
                          Année {yearNumber}:
                          {isExcessive && (
                            <span className="text-red-600 text-xs">⚠️</span>
                          )}
                        </span>
                        <div className="text-right">
                          <div className="font-medium">{count} service(s)</div>
                          <div
                            className={`text-xs ${
                              isExcessive
                                ? "text-red-600 font-medium"
                                : "text-blue-600"
                            }`}
                          >
                            {formatDuration(duration)}
                            {isExcessive && (
                              <span className="block text-xs text-red-600">
                                (Plus de{" "}
                                {planningSettings.total_duration_months} mois)
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  <div className="border-t border-blue-300 pt-2 mt-2">
                    <div className="flex justify-between items-center font-semibold">
                      <span>Total général:</span>
                      <div className="text-right">
                        <div>
                          {Object.values(newPromotion.yearServices).reduce(
                            (total, services) => total + services.length,
                            0
                          )}{" "}
                          service(s)
                        </div>
                        <div className="text-sm">
                          {formatDuration(calculateOverallTotalDuration())}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Show info message instead of warning */}
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-xs text-blue-800">
                    ℹ️ <strong>Note:</strong> Chaque année doit respecter la
                    limite de {planningSettings.total_duration_months} mois (
                    {planningSettings.total_duration_months * 30} jours) pour
                    une planification réaliste.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-2 pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => setModalOpen(false)}
              className="flex-1"
            >
              Annuler
            </Button>
            <Button
              onClick={handleCreatePromotion}
              disabled={
                newPromotion.etudiants.length === 0 ||
                !newPromotion.nom.trim() ||
                loading
              }
              className="flex-1"
            >
              {loading ? "Création..." : "Créer la promotion"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Year Services Management Modal (existing functionality) */}
      <Modal
        open={yearServicesModalOpen}
        onClose={() => setYearServicesModalOpen(false)}
        title={`Gestion des Services - ${selectedPromotion?.nom}`}
        size="large"
      >
        <div className="space-y-6">
          {/* Year Selection */}
          <div>
            <h4 className="font-medium mb-3 flex items-center">
              <Calendar className="h-4 w-4 mr-2" />
              Années de Formation
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {promotionYears.map((year) => (
                <Card
                  key={year.id}
                  className={`cursor-pointer transition-all ${
                    selectedYear?.id === year.id
                      ? "ring-2 ring-primary bg-primary/5"
                      : "hover:bg-muted/50"
                  }`}
                  onClick={() => handleSelectYear(year)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h5 className="font-medium">{year.nom}</h5>
                        <p className="text-sm text-muted-foreground">
                          {year.annee_calendaire}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {year.is_active && (
                          <Badge variant="default" className="text-xs">
                            Active
                          </Badge>
                        )}
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </div>
                    {!year.is_active && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="w-full mt-2"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleActivateYear(year.id);
                        }}
                      >
                        Activer cette année
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Services Management for Selected Year */}
          {selectedYear && (
            <div className="border-t pt-6">
              <h4 className="font-medium mb-3 flex items-center">
                <Building2 className="h-4 w-4 mr-2" />
                Services pour {selectedYear.nom} (
                {selectedYear.annee_calendaire})
              </h4>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Assigned Services */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">
                      Services Assignés
                    </CardTitle>
                    <CardDescription>
                      Services disponibles pour cette année
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {yearServices.length === 0 ? (
                      <div className="text-center py-6 text-muted-foreground">
                        <Building2 className="h-8 w-8 mx-auto mb-2" />
                        <p className="text-sm">Aucun service assigné</p>
                      </div>
                    ) : (
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {yearServices.map((service) => (
                          <div
                            key={service.id}
                            className="flex items-center justify-between p-3 bg-muted/30 rounded-lg"
                          >
                            <div>
                              <p className="font-medium text-sm">
                                {service.nom}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {service.places_disponibles} places •{" "}
                                {service.duree_stage_jours} jours
                              </p>
                            </div>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() =>
                                handleRemoveYearService(service.id)
                              }
                              className="text-destructive hover:text-destructive"
                              disabled={loading}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Available Services */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">
                      Services Disponibles
                    </CardTitle>
                    <CardDescription>
                      Cliquez pour assigner à cette année
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {services
                        .filter(
                          (service) =>
                            !yearServices.find((ys) => ys.id === service.id)
                        )
                        .map((service) => (
                          <div
                            key={service.id}
                            className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/30 transition-colors"
                          >
                            <div>
                              <p className="font-medium text-sm">
                                {service.nom}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {service.places_disponibles} places •{" "}
                                {service.duree_stage_jours} jours
                              </p>
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                handleAssignYearService(service.id)
                              }
                              disabled={loading}
                            >
                              <Plus className="h-4 w-4 mr-1" />
                              Assigner
                            </Button>
                          </div>
                        ))}
                    </div>
                    {services.filter(
                      (service) =>
                        !yearServices.find((ys) => ys.id === service.id)
                    ).length === 0 && (
                      <div className="text-center py-6 text-muted-foreground">
                        <Building2 className="h-8 w-8 mx-auto mb-2" />
                        <p className="text-sm">
                          Tous les services sont assignés
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </div>
      </Modal>

      {/* Students View Modal */}
      <Modal
        open={studentsModalOpen}
        onClose={() => setStudentsModalOpen(false)}
        title={`Étudiants - ${selectedPromotionForStudents?.nom}`}
        size="large"
      >
        <div className="space-y-4">
          {selectedPromotionForStudents?.etudiants?.length > 0 ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground mb-4">
                {selectedPromotionForStudents.etudiants.length} étudiant(s) dans
                cette promotion
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedPromotionForStudents.etudiants.map(
                  (etudiant, index) => (
                    <Card key={etudiant.id || index} className="p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium">
                              {etudiant.nom} {etudiant.prenom}
                            </p>
                            <Badge
                              variant={
                                etudiant.is_active !== false
                                  ? "default"
                                  : "secondary"
                              }
                              className={
                                etudiant.is_active !== false
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-600"
                              }
                            >
                              {etudiant.is_active !== false
                                ? "Actif"
                                : "Désactivé"}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Étudiant #{index + 1}
                            {etudiant.is_active === false &&
                              " • Exclu de la planification"}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              toggleStudentStatus(
                                selectedPromotionForStudents.id,
                                etudiant.id
                              )
                            }
                            className={
                              etudiant.is_active !== false
                                ? "text-red-600 hover:text-red-700"
                                : "text-green-600 hover:text-green-700"
                            }
                          >
                            {etudiant.is_active !== false
                              ? "Désactiver"
                              : "Activer"}
                          </Button>
                        </div>
                      </div>
                    </Card>
                  )
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                Aucun étudiant dans cette promotion
              </p>
            </div>
          )}
        </div>
      </Modal>

      {/* Edit Promotion Modal */}
      <Modal
        open={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Modifier la promotion"
        size="large"
      >
        {editingPromotion && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Nom de la promotion
                </label>
                <Input
                  value={editingPromotion.nom || ""}
                  onChange={(e) =>
                    setEditingPromotion({
                      ...editingPromotion,
                      nom: e.target.value,
                    })
                  }
                  placeholder="Ex: Kinésithérapie 2024"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Année</label>
                <Input
                  type="number"
                  value={editingPromotion.annee || ""}
                  onChange={(e) =>
                    setEditingPromotion({
                      ...editingPromotion,
                      annee: e.target.value,
                    })
                  }
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Spécialité
              </label>
              <select
                value={editingPromotion.speciality_id || ""}
                onChange={(e) =>
                  setEditingPromotion({
                    ...editingPromotion,
                    speciality_id: e.target.value,
                  })
                }
                className="w-full px-3 py-2 border border-input rounded-md"
              >
                <option value="">
                  Sélectionner une spécialité (optionnel)
                </option>
                {specialities.map((speciality) => (
                  <option key={speciality.id} value={speciality.id}>
                    {speciality.nom} ({speciality.duree_annees} ans)
                  </option>
                ))}
              </select>
            </div>

            <div className="border-t pt-4">
              <h4 className="font-medium mb-3 flex items-center">
                <UserPlus className="h-4 w-4 mr-2" />
                Gérer les étudiants
              </h4>

              <div className="grid grid-cols-2 gap-2 mb-3">
                <Input
                  placeholder="Nom"
                  value={editEtudiant.nom}
                  onChange={(e) =>
                    setEditEtudiant({ ...editEtudiant, nom: e.target.value })
                  }
                />
                <Input
                  placeholder="Prénom"
                  value={editEtudiant.prenom}
                  onChange={(e) =>
                    setEditEtudiant({ ...editEtudiant, prenom: e.target.value })
                  }
                />
              </div>

              <Button
                onClick={ajouterEtudiantEdit}
                variant="outline"
                className="w-full mb-3"
              >
                <Plus className="h-4 w-4 mr-2" />
                Ajouter l'étudiant
              </Button>

              <div className="max-h-32 overflow-y-auto border rounded-md">
                {(editingPromotion.etudiants || []).length === 0 ? (
                  <div className="p-4 text-center text-muted-foreground">
                    Aucun étudiant
                  </div>
                ) : (
                  <div className="divide-y">
                    {(editingPromotion.etudiants || []).map((etudiant) => (
                      <div
                        key={etudiant.id}
                        className="flex items-center justify-between p-3"
                      >
                        <div className="flex items-center gap-2 flex-1">
                          <span className="text-sm">
                            {etudiant.nom} {etudiant.prenom}
                          </span>
                          <Badge
                            variant={
                              etudiant.is_active !== false
                                ? "default"
                                : "secondary"
                            }
                            className={
                              etudiant.is_active !== false
                                ? "bg-green-100 text-green-800 text-xs"
                                : "bg-gray-100 text-gray-600 text-xs"
                            }
                          >
                            {etudiant.is_active !== false
                              ? "Actif"
                              : "Désactivé"}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              toggleStudentStatus(
                                editingPromotion.id,
                                etudiant.id
                              )
                            }
                            className={`text-xs px-2 py-1 ${
                              etudiant.is_active !== false
                                ? "text-orange-600 hover:text-orange-700"
                                : "text-green-600 hover:text-green-700"
                            }`}
                          >
                            {etudiant.is_active !== false
                              ? "Désactiver"
                              : "Activer"}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => supprimerEtudiantEdit(etudiant.id)}
                            className="text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex space-x-2 pt-4">
              <Button
                variant="outline"
                onClick={() => setEditModalOpen(false)}
                className="flex-1"
              >
                Annuler
              </Button>
              <Button
                onClick={handleEditPromotion}
                disabled={!editingPromotion.nom?.trim() || loading}
                className="flex-1"
              >
                {loading ? "Mise à jour..." : "Mettre à jour"}
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        title="Confirmer la suppression"
        size="small"
      >
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <Trash2 className="h-5 w-5 text-red-600" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-medium">Supprimer la promotion</h3>
              <p className="text-sm text-muted-foreground">
                Êtes-vous sûr de vouloir supprimer cette promotion ? Cette
                action est irréversible.
              </p>
            </div>
          </div>

          <div className="flex space-x-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setDeleteConfirmOpen(false)}
              className="flex-1"
            >
              Annuler
            </Button>
            <Button
              onClick={confirmDelete}
              disabled={loading}
              className="flex-1 bg-red-600 hover:bg-red-700"
            >
              {loading ? "Suppression..." : "Supprimer"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default StudentsPage;
