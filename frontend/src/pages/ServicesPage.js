import React, { useEffect, useState } from "react";
import {
  getServices,
  createService,
  updateService,
  deleteService,
  getService,
  getSpecialities,
} from "../services/api";
import FormInput from "../components/FormInput";
import Message from "../components/Message";
import Modal from "../components/Modal";
import Table from "../components/Table";
import { useMessage } from "../contexts/MessageContext";

const ServicesPage = () => {
  const [services, setServices] = useState([]);
  const [specialities, setSpecialities] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [newService, setNewService] = useState({
    nom: "",
    places_disponibles: 1,
    duree_stage_jours: 14,
    speciality_id: "",
  });
  const [editServiceId, setEditServiceId] = useState(null);
  const [editService, setEditService] = useState({
    nom: "",
    places_disponibles: 1,
    duree_stage_jours: 14,
    speciality_id: "",
  });
  const [deleteServiceId, setDeleteServiceId] = useState(null);
  const { message, type, showMessage, loading, setLoading } = useMessage();

  useEffect(() => {
    loadServices();
    loadSpecialities();
  }, []);

  const loadServices = async () => {
    try {
      const { data } = await getServices();
      setServices(data);
    } catch (error) {
      showMessage("Erreur lors du chargement des services", "error");
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

  const handleCreateService = async () => {
    if (
      !newService.nom.trim() ||
      newService.places_disponibles < 1 ||
      newService.duree_stage_jours < 1 ||
      !newService.speciality_id
    ) {
      showMessage(
        "Veuillez remplir tous les champs avec des valeurs valides",
        "error"
      );
      return;
    }
    try {
      setLoading(true);
      await createService(newService);
      showMessage("Service créé avec succès");
      setNewService({
        nom: "",
        places_disponibles: 1,
        duree_stage_jours: 14,
        speciality_id: "",
      });
      setModalOpen(false);
      loadServices();
    } catch (error) {
      showMessage("Erreur lors de la création du service", "error");
    } finally {
      setLoading(false);
    }
  };

  const openModal = () => {
    setNewService({
      nom: "",
      places_disponibles: 1,
      duree_stage_jours: 14,
      speciality_id: "",
    });
    setModalOpen(true);
  };

  const openEditModal = async (id) => {
    setEditServiceId(id);
    try {
      setLoading(true);
      const { data } = await getService(id);
      setEditService({
        nom: data.nom,
        places_disponibles: data.places_disponibles,
        duree_stage_jours: data.duree_stage_jours,
        speciality_id: data.speciality_id,
      });
      setEditModalOpen(true);
    } catch (error) {
      showMessage("Erreur lors du chargement du service", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleEditService = async () => {
    if (
      !editService.nom.trim() ||
      editService.places_disponibles < 1 ||
      editService.duree_stage_jours < 1 ||
      !editService.speciality_id
    ) {
      showMessage(
        "Veuillez remplir tous les champs avec des valeurs valides",
        "error"
      );
      return;
    }
    try {
      setLoading(true);
      await updateService(editServiceId, editService);
      showMessage("Service mis à jour avec succès");
      setEditModalOpen(false);
      loadServices();
    } catch (error) {
      showMessage("Erreur lors de la mise à jour du service", "error");
    } finally {
      setLoading(false);
    }
  };

  const openDeleteDialog = (id) => {
    setDeleteServiceId(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteService = async () => {
    try {
      setLoading(true);
      await deleteService(deleteServiceId);
      showMessage("Service supprimé avec succès");
      setDeleteDialogOpen(false);
      loadServices();
    } catch (error) {
      showMessage("Erreur lors de la suppression du service", "error");
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { header: "Nom", accessor: "nom" },
    { header: "Places", accessor: "places_disponibles" },
    { header: "Durée (jours)", accessor: "duree_stage_jours" },
    { header: "Spécialité", accessor: "speciality_nom" },
    { header: "Actions", accessor: "actions" },
  ];

  const dataWithActions = services.map((service) => {
    // Find the speciality name for this service
    const speciality = specialities.find((s) => s.id === service.speciality_id);
    const specialityName = speciality ? speciality.nom : "N/A";

    return {
      ...service,
      speciality_nom: specialityName,
      actions: (
        <>
          <button
            className="text-blue-600 mr-2"
            onClick={() => openEditModal(service.id)}
          >
            Éditer
          </button>
          <button
            className="text-red-600"
            onClick={() => openDeleteDialog(service.id)}
          >
            Supprimer
          </button>
        </>
      ),
    };
  });

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Services</h2>
      <Message text={message} type={type} />
      <button
        onClick={openModal}
        className="bg-blue-600 text-white px-4 py-2 rounded mb-6"
      >
        Ajouter un service
      </button>
      <h3 className="font-semibold mt-6 mb-2">Liste des services</h3>
      <Table columns={columns} data={dataWithActions} />

      {/* Add Service Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Ajouter un service"
      >
        <div className="space-y-3">
          <FormInput
            label="Nom du service"
            value={newService.nom}
            onChange={(e) =>
              setNewService({ ...newService, nom: e.target.value })
            }
            placeholder="Nom du service"
          />
          <FormInput
            label="Places disponibles"
            type="number"
            value={newService.places_disponibles}
            onChange={(e) =>
              setNewService({
                ...newService,
                places_disponibles: Number(e.target.value),
              })
            }
            placeholder="Places disponibles"
          />
          <FormInput
            label="Durée stage (jours)"
            type="number"
            value={newService.duree_stage_jours}
            onChange={(e) =>
              setNewService({
                ...newService,
                duree_stage_jours: Number(e.target.value),
              })
            }
            placeholder="Durée stage (jours)"
          />
          <FormInput
            label="Spécialité"
            type="select"
            value={newService.speciality_id}
            onChange={(value) =>
              setNewService({ ...newService, speciality_id: value })
            }
            options={specialities.map((speciality) => ({
              value: speciality.id,
              label: speciality.nom,
            }))}
            placeholder="Sélectionner une spécialité"
          />
          <button
            onClick={handleCreateService}
            className="bg-blue-600 text-white px-4 py-2 rounded w-full mt-4"
            disabled={
              !newService.nom.trim() ||
              newService.places_disponibles < 1 ||
              newService.duree_stage_jours < 1 ||
              !newService.speciality_id ||
              loading
            }
          >
            Ajouter le service
          </button>
        </div>
      </Modal>

      {/* Edit Service Modal */}
      <Modal
        open={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Éditer le service"
      >
        <div className="space-y-3">
          <FormInput
            label="Nom du service"
            value={editService.nom}
            onChange={(e) =>
              setEditService({ ...editService, nom: e.target.value })
            }
            placeholder="Nom du service"
          />
          <FormInput
            label="Places disponibles"
            type="number"
            value={editService.places_disponibles}
            onChange={(e) =>
              setEditService({
                ...editService,
                places_disponibles: Number(e.target.value),
              })
            }
            placeholder="Places disponibles"
          />
          <FormInput
            label="Durée stage (jours)"
            type="number"
            value={editService.duree_stage_jours}
            onChange={(e) =>
              setEditService({
                ...editService,
                duree_stage_jours: Number(e.target.value),
              })
            }
            placeholder="Durée stage (jours)"
          />
          <FormInput
            label="Spécialité"
            type="select"
            value={editService.speciality_id}
            onChange={(value) =>
              setEditService({ ...editService, speciality_id: value })
            }
            options={specialities.map((speciality) => ({
              value: speciality.id,
              label: speciality.nom,
            }))}
            placeholder="Sélectionner une spécialité"
          />
          <button
            onClick={handleEditService}
            className="bg-blue-600 text-white px-4 py-2 rounded w-full mt-4"
            disabled={
              !editService.nom.trim() ||
              editService.places_disponibles < 1 ||
              editService.duree_stage_jours < 1 ||
              !editService.speciality_id ||
              loading
            }
          >
            Enregistrer les modifications
          </button>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        title="Confirmer la suppression"
      >
        <div className="space-y-4">
          <div>
            Êtes-vous sûr de vouloir supprimer ce service ? Cette action est
            irréversible.
          </div>
          <div className="flex gap-4 justify-end">
            <button
              onClick={() => setDeleteDialogOpen(false)}
              className="px-4 py-2 rounded bg-gray-200"
            >
              Annuler
            </button>
            <button
              onClick={handleDeleteService}
              className="px-4 py-2 rounded bg-red-600 text-white"
              disabled={loading}
            >
              Supprimer
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ServicesPage;
