import React, { useState, useEffect } from "react";
import {
  getPromotions,
  generateAdvancedPlanning,
  analyzePlanningEfficiency,
  validatePlanning,
  getStudentPlanning,
} from "../services/api";
import Message from "../components/Message";
import { useMessage } from "../contexts/MessageContext";

const AdvancedPlanningsPage = () => {
  const [promotions, setPromotions] = useState([]);
  const [selectedPromoId, setSelectedPromoId] = useState("");
  const [advancedPlanning, setAdvancedPlanning] = useState(null);
  const [efficiencyAnalysis, setEfficiencyAnalysis] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [studentPlanning, setStudentPlanning] = useState(null);
  const [selectedStudentId, setSelectedStudentId] = useState("");
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

  const handleGenerateAdvancedPlanning = async () => {
    if (!selectedPromoId) {
      showMessage("Veuillez sélectionner une promotion", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await generateAdvancedPlanning(
        selectedPromoId,
        "2025-01-01"
      );
      setAdvancedPlanning(data);
      showMessage("Planning avancé généré avec succès");
    } catch (error) {
      showMessage("Erreur lors de la génération du planning avancé", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeEfficiency = async () => {
    if (!selectedPromoId) {
      showMessage("Veuillez sélectionner une promotion", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await analyzePlanningEfficiency(selectedPromoId);
      setEfficiencyAnalysis(data);
      showMessage("Analyse d'efficacité terminée");
    } catch (error) {
      showMessage("Erreur lors de l'analyse d'efficacité", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleValidatePlanning = async () => {
    if (!selectedPromoId) {
      showMessage("Veuillez sélectionner une promotion", "error");
      return;
    }

    try {
      setLoading(true);
      const { data } = await validatePlanning(selectedPromoId);
      setValidationResult(data);
      showMessage("Validation du planning terminée");
    } catch (error) {
      showMessage("Erreur lors de la validation du planning", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleGetStudentPlanning = async () => {
    if (!selectedPromoId || !selectedStudentId) {
      showMessage(
        "Veuillez sélectionner une promotion et un étudiant",
        "error"
      );
      return;
    }

    try {
      setLoading(true);
      const { data } = await getStudentPlanning(
        selectedPromoId,
        selectedStudentId
      );
      setStudentPlanning(data);
    } catch (error) {
      showMessage("Erreur lors du chargement du planning étudiant", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Plannings Avancés</h2>
      <Message text={message} type={type} />

      <div className="mb-8 flex flex-wrap items-end gap-4">
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

        <button
          onClick={handleGenerateAdvancedPlanning}
          className="bg-purple-600 text-white px-4 py-2 rounded"
          disabled={!selectedPromoId || loading}
        >
          Générer Planning Avancé
        </button>
        <button
          onClick={handleAnalyzeEfficiency}
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={!selectedPromoId || loading}
        >
          Analyser Efficacité
        </button>
        <button
          onClick={handleValidatePlanning}
          className="bg-green-600 text-white px-4 py-2 rounded"
          disabled={!selectedPromoId || loading}
        >
          Valider Planning
        </button>
      </div>

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
        </div>
      )}

      {/* Advanced Planning Results */}
      {advancedPlanning && (
        <div className="mb-6 p-4 bg-white rounded shadow">
          <h3 className="text-lg font-semibold mb-3">Planning Avancé</h3>
          <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
            {JSON.stringify(advancedPlanning, null, 2)}
          </pre>
        </div>
      )}

      {/* Efficiency Analysis Results */}
      {efficiencyAnalysis && (
        <div className="mb-6 p-4 bg-white rounded shadow">
          <h3 className="text-lg font-semibold mb-3">Analyse d'Efficacité</h3>
          <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
            {JSON.stringify(efficiencyAnalysis, null, 2)}
          </pre>
        </div>
      )}

      {/* Validation Results */}
      {validationResult && (
        <div className="mb-6 p-4 bg-white rounded shadow">
          <h3 className="text-lg font-semibold mb-3">
            Résultats de Validation
          </h3>
          <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
            {JSON.stringify(validationResult, null, 2)}
          </pre>
        </div>
      )}

      {/* Student Planning Section */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">
          Planning Étudiant Individuel
        </h3>
        <div className="flex flex-wrap items-end gap-4 mb-4">
          <div>
            <label className="block mb-1 font-medium">ID Étudiant</label>
            <input
              type="text"
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(e.target.value)}
              className="border p-2 rounded min-w-[200px]"
              placeholder="Entrez l'ID de l'étudiant"
            />
          </div>
          <button
            onClick={handleGetStudentPlanning}
            className="bg-orange-600 text-white px-4 py-2 rounded"
            disabled={!selectedPromoId || !selectedStudentId || loading}
          >
            Obtenir Planning Étudiant
          </button>
        </div>

        {studentPlanning && (
          <div className="p-4 bg-white rounded shadow">
            <h4 className="font-semibold mb-3">Planning de l'Étudiant</h4>
            <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
              {JSON.stringify(studentPlanning, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedPlanningsPage;
