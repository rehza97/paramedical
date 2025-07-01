import React, { useState, useEffect } from "react";
import {
  generatePlanning,
  getPlanning,
  exportPlanningExcel,
  getPromotions,
  getPromotionYears,
  getActivePromotionYear,
} from "../services/api";
import Message from "../components/Message";
import { useMessage } from "../contexts/MessageContext";

const PlanningsPage = () => {
  const [promotions, setPromotions] = useState([]);
  const [selectedPromoId, setSelectedPromoId] = useState("");
  const [promotionYears, setPromotionYears] = useState([]);
  const [selectedYearId, setSelectedYearId] = useState("");
  const [activeYear, setActiveYear] = useState(null);
  const [planning, setPlanning] = useState(null);
  const { message, type, showMessage, loading, setLoading } = useMessage();
  const [promoLoading, setPromoLoading] = useState(false);
  const [planningLoading, setPlanningLoading] = useState(false);

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

  const selectedPromo = promotions.find((p) => p.id === selectedPromoId);
  const selectedYear = promotionYears.find((y) => y.id === selectedYearId);

  const handleGeneratePlanning = async () => {
    if (!selectedPromoId) {
      showMessage("Veuillez sélectionner une promotion", "error");
      return;
    }

    try {
      setLoading(true);
      await generatePlanning(selectedPromoId, "2025-01-01");
      showMessage("Planning généré avec succès");
      handleLoadPlanning();
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

  const handleExportExcel = async () => {
    if (!selectedPromoId) return;
    try {
      const response = await exportPlanningExcel(selectedPromoId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `planning_${selectedPromoId}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      showMessage("Erreur lors de l'export Excel", "error");
    }
  };

  const columns =
    planning && planning.rotations?.length > 0
      ? [
          { header: "Étudiant", accessor: "etudiant_nom" },
          { header: "Service", accessor: "service_nom" },
          { header: "Date début", accessor: "date_debut" },
          { header: "Date fin", accessor: "date_fin" },
          { header: "Rotation", accessor: "ordre" },
        ]
      : [];

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Plannings</h2>
      <Message text={message} type={type} />
      <div className="mb-8 flex flex-wrap items-end gap-4">
        {/* Promotion selector */}
        <div>
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
                {promo.nom} ({promo.annee}
                {promo.speciality ? `, ${promo.speciality.nom}` : ""})
              </option>
            ))}
          </select>
        </div>

        {/* Year selector */}
        {selectedPromoId && (
          <div>
            <label className="block mb-1 font-medium">Année</label>
            <select
              value={selectedYearId}
              onChange={(e) => setSelectedYearId(e.target.value)}
              className="border p-2 rounded min-w-[200px]"
              disabled={promotionYears.length === 0}
            >
              <option value="">
                {promotionYears.length === 0
                  ? "Chargement..."
                  : "Sélectionner une année"}
              </option>
              {promotionYears.map((year) => (
                <option key={year.id} value={year.id}>
                  {year.nom} ({year.annee_calendaire})
                  {year.is_active ? " - Active" : ""}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Buttons */}
        <button
          onClick={handleGeneratePlanning}
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={!selectedPromoId || loading}
        >
          Générer Planning
        </button>
        <button
          onClick={handleLoadPlanning}
          className="bg-green-600 text-white px-4 py-2 rounded"
          disabled={!selectedPromoId || loading}
        >
          Charger Planning
        </button>
        <button
          onClick={handleExportExcel}
          className="bg-yellow-600 text-white px-4 py-2 rounded"
          disabled={!selectedPromoId || loading}
        >
          Exporter Excel
        </button>
      </div>

      {/* Promotion info */}
      {selectedPromo && (
        <div className="mb-4 p-4 bg-white rounded shadow flex flex-wrap gap-8 items-center">
          <div>
            <span className="font-semibold">Nom:</span> {selectedPromo.nom}
          </div>
          <div>
            <span className="font-semibold">Année:</span> {selectedPromo.annee}
          </div>
          {selectedPromo.speciality && (
            <div>
              <span className="font-semibold">Spécialité:</span>{" "}
              {selectedPromo.speciality.nom}
            </div>
          )}
          {selectedPromo.speciality && (
            <div>
              <span className="font-semibold">Durée:</span>{" "}
              {selectedPromo.speciality.duree_annees} ans
            </div>
          )}
          {selectedYear && (
            <div>
              <span className="font-semibold">Année sélectionnée:</span>{" "}
              {selectedYear.nom} ({selectedYear.annee_calendaire})
              {selectedYear.is_active && (
                <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                  Active
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded shadow p-2 overflow-x-auto">
        {planningLoading ? (
          <div className="text-center text-gray-500 py-8">
            Chargement du planning...
          </div>
        ) : planning?.rotations?.length > 0 ? (
          <table className="min-w-full text-sm">
            <thead className="sticky top-0 bg-gray-100 z-10">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.accessor}
                    className="px-4 py-2 text-left font-semibold border-b"
                  >
                    {col.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {planning.rotations.map((row, i) => (
                <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                  {columns.map((col) => (
                    <td key={col.accessor} className="px-4 py-2 border-b">
                      {row[col.accessor]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : planning ? (
          <div className="text-gray-500 py-8">
            Aucune rotation trouvée pour cette promotion.
          </div>
        ) : (
          <div className="text-gray-400 py-8">
            Veuillez sélectionner une promotion et charger un planning.
          </div>
        )}
      </div>
    </div>
  );
};

export default PlanningsPage;
