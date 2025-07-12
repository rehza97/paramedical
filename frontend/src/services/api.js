import axios from "axios";

const API_BASE_URL = "http://localhost:8001/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ===== HEALTH CHECK =====
export const healthCheck = () => api.get("/health");

// ===== PROMOTIONS =====
export const getPromotions = () => api.get("/promotions");
export const createPromotion = (data) => api.post("/promotions", data);
export const getPromotion = (id) => api.get(`/promotions/${id}`);
export const updatePromotion = (id, data) => api.put(`/promotions/${id}`, data);
export const deletePromotion = (id) => api.delete(`/promotions/${id}`);

// Promotion-Service Assignments (Legacy)
export const assignServiceToPromotion = (promotionId, serviceId) =>
  api.post(`/promotions/${promotionId}/services/${serviceId}`);
export const removeServiceFromPromotion = (promotionId, serviceId) =>
  api.delete(`/promotions/${promotionId}/services/${serviceId}`);
export const getPromotionServices = (promotionId) =>
  api.get(`/promotions/${promotionId}/services`);

// ===== SERVICES =====
export const getServices = () => api.get("/services");
export const createService = (data) => api.post("/services", data);
export const getService = (id) => api.get(`/services/${id}`);
export const updateService = (id, data) => api.put(`/services/${id}`, data);
export const deleteService = (id) => api.delete(`/services/${id}`);

// ===== SPECIALITIES =====
export const getSpecialities = () => api.get("/specialities");
export const createSpeciality = (data) => api.post("/specialities", data);
export const getSpeciality = (id) => api.get(`/specialities/${id}`);
export const updateSpeciality = (id, data) =>
  api.put(`/specialities/${id}`, data);
export const deleteSpeciality = (id) => api.delete(`/specialities/${id}`);

// ===== PLANNINGS =====
export const generatePlanning = (promoId, date_debut) =>
  api.post(`/plannings/generer/${promoId}?date_debut=${date_debut}`);
export const getPlanning = (promoId) => api.get(`/plannings/${promoId}`);
export const getStudentPlanning = (promoId, etudiantId) =>
  api.get(`/plannings/etudiant/${promoId}/${etudiantId}`);
export const exportPlanningExcel = (promoId) =>
  api.get(`/plannings/${promoId}/export`, { responseType: "blob" });
export const updateRotation = (rotationId, data) =>
  api.put(`/plannings/rotation/${rotationId}`, data);
export const getPromotionsForPlanning = (planningId) =>
  api.get(`/plannings/${planningId}/promotions`);
export const getPlanningDetails = (planningId) =>
  api.get(`/plannings/${planningId}/details`);
export const validatePlanning = (planningId) =>
  api.get(`/plannings/${planningId}/validate`);

// ===== STUDENT SCHEDULES =====
export const getStudentSchedule = (etudiantId) =>
  api.get(`/student-schedules/etudiant/${etudiantId}`);
export const getStudentScheduleHistory = (etudiantId) =>
  api.get(`/student-schedules/etudiant/${etudiantId}/historique`);
export const getStudentProgress = (etudiantId) =>
  api.get(`/student-schedules/etudiant/${etudiantId}/progression`);
export const updateServiceStatus = (scheduleId, serviceId, data) =>
  api.put(`/student-schedules/${scheduleId}/service/${serviceId}/statut`, data);
export const getPlanningSummary = (planningId) =>
  api.get(`/student-schedules/planning/${planningId}/resume`);
export const archiveSchedule = (scheduleId) =>
  api.post(`/student-schedules/${scheduleId}/archiver`);
export const createScheduleVersion = (scheduleId) =>
  api.post(`/student-schedules/${scheduleId}/nouvelle-version`);
export const getScheduleById = (scheduleId) =>
  api.get(`/student-schedules/${scheduleId}`);
export const createStudentSchedule = (data) =>
  api.post("/student-schedules", data);
export const updateStudentSchedule = (id, data) =>
  api.put(`/student-schedules/${id}`, data);
export const deleteStudentSchedule = (id) =>
  api.delete(`/student-schedules/${id}`);
export const createScheduleDetail = (scheduleId, data) =>
  api.post(`/student-schedules/${scheduleId}/detail`, data);
export const updateScheduleDetail = (scheduleId, detailId, data) =>
  api.put(`/student-schedules/${scheduleId}/detail/${detailId}`, data);
export const deleteScheduleDetail = (scheduleId, detailId) =>
  api.delete(`/student-schedules/${scheduleId}/detail/${detailId}`);
export const exportScheduleExcel = (scheduleId) =>
  api.get(`/student-schedules/${scheduleId}/export`, { responseType: "blob" });
export const exportPlanningSchedulesExcel = (planningId) =>
  api.get(`/student-schedules/planning/${planningId}/export`, {
    responseType: "blob",
  });

// Legacy endpoints for backward compatibility
export const getStudentSchedules = (promoId) =>
  api.get(`/student-schedules/promotion/${promoId}`);
export const getStudentScheduleDetail = (scheduleId) =>
  api.get(`/student-schedules/detail/${scheduleId}`);

// ===== PROMOTION YEARS =====
export const createPromotionYears = (promotionId) =>
  api.post(`/promotion-years/create-for-promotion/${promotionId}`);
export const getPromotionYears = (promotionId) =>
  api.get(`/promotion-years/promotion/${promotionId}`);
export const getActivePromotionYear = (promotionId) =>
  api.get(`/promotion-years/promotion/${promotionId}/active`);
export const activatePromotionYear = (promotionYearId) =>
  api.put(`/promotion-years/${promotionYearId}/activate`);
export const getPromotionYear = (promotionYearId) =>
  api.get(`/promotion-years/${promotionYearId}`);
export const updatePromotionYear = (promotionYearId, data) =>
  api.put(`/promotion-years/${promotionYearId}`, data);

// Promotion Year-Service Assignments
export const assignServiceToPromotionYear = (promotionYearId, serviceId) =>
  api.post(`/promotion-years/${promotionYearId}/services/${serviceId}`);
export const removeServiceFromPromotionYear = (promotionYearId, serviceId) =>
  api.delete(`/promotion-years/${promotionYearId}/services/${serviceId}`);
export const getPromotionYearServices = (promotionYearId) =>
  api.get(`/promotion-years/${promotionYearId}/services`);

// Planning Settings API
export const getPlanningSettings = () => api.get("/planning-settings/");
export const createPlanningSettings = (data) =>
  api.post("/planning-settings/", data);
export const updatePlanningSettings = (data) =>
  api.put("/planning-settings/", data);
