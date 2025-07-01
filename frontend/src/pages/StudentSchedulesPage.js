import React, { useState, useEffect } from "react";
import {
  getStudentSchedules,
  getStudentScheduleDetail,
  deleteStudentSchedule,
  getPromotions,
} from "../services/api";
import Message from "../components/Message";
import { useMessage } from "../contexts/MessageContext";

const StudentSchedulesPage = () => {
  const [promotions, setPromotions] = useState([]);
  const [selectedPromoId, setSelectedPromoId] = useState("");
  const [schedules, setSchedules] = useState([]);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const { message, type, showMessage, loading, setLoading } = useMessage();
  const [promoLoading, setPromoLoading] = useState(false);
  const [schedulesLoading, setSchedulesLoading] = useState(false);

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

  const handleLoadSchedules = async () => {
    if (!selectedPromoId) return;
    try {
      setSchedulesLoading(true);
      const { data } = await getStudentSchedules(selectedPromoId);
      setSchedules(data);
      setSelectedSchedule(null);
    } catch (error) {
      showMessage("Erreur lors du chargement des plannings étudiants", "error");
    } finally {
      setSchedulesLoading(false);
    }
  };

  const handleSelectSchedule = async (scheduleId) => {
    try {
      setLoading(true);
      const { data } = await getStudentScheduleDetail(scheduleId);
      setSelectedSchedule(data);
    } catch (error) {
      showMessage("Erreur lors du chargement du détail du planning", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSchedule = async (scheduleId) => {
    try {
      setLoading(true);
      await deleteStudentSchedule(scheduleId);
      showMessage("Planning supprimé");
      handleLoadSchedules();
    } catch (error) {
      showMessage("Erreur lors de la suppression du planning", "error");
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { header: "Nom", accessor: "etudiant_nom" },
    { header: "Prénom", accessor: "etudiant_prenom" },
    { header: "Promotion", accessor: "promotion_nom" },
    { header: "Actions", accessor: "actions" },
  ];

  const dataWithActions = schedules.map((schedule) => ({
    ...schedule,
    actions: (
      <>
        <button
          onClick={() => handleSelectSchedule(schedule.id)}
          className="text-blue-600 mr-2"
        >
          Voir
        </button>
        <button
          onClick={() => handleDeleteSchedule(schedule.id)}
          className="text-red-600"
        >
          Supprimer
        </button>
      </>
    ),
  }));

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Plannings Étudiants</h2>
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
                {promo.specialite ? `, ${promo.specialite}` : ""})
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleLoadSchedules}
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={!selectedPromoId || schedulesLoading}
        >
          Charger Plannings Étudiants
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
          {selectedPromo.specialite && (
            <div>
              <span className="font-semibold">Spécialité:</span>{" "}
              {selectedPromo.specialite}
            </div>
          )}
          {selectedPromo.duree && (
            <div>
              <span className="font-semibold">Durée:</span>{" "}
              {selectedPromo.duree} ans
            </div>
          )}
        </div>
      )}

      <div className="bg-white rounded shadow p-2 overflow-x-auto">
        <h3 className="font-semibold mb-2">Liste des plannings</h3>
        {schedulesLoading ? (
          <div className="text-center text-gray-500 py-8">
            Chargement des plannings étudiants...
          </div>
        ) : dataWithActions.length > 0 ? (
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
              {dataWithActions.map((row, i) => (
                <tr
                  key={row.id}
                  className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}
                >
                  {columns.map((col) => (
                    <td key={col.accessor} className="px-4 py-2 border-b">
                      {row[col.accessor]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-gray-400 py-8">
            Aucun planning étudiant trouvé pour cette promotion.
          </div>
        )}
      </div>

      {selectedSchedule && (
        <div className="bg-gray-100 p-4 rounded mt-6">
          <h4 className="font-semibold mb-2">Détail du planning</h4>
          <pre>{JSON.stringify(selectedSchedule, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default StudentSchedulesPage;
