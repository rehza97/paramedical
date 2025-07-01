import React, { useState, useEffect } from "react";
import { useMessage } from "../contexts/MessageContext";
import {
  getSpecialities,
  createSpeciality,
  updateSpeciality,
  deleteSpeciality,
} from "../services/api";
import Table from "../components/Table";
import Modal from "../components/Modal";
import FormInput from "../components/FormInput";
import Message from "../components/Message";

const SpecialitiesPage = () => {
  const [specialities, setSpecialities] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSpeciality, setEditingSpeciality] = useState(null);
  const [formData, setFormData] = useState({
    nom: "",
    description: "",
    duree_annees: 3,
  });
  const { message, type, showMessage, loading, setLoading } = useMessage();

  useEffect(() => {
    fetchSpecialities();
  }, []);

  const fetchSpecialities = async () => {
    try {
      setLoading(true);
      const response = await getSpecialities();
      setSpecialities(response.data || response);
    } catch (error) {
      showMessage("Erreur lors du chargement des spécialités", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      if (editingSpeciality) {
        await updateSpeciality(editingSpeciality.id, formData);
        showMessage("Spécialité mise à jour avec succès", "success");
      } else {
        await createSpeciality(formData);
        showMessage("Spécialité créée avec succès", "success");
      }
      setIsModalOpen(false);
      setEditingSpeciality(null);
      setFormData({ nom: "", description: "", duree_annees: 3 });
      fetchSpecialities();
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Erreur lors de la sauvegarde";
      showMessage(errorMessage, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (speciality) => {
    setEditingSpeciality(speciality);
    setFormData({
      nom: speciality.nom,
      description: speciality.description || "",
      duree_annees: speciality.duree_annees,
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (speciality) => {
    if (
      window.confirm(
        `Êtes-vous sûr de vouloir supprimer la spécialité "${speciality.nom}" ?`
      )
    ) {
      try {
        setLoading(true);
        await deleteSpeciality(speciality.id);
        showMessage("Spécialité supprimée avec succès", "success");
        fetchSpecialities();
      } catch (error) {
        const errorMessage =
          error.response?.data?.detail || "Erreur lors de la suppression";
        showMessage(errorMessage, "error");
      } finally {
        setLoading(false);
      }
    }
  };

  const openCreateModal = () => {
    setEditingSpeciality(null);
    setFormData({ nom: "", description: "", duree_annees: 3 });
    setIsModalOpen(true);
  };

  const columns = [
    { key: "nom", label: "Nom" },
    { key: "description", label: "Description" },
    {
      key: "duree_annees",
      label: "Durée",
      render: (value) => `${value} an${value > 1 ? "s" : ""}`,
    },
    {
      key: "date_creation",
      label: "Date de création",
      render: (value) => new Date(value).toLocaleDateString("fr-FR"),
    },
    {
      key: "actions",
      label: "Actions",
      render: (_, speciality) => (
        <div className="flex space-x-2">
          <button
            onClick={() => handleEdit(speciality)}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Modifier
          </button>
          <button
            onClick={() => handleDelete(speciality)}
            className="text-red-600 hover:text-red-800 font-medium"
          >
            Supprimer
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">
          Gestion des Spécialités
        </h1>
        <button
          onClick={openCreateModal}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          disabled={loading}
        >
          Nouvelle Spécialité
        </button>
      </div>

      <Message text={message} type={type} />

      {loading ? (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow">
          {specialities.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <p>Aucune spécialité trouvée.</p>
              <button
                onClick={openCreateModal}
                className="mt-4 text-blue-600 hover:text-blue-800 font-medium"
              >
                Créer la première spécialité
              </button>
            </div>
          ) : (
            <Table columns={columns} data={specialities} />
          )}
        </div>
      )}

      {/* Create/Edit Speciality Modal */}
      <Modal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={
          editingSpeciality ? "Modifier la Spécialité" : "Nouvelle Spécialité"
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <FormInput
            label="Nom de la spécialité"
            type="text"
            value={formData.nom}
            onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
            required
            placeholder="Ex: Kinésithérapie, Orthophonie..."
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Description optionnelle de la spécialité..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Durée des études
            </label>
            <select
              value={formData.duree_annees}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  duree_annees: parseInt(e.target.value),
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value={3}>3 ans</option>
              <option value={4}>4 ans</option>
              <option value={5}>5 ans</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading
                ? "Sauvegarde..."
                : editingSpeciality
                ? "Mettre à jour"
                : "Créer"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default SpecialitiesPage;
