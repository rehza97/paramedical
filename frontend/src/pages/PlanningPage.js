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
import {
  generatePlanning,
  getPlanning,
  getPromotions,
  getPromotionYears,
  getActivePromotionYear,
  getStudentSchedules,
  getStudentScheduleDetail,
  updateRotation,
  exportPlanningExcel,
  validatePlanning,
} from "../services/api";
import {
  Calendar,
  Play,
  Users,
  Clock,
  FileText,
  Search,
  Filter,
  RotateCcw,
} from "lucide-react";

const PlanningPage = () => {
  const [promotions, setPromotions] = useState([]);
  const [selectedPromoId, setSelectedPromoId] = useState("");
  const [promotionYears, setPromotionYears] = useState([]);
  const [selectedYearId, setSelectedYearId] = useState("");
  const [activeYear, setActiveYear] = useState(null);
  const [planning, setPlanning] = useState(null);
  const [studentSchedules, setStudentSchedules] = useState([]);
  const [selectedView, setSelectedView] = useState("overview"); // overview, rotations, students
  const [searchTerm, setSearchTerm] = useState("");
  const { message, type, showMessage, loading, setLoading } = useMessage();
  const [promoLoading, setPromoLoading] = useState(false);
  const [planningLoading, setPlanningLoading] = useState(false);
  const [editingCell, setEditingCell] = useState(null);
  const [editingValue, setEditingValue] = useState("");
  const [allServices, setAllServices] = useState([]);
  const [allStudents, setAllStudents] = useState([]);
  const [validationResult, setValidationResult] = useState(null);
  const [validationLoading, setValidationLoading] = useState(false);
  const [allYearsMode, setAllYearsMode] = useState(false); // NEW: toggle for all years mode
  const [numberOfServices, setNumberOfServices] = useState(0); // NEW: service count
  const [numberOfStudents, setNumberOfStudents] = useState(0); // NEW: student count
  const [selectedTabYearId, setSelectedTabYearId] = useState(""); // NEW: year tab state
  const [allPlannings, setAllPlannings] = useState([]); // NEW: store all plannings for year switching

  useEffect(() => {
    const fetchPromos = async () => {
      setPromoLoading(true);
      try {
        const { data } = await getPromotions();
        setPromotions(data);
      } catch (e) {
        showMessage("Erreur lors du chargement des promotions", "error");
      } finally {
        setPromoLoading(false);
      }
    };
    fetchPromos();
  }, [showMessage]);

  useEffect(() => {
    const loadPromotionYears = async () => {
      if (!selectedPromoId) {
        setPromotionYears([]);
        setSelectedYearId("");
        setActiveYear(null);
        return;
      }

      try {
        const [yearsRes, activeRes] = await Promise.all([
          getPromotionYears(selectedPromoId),
          getActivePromotionYear(selectedPromoId),
        ]);
        setPromotionYears(yearsRes.data);
        setActiveYear(activeRes.data);

        if (activeRes.data) {
          setSelectedYearId(activeRes.data.id);
        } else if (yearsRes.data.length > 0) {
          setSelectedYearId(yearsRes.data[0].id);
        }
      } catch (error) {
        showMessage(
          "Erreur lors du chargement des années de promotion",
          "error"
        );
      }
    };

    loadPromotionYears();
  }, [selectedPromoId, showMessage]);

  // Load services and students for editing
  useEffect(() => {
    const loadEditingData = async () => {
      try {
        const [servicesResponse, studentsResponse] = await Promise.all([
          fetch("http://localhost:8001/api/services"),
          selectedPromoId
            ? fetch(`http://localhost:8001/api/promotions/${selectedPromoId}`)
            : null,
        ]);

        if (servicesResponse.ok) {
          const servicesData = await servicesResponse.json();
          setAllServices(servicesData);
        }

        if (studentsResponse && studentsResponse.ok) {
          const promoData = await studentsResponse.json();
          setAllStudents(promoData.etudiants || []);
        }
      } catch (error) {
        console.error("Error loading editing data:", error);
      }
    };

    loadEditingData();
  }, [selectedPromoId]);

  // Fetch validation results when planning changes
  useEffect(() => {
    const fetchValidation = async () => {
      if (!planning?.id) {
        setValidationResult(null);
        return;
      }
      setValidationLoading(true);
      try {
        const { data } = await validatePlanning(planning.id);
        setValidationResult(data);
      } catch (e) {
        setValidationResult(null);
      } finally {
        setValidationLoading(false);
      }
    };
    fetchValidation();
  }, [planning]);

  // Set default selectedTabYearId when promotionYears change
  useEffect(() => {
    if (promotionYears && promotionYears.length > 0) {
      const active = promotionYears.find((y) => y.is_active);
      setSelectedTabYearId(active ? active.id : promotionYears[0].id);
    }
  }, [promotionYears]);

  // Filtered rotations (no year filtering, just search)
  const filteredRotations =
    planning?.rotations?.filter(
      (rotation) =>
        rotation.etudiant_nom
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        rotation.service_nom?.toLowerCase().includes(searchTerm.toLowerCase())
    ) || [];

  // Filtered students (no year filtering, just search)
  const filteredStudents =
    studentSchedules?.filter(
      (schedule) =>
        schedule.etudiant_nom
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        schedule.etudiant_prenom
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase())
    ) || [];

  // Debug logs (moved after variable definitions)
  console.log("promotionYears:", promotionYears);
  console.log("selectedTabYearId:", selectedTabYearId);
  console.log("planning:", planning);
  console.log("studentSchedules:", studentSchedules);
  console.log("filteredRotations:", filteredRotations);
  console.log("filteredStudents:", filteredStudents);

  const selectedPromo = promotions.find((p) => p.id === selectedPromoId);
  const selectedYear = promotionYears.find((y) => y.id === selectedYearId);

  const handleGeneratePlanning = async () => {
    if (!selectedPromoId) {
      showMessage("Veuillez sélectionner une promotion", "error");
      return;
    }

    try {
      setLoading(true);
      // Pass allYearsMode to the API
      const { data } = await generatePlanning(
        selectedPromoId,
        "2025-01-01",
        allYearsMode
      );
      showMessage("Planning généré avec succès");
      // Save service and student counts from backend
      setNumberOfServices(data.number_of_services || 0);
      setNumberOfStudents(data.number_of_students || 0);

      // Handle the new response structure
      if (allYearsMode && data.plannings) {
        // Multiple plannings returned - use the first one or the one matching selected year
        const plannings = data.plannings;
        if (plannings.length > 0) {
          // Find planning for the selected year tab, or use the first one
          const selectedPlanning =
            plannings.find((p) => p.promotion_year_id === selectedTabYearId) ||
            plannings[0];
          setPlanning(selectedPlanning);
          setAllPlannings(plannings); // Store all plannings
        }
      } else {
        // Single planning returned (legacy behavior)
        setPlanning(data.planning);
      }

      // Then automatically load student schedules for better UX
      await handleLoadStudentSchedules();
      showMessage(
        "Planning et plannings individuels chargés avec succès",
        "success"
      );
    } catch (error) {
      showMessage("Erreur lors de la génération du planning", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadPlanning = async () => {
    if (!selectedPromoId) return;
    try {
      setPlanningLoading(true);
      const { data } = await getPlanning(selectedPromoId);
      setPlanning(data);
    } catch (error) {
      showMessage("Erreur lors du chargement du planning", "error");
    } finally {
      setPlanningLoading(false);
    }
  };

  const handleLoadStudentSchedules = async () => {
    if (!selectedPromoId) return;
    try {
      setPlanningLoading(true);

      // First try to get existing schedules
      let response;
      try {
        response = await fetch(
          `http://localhost:8001/api/student-schedules/promotion/${selectedPromoId}`
        );
      } catch (error) {
        response = await fetch(
          `http://localhost:8000/api/student-schedules/promotion/${selectedPromoId}`
        );
      }

      if (response.ok) {
        const data = await response.json();

        // Check if students have schedules or if we need to generate them
        const hasSchedules = data.some(
          (schedule) => schedule.id && schedule.id !== ""
        );

        if (!hasSchedules) {
          // Generate schedules from rotations first
          try {
            const generateResponse = await fetch(
              `http://localhost:8001/api/student-schedules/generate-from-rotations/${selectedPromoId}`,
              { method: "POST" }
            );

            if (generateResponse.ok) {
              // Reload schedules after generation
              const reloadResponse = await fetch(
                `http://localhost:8001/api/student-schedules/promotion/${selectedPromoId}`
              );
              if (reloadResponse.ok) {
                const reloadData = await reloadResponse.json();
                setStudentSchedules(reloadData);
                showMessage("Plannings individuels générés avec succès");
              }
            } else {
              setStudentSchedules(data); // Use empty schedules
              showMessage(
                "Aucun planning trouvé - générez d'abord un planning général",
                "error"
              );
            }
          } catch (genError) {
            setStudentSchedules(data); // Use empty schedules
            showMessage(
              "Impossible de générer les plannings individuels",
              "error"
            );
          }
        } else {
          setStudentSchedules(data);
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      showMessage("Erreur lors du chargement des plannings étudiants", "error");
      setStudentSchedules([]);
    } finally {
      setPlanningLoading(false);
    }
  };

  // Handle double-click to edit cell
  const handleCellDoubleClick = (rotation, field, value) => {
    setEditingCell({ rotationId: rotation.id, field });
    setEditingValue(value);
  };

  // Handle save edit
  const handleSaveEdit = async () => {
    if (!editingCell) return;

    try {
      const { rotationId, field } = editingCell;
      const updateData = { [field]: editingValue };

      await updateRotation(rotationId, updateData);

      // Reload the planning to get updated names
      await handleLoadPlanning();

      setEditingCell(null);
      setEditingValue("");
      showMessage("Rotation mise à jour avec succès", "success");
    } catch (error) {
      showMessage("Erreur lors de la mise à jour", "error");
    }
  };

  // Handle cancel edit
  const handleCancelEdit = () => {
    setEditingCell(null);
    setEditingValue("");
  };

  // Handle key press in edit mode
  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSaveEdit();
    } else if (e.key === "Escape") {
      handleCancelEdit();
    }
  };

  // Render editable cell
  const renderEditableCell = (rotation, field, value, displayValue = value) => {
    const isEditing =
      editingCell?.rotationId === rotation.id && editingCell?.field === field;

    if (isEditing) {
      if (field === "etudiant_id") {
        return (
          <select
            value={editingValue}
            onChange={(e) => setEditingValue(e.target.value)}
            onBlur={handleSaveEdit}
            onKeyDown={handleKeyPress}
            autoFocus
            className="w-full px-2 py-1 border rounded text-sm"
          >
            <option value="">Sélectionner un étudiant</option>
            {allStudents?.map((student) => (
              <option key={student.id} value={student.id}>
                {student.prenom} {student.nom}
              </option>
            ))}
          </select>
        );
      } else if (field === "service_id") {
        return (
          <select
            value={editingValue}
            onChange={(e) => setEditingValue(e.target.value)}
            onBlur={handleSaveEdit}
            onKeyDown={handleKeyPress}
            autoFocus
            className="w-full px-2 py-1 border rounded text-sm"
          >
            <option value="">Sélectionner un service</option>
            {allServices?.map((service) => (
              <option key={service.id} value={service.id}>
                {service.nom}
              </option>
            ))}
          </select>
        );
      } else if (field === "date_debut" || field === "date_fin") {
        return (
          <input
            type="date"
            value={editingValue}
            onChange={(e) => setEditingValue(e.target.value)}
            onBlur={handleSaveEdit}
            onKeyDown={handleKeyPress}
            autoFocus
            className="w-full px-2 py-1 border rounded text-sm"
          />
        );
      } else if (field === "ordre") {
        return (
          <input
            type="number"
            value={editingValue}
            onChange={(e) => setEditingValue(e.target.value)}
            onBlur={handleSaveEdit}
            onKeyDown={handleKeyPress}
            autoFocus
            className="w-full px-2 py-1 border rounded text-sm"
            min="1"
          />
        );
      }
    }

    return (
      <div
        onDoubleClick={() => handleCellDoubleClick(rotation, field, value)}
        className="cursor-pointer hover:bg-gray-100 p-2 rounded transition-colors"
        title="Double-cliquez pour modifier"
      >
        {displayValue}
      </div>
    );
  };

  const ViewTabs = () => (
    <div className="flex space-x-1 bg-muted p-1 rounded-lg">
      <Button
        variant={selectedView === "overview" ? "default" : "ghost"}
        size="sm"
        onClick={() => setSelectedView("overview")}
      >
        Vue d'ensemble
      </Button>
      <Button
        variant={selectedView === "rotations" ? "default" : "ghost"}
        size="sm"
        onClick={() => setSelectedView("rotations")}
      >
        Rotations
      </Button>
      <Button
        variant={selectedView === "students" ? "default" : "ghost"}
        size="sm"
        onClick={() => setSelectedView("students")}
      >
        Étudiants
      </Button>
    </div>
  );

  // Year Tabs component
  const YearTabs = () => {
    if (!allYearsMode || !promotionYears || promotionYears.length === 0) {
      return null;
    }

    return (
      <div className="flex space-x-2 mb-4">
        {promotionYears?.map((year) => (
          <button
            key={year.id}
            className={`px-4 py-2 rounded ${
              selectedTabYearId === year.id
                ? "bg-blue-600 text-white"
                : "bg-gray-200"
            }`}
            onClick={() => {
              setSelectedTabYearId(year.id);
              if (allYearsMode && allPlannings.length > 0) {
                const selectedPlanning = allPlannings.find(
                  (p) => p.promotion_year_id === year.id
                );
                if (selectedPlanning) {
                  setPlanning(selectedPlanning);
                } else {
                  // Fallback to default if no planning found for this year
                  setPlanning(null);
                  showMessage(
                    `Aucun planning trouvé pour l'année ${year.nom}. Générez-en un d'abord.`,
                    "warning"
                  );
                }
              }
            }}
          >
            {year.nom}
          </button>
        ))}
      </div>
    );
  };

  // Handle export to Excel
  const handleExportExcel = async () => {
    if (!selectedPromoId) {
      showMessage("Veuillez sélectionner une promotion", "error");
      return;
    }

    try {
      setLoading(true);
      const response = await exportPlanningExcel(selectedPromoId);

      // Create blob and download
      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      // Generate filename with promotion name and current date
      const currentDate = new Date()
        .toISOString()
        .slice(0, 10)
        .replace(/-/g, "");
      const promotionName =
        selectedPromo?.nom?.replace(/\s+/g, "_") || "planning";
      link.download = `planning_${promotionName}_${currentDate}.xlsx`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      showMessage("Planning exporté avec succès", "success");
    } catch (error) {
      showMessage("Erreur lors de l'export", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Planification des Stages
          </h1>
          <p className="text-muted-foreground">
            Gérez et visualisez les plannings de rotation
          </p>
        </div>
        <ViewTabs />
      </div>

      <Message text={message} type={type} />

      {/* Warnings & Conflicts Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>⚠️ Warnings & Conflicts</CardTitle>
        </CardHeader>
        <CardContent>
          {validationLoading ? (
            <p>Vérification des anomalies...</p>
          ) : validationResult &&
            (validationResult.erreurs?.length > 0 ||
              validationResult.warnings?.length > 0) ? (
            <ul className="space-y-1">
              {validationResult.erreurs?.map((err, idx) => (
                <li key={"err-" + idx} className="text-red-600">
                  ❌ {err}
                </li>
              ))}
              {validationResult.warnings?.map((warn, idx) => (
                <li key={"warn-" + idx} className="text-yellow-600">
                  ⚠️ {warn}
                </li>
              ))}
            </ul>
          ) : validationResult ? (
            <p className="text-green-600">
              Aucune anomalie détectée. Toutes les rotations sont valides !
            </p>
          ) : (
            <p className="text-muted-foreground">
              Aucune donnée de validation disponible.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Selection Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="h-5 w-5" />
            <span>Sélection</span>
          </CardTitle>
          <CardDescription>
            Choisissez la promotion et l'année pour travailler
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Promotion
              </label>
              <select
                value={selectedPromoId}
                onChange={(e) => setSelectedPromoId(e.target.value)}
                className="w-full px-3 py-2 border border-input rounded-md"
                disabled={promoLoading}
              >
                <option value="">
                  {promoLoading
                    ? "Chargement..."
                    : "Sélectionner une promotion"}
                </option>
                {promotions?.map((promo) => (
                  <option key={promo.id} value={promo.id}>
                    {promo.nom} ({promo.annee}
                    {promo.speciality ? `, ${promo.speciality.nom}` : ""})
                  </option>
                ))}
              </select>
            </div>

            {selectedPromoId && (
              <div>
                <label className="block text-sm font-medium mb-2">Année</label>
                <select
                  value={selectedYearId}
                  onChange={(e) => setSelectedYearId(e.target.value)}
                  className="w-full px-3 py-2 border border-input rounded-md"
                  disabled={!promotionYears || promotionYears.length === 0}
                >
                  <option value="">
                    {!promotionYears || promotionYears.length === 0
                      ? "Chargement..."
                      : "Sélectionner une année"}
                  </option>
                  {promotionYears?.map((year) => (
                    <option key={year.id} value={year.id}>
                      {year.nom} ({year.annee_calendaire})
                      {year.is_active ? " - Active" : ""}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="flex items-end">
              <div className="flex space-x-2 w-full">
                <Button
                  onClick={handleGeneratePlanning}
                  disabled={!selectedPromoId || loading}
                  className="flex-1"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Générer
                </Button>
                <Button
                  onClick={handleLoadPlanning}
                  disabled={!selectedPromoId || loading}
                  variant="outline"
                  className="flex-1"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Charger
                </Button>
              </div>
            </div>
          </div>
          {/* NEW: Toggle for all years mode */}
          <div className="mt-4 flex items-center space-x-2">
            <input
              type="checkbox"
              id="allYearsMode"
              checked={allYearsMode}
              onChange={() => setAllYearsMode((v) => !v)}
              className="form-checkbox h-4 w-4 text-blue-600"
            />
            <label htmlFor="allYearsMode" className="text-sm">
              Planifier pour toutes les années (active et inactives)
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Promotion Info */}
      {selectedPromo && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <span className="text-sm font-medium text-muted-foreground">
                  Promotion
                </span>
                <p className="text-lg font-semibold">{selectedPromo.nom}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-muted-foreground">
                  Année
                </span>
                <p className="text-lg font-semibold">{selectedPromo.annee}</p>
              </div>
              {selectedPromo.speciality && (
                <div>
                  <span className="text-sm font-medium text-muted-foreground">
                    Spécialité
                  </span>
                  <p className="text-lg font-semibold">
                    {selectedPromo.speciality.nom}
                  </p>
                </div>
              )}
              {selectedYear && (
                <div>
                  <span className="text-sm font-medium text-muted-foreground">
                    Année sélectionnée
                  </span>
                  <div className="flex items-center space-x-2">
                    <p className="text-lg font-semibold">{selectedYear.nom}</p>
                    {selectedYear.is_active && (
                      <Badge variant="default">Active</Badge>
                    )}
                  </div>
                </div>
              )}
            </div>
            {/* NEW: Service and student counts */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div>
                <span className="text-sm font-medium text-muted-foreground">
                  Services sélectionnés
                </span>
                <p className="text-lg font-semibold">{numberOfServices}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-muted-foreground">
                  Étudiants dans la promotion
                </span>
                <p className="text-lg font-semibold">{numberOfStudents}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Content based on selected view */}
      {selectedView === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {allYearsMode && (
            <div className="col-span-full">
              <Card className="border-blue-200 bg-blue-50">
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    <p className="text-sm text-blue-800">
                      Mode multi-années activé : Le planning sera généré pour
                      toutes les années de la promotion. Utilisez les onglets
                      d'année pour naviguer entre les différents plannings.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Rotations
              </CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {planning?.rotations?.length || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Rotations planifiées
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Étudiants</CardTitle>
              <Users className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {selectedPromo?.etudiants?.length || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Dans cette promotion
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Actions</CardTitle>
              <FileText className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Button
                  onClick={handleLoadStudentSchedules}
                  disabled={!selectedPromoId}
                  variant="outline"
                  size="sm"
                  className="w-full"
                >
                  <Users className="h-4 w-4 mr-2" />
                  Plannings Étudiants
                </Button>
                <Button
                  onClick={handleExportExcel}
                  disabled={!selectedPromoId || !planning}
                  variant="outline"
                  size="sm"
                  className="w-full"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Exporter Excel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {selectedView === "rotations" && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Rotations de Stage</CardTitle>
                <CardDescription>
                  Liste détaillée de toutes les rotations - Double-cliquez pour
                  modifier
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
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <YearTabs /> {/* NEW: year tabs above table */}
            {planningLoading ? (
              <div className="text-center text-muted-foreground py-8">
                <Clock className="h-8 w-8 mx-auto mb-2 animate-spin" />
                Chargement du planning...
              </div>
            ) : filteredRotations.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left p-2 font-medium">Étudiant</th>
                      <th className="text-left p-2 font-medium">Service</th>
                      <th className="text-left p-2 font-medium">Date début</th>
                      <th className="text-left p-2 font-medium">Date fin</th>
                      <th className="text-left p-2 font-medium">Rotation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {filteredRotations.map((rotation, i) => (
                      <tr
                        key={rotation.id || `rotation-${i}`}
                        className="hover:bg-muted/50"
                      >
                        <td className="p-0">
                          {renderEditableCell(
                            rotation,
                            "etudiant_id",
                            rotation.etudiant_id,
                            rotation.etudiant_nom
                          )}
                        </td>
                        <td className="p-0">
                          {renderEditableCell(
                            rotation,
                            "service_id",
                            rotation.service_id,
                            rotation.service_nom
                          )}
                        </td>
                        <td className="p-0">
                          {renderEditableCell(
                            rotation,
                            "date_debut",
                            rotation.date_debut
                          )}
                        </td>
                        <td className="p-0">
                          {renderEditableCell(
                            rotation,
                            "date_fin",
                            rotation.date_fin
                          )}
                        </td>
                        <td className="p-0">
                          {renderEditableCell(
                            rotation,
                            "ordre",
                            rotation.ordre,
                            <Badge variant="outline">#{rotation.ordre}</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                <Calendar className="h-8 w-8 mx-auto mb-2" />
                Aucune rotation trouvée
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {selectedView === "students" && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Plannings Étudiants</CardTitle>
                <CardDescription>
                  Vue individuelle des plannings par étudiant avec résumé
                  détaillé
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Rechercher un étudiant..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <Button
                  onClick={handleLoadStudentSchedules}
                  disabled={!selectedPromoId}
                  variant="outline"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Actualiser
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <YearTabs /> {/* NEW: year tabs above students */}
            {planningLoading ? (
              <div className="text-center text-muted-foreground py-8">
                <Clock className="h-8 w-8 mx-auto mb-2 animate-spin" />
                Chargement des plannings étudiants...
              </div>
            ) : filteredStudents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredStudents.map((schedule, index) => {
                  // Calculate student statistics from rotations
                  const studentRotations =
                    planning?.rotations?.filter(
                      (r) => r.etudiant_id === schedule.etudiant_id
                    ) || [];

                  const totalServices = studentRotations?.length || 0;
                  const totalDuration =
                    studentRotations?.reduce((sum, rotation) => {
                      const start = new Date(rotation.date_debut);
                      const end = new Date(rotation.date_fin);
                      return (
                        sum + Math.ceil((end - start) / (1000 * 60 * 60 * 24))
                      );
                    }, 0) || 0;

                  // Calculate breaks between rotations
                  const sortedRotations = [...(studentRotations || [])].sort(
                    (a, b) => new Date(a.date_debut) - new Date(b.date_debut)
                  );

                  let totalBreakDays = 0;
                  for (let i = 1; i < sortedRotations.length; i++) {
                    const prevEnd = new Date(sortedRotations[i - 1].date_fin);
                    const currentStart = new Date(
                      sortedRotations[i].date_debut
                    );
                    const breakDays =
                      Math.ceil(
                        (currentStart - prevEnd) / (1000 * 60 * 60 * 24)
                      ) - 1;
                    if (breakDays > 0) totalBreakDays += breakDays;
                  }

                  const formatDuration = (days) => {
                    const months = Math.floor(days / 30);
                    const remainingDays = days % 30;
                    if (months > 0) {
                      return `${months} mois ${remainingDays} jours`;
                    }
                    return `${remainingDays} jours`;
                  };

                  return (
                    <Card
                      key={
                        schedule.id ||
                        `student-${schedule.etudiant_nom}-${schedule.etudiant_prenom}-${index}`
                      }
                      className="hover:shadow-md transition-shadow"
                    >
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="text-lg">
                              {schedule.etudiant_nom} {schedule.etudiant_prenom}
                            </CardTitle>
                            <CardDescription>
                              {selectedPromo?.nom} -{" "}
                              {selectedPromo?.speciality?.nom}
                            </CardDescription>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {totalServices} services
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                          {/* Services Count */}
                          <div className="text-center p-3 bg-blue-50 rounded-lg">
                            <div className="text-2xl font-bold text-blue-600">
                              {totalServices}
                            </div>
                            <div className="text-xs text-blue-700">
                              🔵 Services assignés
                            </div>
                          </div>

                          {/* Total Duration */}
                          <div className="text-center p-3 bg-green-50 rounded-lg">
                            <div className="text-lg font-bold text-green-600">
                              {formatDuration(totalDuration)}
                            </div>
                            <div className="text-xs text-green-700">
                              🟢 Durée totale des stages
                            </div>
                          </div>

                          {/* Break Days */}
                          <div className="text-center p-3 bg-orange-50 rounded-lg">
                            <div className="text-2xl font-bold text-orange-600">
                              {totalBreakDays}
                            </div>
                            <div className="text-xs text-orange-700">
                              🟠 Jours de pause total
                            </div>
                          </div>

                          {/* Service Order Summary */}
                          <div className="text-center p-3 bg-purple-50 rounded-lg">
                            <div className="text-lg font-bold text-purple-600">
                              {sortedRotations.length > 0
                                ? `1→${sortedRotations.length}`
                                : "0"}
                            </div>
                            <div className="text-xs text-purple-700">
                              🟣 Ordre des services
                            </div>
                          </div>
                        </div>

                        {/* Detailed Schedule */}
                        {studentRotations?.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="font-medium text-sm text-muted-foreground mb-2">
                              Planning détaillé avec chronologie des rotations:
                            </h4>
                            <div className="max-h-48 overflow-y-auto space-y-1">
                              {sortedRotations.map((rotation, index) => {
                                const start = new Date(rotation.date_debut);
                                const end = new Date(rotation.date_fin);
                                const duration = Math.ceil(
                                  (end - start) / (1000 * 60 * 60 * 24)
                                );

                                // Calculate break before this rotation
                                let breakBefore = 0;
                                if (index > 0) {
                                  const prevEnd = new Date(
                                    sortedRotations[index - 1].date_fin
                                  );
                                  breakBefore =
                                    Math.ceil(
                                      (start - prevEnd) / (1000 * 60 * 60 * 24)
                                    ) - 1;
                                }

                                return (
                                  <div
                                    key={
                                      rotation.id ||
                                      `rotation-${index}-${rotation.etudiant_nom}-${rotation.service_nom}`
                                    }
                                    className="text-xs"
                                  >
                                    {breakBefore > 0 && (
                                      <div className="text-orange-600 italic mb-1 pl-4">
                                        ↳ 🟠 Pause: {breakBefore} jour(s)
                                      </div>
                                    )}
                                    <div className="flex justify-between items-center p-2 bg-muted/30 rounded border-l-4 border-purple-400">
                                      <div className="flex items-center space-x-2">
                                        <Badge
                                          variant="outline"
                                          className="bg-purple-100 text-purple-800 font-bold"
                                        >
                                          #{rotation.ordre}
                                        </Badge>
                                        <span className="font-medium">
                                          {rotation.service_nom}
                                        </span>
                                      </div>
                                      <div className="text-right">
                                        <div>
                                          {rotation.date_debut} →{" "}
                                          {rotation.date_fin}
                                        </div>
                                        <div className="text-muted-foreground">
                                          {duration} jour(s)
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {studentRotations?.length === 0 && (
                          <div className="text-center text-muted-foreground py-4">
                            <Calendar className="h-6 w-6 mx-auto mb-2" />
                            Aucune rotation planifiée
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                <Users className="h-8 w-8 mx-auto mb-2" />
                {searchTerm
                  ? "Aucun étudiant trouvé avec ce nom"
                  : "Chargez d'abord les plannings étudiants"}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PlanningPage;
