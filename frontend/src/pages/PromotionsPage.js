import React, { useEffect, useState } from "react";
import {
  getPromotions,
  createPromotion,
  deletePromotion,
  getSpecialities,
  getServices,
  assignServiceToPromotion,
  removeServiceFromPromotion,
  getPromotionServices,
  getPromotionYears,
  getActivePromotionYear,
  activatePromotionYear,
  assignServiceToPromotionYear,
  removeServiceFromPromotionYear,
  getPromotionYearServices,
} from "../services/api";
import FormInput from "../components/FormInput";
import Message from "../components/Message";
import Modal from "../components/Modal";
import Table from "../components/Table";
import { useMessage } from "../contexts/MessageContext";

const PromotionsPage = () => {
  const [promotions, setPromotions] = useState([]);
  const [specialities, setSpecialities] = useState([]);
  const [services, setServices] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [serviceModalOpen, setServiceModalOpen] = useState(false);
  const [yearsModalOpen, setYearsModalOpen] = useState(false);
  const [yearServicesModalOpen, setYearServicesModalOpen] = useState(false);
  const [selectedPromotion, setSelectedPromotion] = useState(null);
  const [promotionServices, setPromotionServices] = useState([]);
  const [promotionYears, setPromotionYears] = useState([]);
  const [activeYear, setActiveYear] = useState(null);
  const [selectedYear, setSelectedYear] = useState(null);
  const [yearServices, setYearServices] = useState([]);
  const [newPromotion, setNewPromotion] = useState({
    nom: "",
    annee: new Date().getFullYear(),
    speciality_id: "",
    etudiants: [],
  });
  const [newEtudiant, setNewEtudiant] = useState({ nom: "", prenom: "" });
  const { message, type, showMessage, loading, setLoading } = useMessage();

  useEffect(() => {
    loadPromotions();
    loadSpecialities();
    loadServices();
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
      await createPromotion(newPromotion);
      showMessage("Promotion créée avec succès");
      setNewPromotion({
        nom: "",
        annee: new Date().getFullYear(),
        speciality_id: "",
        etudiants: [],
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

  const openModal = () => {
    setNewPromotion({
      nom: "",
      annee: new Date().getFullYear(),
      speciality_id: "",
      etudiants: [],
    });
    setNewEtudiant({ nom: "", prenom: "" });
    setModalOpen(true);
  };

  const openServiceModal = async (promotion) => {
    setSelectedPromotion(promotion);
    try {
      const { data } = await getPromotionServices(promotion.id);
      setPromotionServices(data);
      setServiceModalOpen(true);
    } catch (error) {
      showMessage(
        "Erreur lors du chargement des services de la promotion",
        "error"
      );
    }
  };

  const handleAssignService = async (serviceId) => {
    try {
      setLoading(true);
      await assignServiceToPromotion(selectedPromotion.id, serviceId);
      showMessage("Service assigné avec succès");
      const { data } = await getPromotionServices(selectedPromotion.id);
      setPromotionServices(data);
    } catch (error) {
      showMessage("Erreur lors de l'assignation du service", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveService = async (serviceId) => {
    try {
      setLoading(true);
      await removeServiceFromPromotion(selectedPromotion.id, serviceId);
      showMessage("Service retiré avec succès");
      const { data } = await getPromotionServices(selectedPromotion.id);
      setPromotionServices(data);
    } catch (error) {
      showMessage("Erreur lors du retrait du service", "error");
    } finally {
      setLoading(false);
    }
  };

  // Promotion years functions
  const openYearsModal = async (promotion) => {
    setSelectedPromotion(promotion);
    try {
      setLoading(true);
      const [yearsResponse, activeResponse] = await Promise.all([
        getPromotionYears(promotion.id),
        getActivePromotionYear(promotion.id),
      ]);
      setPromotionYears(yearsResponse.data);
      setActiveYear(activeResponse.data);
      setYearsModalOpen(true);
    } catch (error) {
      showMessage("Erreur lors du chargement des années de promotion", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleActivateYear = async (yearId) => {
    try {
      setLoading(true);
      await activatePromotionYear(yearId);
      showMessage("Année activée avec succès");
      const [yearsResponse, activeResponse] = await Promise.all([
        getPromotionYears(selectedPromotion.id),
        getActivePromotionYear(selectedPromotion.id),
      ]);
      setPromotionYears(yearsResponse.data);
      setActiveYear(activeResponse.data);
    } catch (error) {
      showMessage("Erreur lors de l'activation de l'année", "error");
    } finally {
      setLoading(false);
    }
  };

  const openYearServicesModal = async (year) => {
    setSelectedYear(year);
    try {
      const { data } = await getPromotionYearServices(year.id);
      setYearServices(data);
      setYearServicesModalOpen(true);
    } catch (error) {
      showMessage("Erreur lors du chargement des services de l'année", "error");
    }
  };

  const handleAssignYearService = async (serviceId) => {
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

  const handleDeletePromotion = async (id) => {
    if (
      window.confirm("Êtes-vous sûr de vouloir supprimer cette promotion ?")
    ) {
      try {
        setLoading(true);
        await deletePromotion(id);
        showMessage("Promotion supprimée avec succès");
        loadPromotions();
      } catch (error) {
        showMessage("Erreur lors de la suppression", "error");
      } finally {
        setLoading(false);
      }
    }
  };

  const columns = [
    { header: "Titre", accessor: "nom" },
    { header: "Année", accessor: "annee" },
    { header: "Spécialité", accessor: "speciality_name" },
    { header: "Durée", accessor: "duree_annees" },
    { header: "Nombre d'étudiants", accessor: "nb_etudiants" },
    { header: "Actions", accessor: "actions" },
  ];

  const dataWithActions = promotions.map((promo) => ({
    ...promo,
    nb_etudiants: promo.etudiants ? promo.etudiants.length : 0,
    speciality_name: promo.speciality ? promo.speciality.nom : "Non définie",
    duree_annees: promo.speciality
      ? `${promo.speciality.duree_annees} ans`
      : "-",
    actions: (
      <div className="flex space-x-2">
        <button
          className="text-blue-600 hover:text-blue-800 font-medium"
          onClick={() => openYearsModal(promo)}
        >
          Années
        </button>
        <button
          className="text-green-600 hover:text-green-800 font-medium"
          onClick={() => openServiceModal(promo)}
        >
          Services (Legacy)
        </button>
        <button
          className="text-red-600 hover:text-red-800 font-medium"
          onClick={() => handleDeletePromotion(promo.id)}
        >
          Supprimer
        </button>
      </div>
    ),
  }));

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Promotions</h2>
      <Message text={message} type={type} />
      <button
        onClick={openModal}
        className="bg-blue-600 text-white px-4 py-2 rounded mb-6"
      >
        Créer une promotion
      </button>
      <h3 className="font-semibold mt-6 mb-2">Liste des promotions</h3>
      <Table columns={columns} data={dataWithActions} />

      {/* Create Promotion Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Créer une promotion"
      >
        <div className="space-y-3">
          <FormInput
            label="Nom de la promotion"
            value={newPromotion.nom}
            onChange={(e) =>
              setNewPromotion({ ...newPromotion, nom: e.target.value })
            }
            placeholder="Nom de la promotion"
          />
          <FormInput
            label="Année"
            type="number"
            value={newPromotion.annee}
            onChange={(e) =>
              setNewPromotion({ ...newPromotion, annee: e.target.value })
            }
            placeholder="Année"
          />
          <div>
            <label className="block mb-1 font-medium">Spécialité</label>
            <select
              value={newPromotion.speciality_id}
              onChange={(e) =>
                setNewPromotion({
                  ...newPromotion,
                  speciality_id: e.target.value,
                })
              }
              className="border p-2 rounded w-full"
            >
              <option value="">Sélectionner une spécialité (optionnel)</option>
              {specialities.map((speciality) => (
                <option key={speciality.id} value={speciality.id}>
                  {speciality.nom} ({speciality.duree_annees} ans)
                </option>
              ))}
            </select>
          </div>
          <hr className="my-2" />
          <div className="font-semibold mb-2">Ajouter des étudiants</div>
          <div className="flex gap-2 mb-2 items-end">
            <div className="flex-1">
              <FormInput
                label="Nom étudiant"
                value={newEtudiant.nom}
                onChange={(e) =>
                  setNewEtudiant({ ...newEtudiant, nom: e.target.value })
                }
                placeholder="Nom étudiant"
                className="mb-0"
              />
            </div>
            <div className="flex-1">
              <FormInput
                label="Prénom étudiant"
                value={newEtudiant.prenom}
                onChange={(e) =>
                  setNewEtudiant({ ...newEtudiant, prenom: e.target.value })
                }
                placeholder="Prénom étudiant"
                className="mb-0"
              />
            </div>
            <button
              onClick={ajouterEtudiant}
              className="bg-green-600 text-white px-4 py-2 rounded h-10"
            >
              Ajouter
            </button>
          </div>
          <div className="overflow-y-auto max-h-32 border rounded">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-2 py-1 text-left">Nom</th>
                  <th className="px-2 py-1 text-left">Prénom</th>
                  <th className="px-2 py-1 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {newPromotion.etudiants.map((etudiant) => (
                  <tr key={etudiant.id}>
                    <td className="px-2 py-1">{etudiant.nom}</td>
                    <td className="px-2 py-1">{etudiant.prenom}</td>
                    <td className="px-2 py-1">
                      <button
                        onClick={() => supprimerEtudiant(etudiant.id)}
                        className="text-red-500 text-xs hover:underline px-2 py-1"
                      >
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))}
                {newPromotion.etudiants.length === 0 && (
                  <tr>
                    <td colSpan={3} className="text-gray-400 text-center py-2">
                      Aucun étudiant ajouté
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <button
            onClick={handleCreatePromotion}
            className="bg-blue-600 text-white px-4 py-2 rounded w-full mt-4"
            disabled={
              newPromotion.etudiants.length === 0 ||
              !newPromotion.nom.trim() ||
              loading
            }
          >
            Créer la promotion
          </button>
        </div>
      </Modal>

      {/* Legacy Service Assignment Modal */}
      <Modal
        open={serviceModalOpen}
        onClose={() => setServiceModalOpen(false)}
        title={`Gestion des services (Legacy) - ${selectedPromotion?.nom}`}
      >
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2">Services assignés</h4>
            {promotionServices.length === 0 ? (
              <p className="text-gray-500 text-sm">Aucun service assigné</p>
            ) : (
              <div className="space-y-2">
                {promotionServices.map((service) => (
                  <div
                    key={service.id}
                    className="flex justify-between items-center p-2 bg-gray-50 rounded"
                  >
                    <div>
                      <span className="font-medium">{service.nom}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        ({service.places_disponibles} places,{" "}
                        {service.duree_stage_jours} jours)
                      </span>
                    </div>
                    <button
                      onClick={() => handleRemoveService(service.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                      disabled={loading}
                    >
                      Retirer
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h4 className="font-semibold mb-2">Services disponibles</h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {services
                .filter(
                  (service) =>
                    !promotionServices.find((ps) => ps.id === service.id)
                )
                .map((service) => (
                  <div
                    key={service.id}
                    className="flex justify-between items-center p-2 border rounded"
                  >
                    <div>
                      <span className="font-medium">{service.nom}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        ({service.places_disponibles} places,{" "}
                        {service.duree_stage_jours} jours)
                      </span>
                    </div>
                    <button
                      onClick={() => handleAssignService(service.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                      disabled={loading}
                    >
                      Assigner
                    </button>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </Modal>

      {/* Promotion Years Modal */}
      <Modal
        open={yearsModalOpen}
        onClose={() => setYearsModalOpen(false)}
        title={`Gestion des années - ${selectedPromotion?.nom}`}
      >
        <div className="space-y-4">
          {activeYear && (
            <div className="bg-green-50 border border-green-200 rounded p-3">
              <h4 className="font-semibold text-green-800 mb-1">
                Année active
              </h4>
              <p className="text-green-700">
                {activeYear.nom} ({activeYear.annee_calendaire})
              </p>
            </div>
          )}

          <div>
            <h4 className="font-semibold mb-2">Toutes les années</h4>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {promotionYears.map((year) => (
                <div
                  key={year.id}
                  className={`flex justify-between items-center p-3 border rounded ${
                    year.is_active
                      ? "bg-green-50 border-green-200"
                      : "bg-gray-50"
                  }`}
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{year.nom}</span>
                      <span className="text-sm text-gray-600">
                        ({year.annee_calendaire})
                      </span>
                      {year.is_active && (
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                          Active
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {year.date_debut && year.date_fin
                        ? `${new Date(
                            year.date_debut
                          ).toLocaleDateString()} - ${new Date(
                            year.date_fin
                          ).toLocaleDateString()}`
                        : "Dates non définies"}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => openYearServicesModal(year)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                      disabled={loading}
                    >
                      Services
                    </button>
                    {!year.is_active && (
                      <button
                        onClick={() => handleActivateYear(year.id)}
                        className="text-green-600 hover:text-green-800 text-sm"
                        disabled={loading}
                      >
                        Activer
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Modal>

      {/* Year Services Modal */}
      <Modal
        open={yearServicesModalOpen}
        onClose={() => setYearServicesModalOpen(false)}
        title={`Services de ${selectedYear?.nom}`}
      >
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2">Services assignés</h4>
            {yearServices.length === 0 ? (
              <p className="text-gray-500 text-sm">Aucun service assigné</p>
            ) : (
              <div className="space-y-2">
                {yearServices.map((service) => (
                  <div
                    key={service.id}
                    className="flex justify-between items-center p-2 bg-gray-50 rounded"
                  >
                    <div>
                      <span className="font-medium">{service.nom}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        ({service.places_disponibles} places,{" "}
                        {service.duree_stage_jours} jours)
                      </span>
                    </div>
                    <button
                      onClick={() => handleRemoveYearService(service.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                      disabled={loading}
                    >
                      Retirer
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h4 className="font-semibold mb-2">Services disponibles</h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {services
                .filter(
                  (service) => !yearServices.find((ys) => ys.id === service.id)
                )
                .map((service) => (
                  <div
                    key={service.id}
                    className="flex justify-between items-center p-2 border rounded"
                  >
                    <div>
                      <span className="font-medium">{service.nom}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        ({service.places_disponibles} places,{" "}
                        {service.duree_stage_jours} jours)
                      </span>
                    </div>
                    <button
                      onClick={() => handleAssignYearService(service.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                      disabled={loading}
                    >
                      Assigner
                    </button>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default PromotionsPage;
