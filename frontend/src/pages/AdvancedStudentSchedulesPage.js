import React, { useState, useEffect } from "react";
import {
  getPromotions,
  getStudentSchedule,
  getStudentScheduleHistory,
  getStudentProgress,
  updateServiceStatus,
  getPlanningSummary,
  archiveSchedule,
  createScheduleVersion,
  getScheduleById,
  createStudentSchedule,
  updateStudentSchedule,
  deleteStudentSchedule,
  createScheduleDetail,
  updateScheduleDetail,
  deleteScheduleDetail,
  exportScheduleExcel,
  exportPlanningSchedulesExcel,
} from "../services/api";
import Message from "../components/Message";
import { useMessage } from "../contexts/MessageContext";

const AdvancedStudentSchedulesPage = () => {
  const [promotions, setPromotions] = useState([]);
  const [selectedPromoId, setSelectedPromoId] = useState("");
  const [selectedStudentId, setSelectedStudentId] = useState("");
  const [selectedScheduleId, setSelectedScheduleId] = useState("");
  const [selectedDetailId, setSelectedDetailId] = useState("");
  const [studentSchedule, setStudentSchedule] = useState(null);
  const [scheduleHistory, setScheduleHistory] = useState([]);
  const [studentProgress, setStudentProgress] = useState(null);
  const [planningSummary, setPlanningSummary] = useState([]);
  const [scheduleById, setScheduleById] = useState(null);
  const [newSchedule, setNewSchedule] = useState({
    etudiant_id: "",
    planning_id: "",
    date_debut: "",
    date_fin: "",
    statut: "actif",
  });
  const [newDetail, setNewDetail] = useState({
    service_id: "",
    service_nom: "",
    ordre_service: 1,
    date_debut: "",
    date_fin: "",
    duree_jours: 14,
    statut: "en_cours",
    notes: "",
  });
  const [updateStatus, setUpdateStatus] = useState({
    statut: "termine",
    notes: "",
  });
  const { message, type, showMessage, loading, setLoading } = useMessage();
  const [promoLoading, setPromoLoading] = useState(false);

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

  const selectedPromo = promotions.find((p) => p.id === selectedPromoId);

  // Student Schedule Functions
  const handleGetStudentSchedule = async () => {
    if (!selectedStudentId) {
      showMessage("Veuillez entrer un ID étudiant", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await getStudentSchedule(selectedStudentId);
      setStudentSchedule(data);
    } catch (error) {
      showMessage("Erreur lors du chargement du planning étudiant", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleGetScheduleHistory = async () => {
    if (!selectedStudentId) {
      showMessage("Veuillez entrer un ID étudiant", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await getStudentScheduleHistory(selectedStudentId);
      setScheduleHistory(data);
    } catch (error) {
      showMessage("Erreur lors du chargement de l'historique", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleGetStudentProgress = async () => {
    if (!selectedStudentId) {
      showMessage("Veuillez entrer un ID étudiant", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await getStudentProgress(selectedStudentId);
      setStudentProgress(data);
    } catch (error) {
      showMessage("Erreur lors du chargement de la progression", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateServiceStatus = async () => {
    if (!selectedScheduleId || !selectedDetailId) {
      showMessage("Veuillez sélectionner un planning et un détail", "error");
      return;
    }

    try {
      setLoading(true);
      await updateServiceStatus(
        selectedScheduleId,
        selectedDetailId,
        updateStatus
      );
      showMessage("Statut mis à jour avec succès");
    } catch (error) {
      showMessage("Erreur lors de la mise à jour du statut", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleGetPlanningSummary = async () => {
    if (!selectedPromoId) {
      showMessage("Veuillez sélectionner une promotion", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await getPlanningSummary(selectedPromoId);
      setPlanningSummary(data);
    } catch (error) {
      showMessage("Erreur lors du chargement du résumé", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleArchiveSchedule = async () => {
    if (!selectedScheduleId) {
      showMessage("Veuillez sélectionner un planning", "error");
      return;
    }

    try {
      setLoading(true);
      await archiveSchedule(selectedScheduleId);
      showMessage("Planning archivé avec succès");
    } catch (error) {
      showMessage("Erreur lors de l'archivage", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScheduleVersion = async () => {
    if (!selectedScheduleId) {
      showMessage("Veuillez sélectionner un planning", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await createScheduleVersion(selectedScheduleId);
      setScheduleById(data);
      showMessage("Nouvelle version créée avec succès");
    } catch (error) {
      showMessage("Erreur lors de la création de la version", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleGetScheduleById = async () => {
    if (!selectedScheduleId) {
      showMessage("Veuillez entrer un ID de planning", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await getScheduleById(selectedScheduleId);
      setScheduleById(data);
    } catch (error) {
      showMessage("Erreur lors du chargement du planning", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStudentSchedule = async () => {
    if (!newSchedule.etudiant_id || !newSchedule.planning_id) {
      showMessage("Veuillez remplir les champs obligatoires", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await createStudentSchedule(newSchedule);
      setScheduleById(data);
      showMessage("Planning étudiant créé avec succès");
      setNewSchedule({
        etudiant_id: "",
        planning_id: "",
        date_debut: "",
        date_fin: "",
        statut: "actif",
      });
    } catch (error) {
      showMessage("Erreur lors de la création du planning", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScheduleDetail = async () => {
    if (!selectedScheduleId || !newDetail.service_id) {
      showMessage("Veuillez sélectionner un planning et un service", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await createScheduleDetail(
        selectedScheduleId,
        newDetail
      );
      showMessage("Détail créé avec succès");
      setNewDetail({
        service_id: "",
        service_nom: "",
        ordre_service: 1,
        date_debut: "",
        date_fin: "",
        duree_jours: 14,
        statut: "en_cours",
        notes: "",
      });
    } catch (error) {
      showMessage("Erreur lors de la création du détail", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleExportScheduleExcel = async () => {
    if (!selectedScheduleId) {
      showMessage("Veuillez sélectionner un planning", "error");
      return;
    }

    try {
      const response = await exportScheduleExcel(selectedScheduleId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `schedule_${selectedScheduleId}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      showMessage("Export Excel réussi");
    } catch (error) {
      showMessage("Erreur lors de l'export Excel", "error");
    }
  };

  const handleExportPlanningSchedulesExcel = async () => {
    if (!selectedPromoId) {
      showMessage("Veuillez sélectionner une promotion", "error");
      return;
    }

    try {
      const response = await exportPlanningSchedulesExcel(selectedPromoId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `planning_schedules_${selectedPromoId}.xlsx`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      showMessage("Export Excel réussi");
    } catch (error) {
      showMessage("Erreur lors de l'export Excel", "error");
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Plannings Étudiants Avancés</h2>
      <Message text={message} type={type} />

      {/* Promotion Selection */}
      <div className="mb-6">
        <label className="block mb-1 font-medium">Promotion</label>
        <select
          value={selectedPromoId}
          onChange={(e) => setSelectedPromoId(e.target.value)}
          className="border p-2 rounded min-w-[250px]"
          disabled={promoLoading}
        >
          <option value="">
            {promoLoading ? "Chargement..." : "Sélectionner une promotion"}
          </option>
          {promotions.map((promo) => (
            <option key={promo.id} value={promo.id}>
              {promo.nom} ({promo.annee})
            </option>
          ))}
        </select>
      </div>

      {/* Student Schedule Section */}
      <div className="mb-8 p-4 bg-white rounded shadow">
        <h3 className="text-lg font-semibold mb-4">Planning Étudiant</h3>
        <div className="flex flex-wrap gap-4 mb-4">
          <div>
            <label className="block mb-1 font-medium">ID Étudiant</label>
            <input
              type="text"
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(e.target.value)}
              className="border p-2 rounded min-w-[200px]"
              placeholder="ID étudiant"
            />
          </div>
          <button
            onClick={handleGetStudentSchedule}
            className="bg-blue-600 text-white px-4 py-2 rounded"
            disabled={!selectedStudentId || loading}
          >
            Obtenir Planning
          </button>
          <button
            onClick={handleGetScheduleHistory}
            className="bg-green-600 text-white px-4 py-2 rounded"
            disabled={!selectedStudentId || loading}
          >
            Historique
          </button>
          <button
            onClick={handleGetStudentProgress}
            className="bg-purple-600 text-white px-4 py-2 rounded"
            disabled={!selectedStudentId || loading}
          >
            Progression
          </button>
        </div>

        {studentSchedule && (
          <div className="mb-4">
            <h4 className="font-semibold mb-2">Planning Actuel</h4>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(studentSchedule, null, 2)}
            </pre>
          </div>
        )}

        {scheduleHistory.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold mb-2">Historique</h4>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(scheduleHistory, null, 2)}
            </pre>
          </div>
        )}

        {studentProgress && (
          <div className="mb-4">
            <h4 className="font-semibold mb-2">Progression</h4>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(studentProgress, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Service Status Update */}
      <div className="mb-8 p-4 bg-white rounded shadow">
        <h3 className="text-lg font-semibold mb-4">
          Mise à Jour Statut Service
        </h3>
        <div className="flex flex-wrap gap-4 mb-4">
          <div>
            <label className="block mb-1 font-medium">ID Planning</label>
            <input
              type="text"
              value={selectedScheduleId}
              onChange={(e) => setSelectedScheduleId(e.target.value)}
              className="border p-2 rounded min-w-[150px]"
              placeholder="ID planning"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">ID Détail</label>
            <input
              type="text"
              value={selectedDetailId}
              onChange={(e) => setSelectedDetailId(e.target.value)}
              className="border p-2 rounded min-w-[150px]"
              placeholder="ID détail"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Statut</label>
            <select
              value={updateStatus.statut}
              onChange={(e) =>
                setUpdateStatus({ ...updateStatus, statut: e.target.value })
              }
              className="border p-2 rounded"
            >
              <option value="en_cours">En cours</option>
              <option value="termine">Terminé</option>
              <option value="annule">Annulé</option>
            </select>
          </div>
          <div>
            <label className="block mb-1 font-medium">Notes</label>
            <input
              type="text"
              value={updateStatus.notes}
              onChange={(e) =>
                setUpdateStatus({ ...updateStatus, notes: e.target.value })
              }
              className="border p-2 rounded min-w-[200px]"
              placeholder="Notes"
            />
          </div>
          <button
            onClick={handleUpdateServiceStatus}
            className="bg-orange-600 text-white px-4 py-2 rounded"
            disabled={!selectedScheduleId || !selectedDetailId || loading}
          >
            Mettre à Jour
          </button>
        </div>
      </div>

      {/* Planning Summary */}
      <div className="mb-8 p-4 bg-white rounded shadow">
        <h3 className="text-lg font-semibold mb-4">Résumé Planning</h3>
        <div className="flex gap-4 mb-4">
          <button
            onClick={handleGetPlanningSummary}
            className="bg-indigo-600 text-white px-4 py-2 rounded"
            disabled={!selectedPromoId || loading}
          >
            Obtenir Résumé
          </button>
          <button
            onClick={handleExportPlanningSchedulesExcel}
            className="bg-yellow-600 text-white px-4 py-2 rounded"
            disabled={!selectedPromoId || loading}
          >
            Exporter Excel Planning
          </button>
        </div>

        {planningSummary.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2">Résumé</h4>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(planningSummary, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Schedule Management */}
      <div className="mb-8 p-4 bg-white rounded shadow">
        <h3 className="text-lg font-semibold mb-4">Gestion Planning</h3>
        <div className="flex flex-wrap gap-4 mb-4">
          <button
            onClick={handleGetScheduleById}
            className="bg-blue-600 text-white px-4 py-2 rounded"
            disabled={!selectedScheduleId || loading}
          >
            Obtenir par ID
          </button>
          <button
            onClick={handleArchiveSchedule}
            className="bg-gray-600 text-white px-4 py-2 rounded"
            disabled={!selectedScheduleId || loading}
          >
            Archiver
          </button>
          <button
            onClick={handleCreateScheduleVersion}
            className="bg-green-600 text-white px-4 py-2 rounded"
            disabled={!selectedScheduleId || loading}
          >
            Nouvelle Version
          </button>
          <button
            onClick={handleExportScheduleExcel}
            className="bg-yellow-600 text-white px-4 py-2 rounded"
            disabled={!selectedScheduleId || loading}
          >
            Exporter Excel
          </button>
        </div>

        {scheduleById && (
          <div className="mb-4">
            <h4 className="font-semibold mb-2">Planning par ID</h4>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(scheduleById, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Create New Schedule */}
      <div className="mb-8 p-4 bg-white rounded shadow">
        <h3 className="text-lg font-semibold mb-4">Créer Nouveau Planning</h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block mb-1 font-medium">ID Étudiant</label>
            <input
              type="text"
              value={newSchedule.etudiant_id}
              onChange={(e) =>
                setNewSchedule({ ...newSchedule, etudiant_id: e.target.value })
              }
              className="border p-2 rounded w-full"
              placeholder="ID étudiant"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">ID Planning</label>
            <input
              type="text"
              value={newSchedule.planning_id}
              onChange={(e) =>
                setNewSchedule({ ...newSchedule, planning_id: e.target.value })
              }
              className="border p-2 rounded w-full"
              placeholder="ID planning"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Date Début</label>
            <input
              type="date"
              value={newSchedule.date_debut}
              onChange={(e) =>
                setNewSchedule({ ...newSchedule, date_debut: e.target.value })
              }
              className="border p-2 rounded w-full"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Date Fin</label>
            <input
              type="date"
              value={newSchedule.date_fin}
              onChange={(e) =>
                setNewSchedule({ ...newSchedule, date_fin: e.target.value })
              }
              className="border p-2 rounded w-full"
            />
          </div>
        </div>
        <button
          onClick={handleCreateStudentSchedule}
          className="bg-green-600 text-white px-4 py-2 rounded"
          disabled={
            !newSchedule.etudiant_id || !newSchedule.planning_id || loading
          }
        >
          Créer Planning
        </button>
      </div>

      {/* Create Schedule Detail */}
      <div className="mb-8 p-4 bg-white rounded shadow">
        <h3 className="text-lg font-semibold mb-4">Créer Détail Planning</h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block mb-1 font-medium">ID Service</label>
            <input
              type="text"
              value={newDetail.service_id}
              onChange={(e) =>
                setNewDetail({ ...newDetail, service_id: e.target.value })
              }
              className="border p-2 rounded w-full"
              placeholder="ID service"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Nom Service</label>
            <input
              type="text"
              value={newDetail.service_nom}
              onChange={(e) =>
                setNewDetail({ ...newDetail, service_nom: e.target.value })
              }
              className="border p-2 rounded w-full"
              placeholder="Nom service"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Ordre</label>
            <input
              type="number"
              value={newDetail.ordre_service}
              onChange={(e) =>
                setNewDetail({
                  ...newDetail,
                  ordre_service: parseInt(e.target.value),
                })
              }
              className="border p-2 rounded w-full"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Durée (jours)</label>
            <input
              type="number"
              value={newDetail.duree_jours}
              onChange={(e) =>
                setNewDetail({
                  ...newDetail,
                  duree_jours: parseInt(e.target.value),
                })
              }
              className="border p-2 rounded w-full"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Date Début</label>
            <input
              type="date"
              value={newDetail.date_debut}
              onChange={(e) =>
                setNewDetail({ ...newDetail, date_debut: e.target.value })
              }
              className="border p-2 rounded w-full"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Date Fin</label>
            <input
              type="date"
              value={newDetail.date_fin}
              onChange={(e) =>
                setNewDetail({ ...newDetail, date_fin: e.target.value })
              }
              className="border p-2 rounded w-full"
            />
          </div>
        </div>
        <button
          onClick={handleCreateScheduleDetail}
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={!selectedScheduleId || !newDetail.service_id || loading}
        >
          Créer Détail
        </button>
      </div>
    </div>
  );
};

export default AdvancedStudentSchedulesPage;
