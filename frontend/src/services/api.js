import axios from "axios";

const API_BASE_URL = "http://localhost:8003/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Promotions
export const getPromotions = () => api.get("/promotions");
export const createPromotion = (data) => api.post("/promotions", data);
export const updatePromotion = (id, data) => api.put(`/promotions/${id}`, data);
export const deletePromotion = (id) => api.delete(`/promotions/${id}`);

// Services
export const getServices = () => api.get("/services");
export const createService = (data) => api.post("/services", data);
export const updateService = (id, data) => api.put(`/services/${id}`, data);
export const deleteService = (id) => api.delete(`/services/${id}`);
export const getService = (id) => api.get(`/services/${id}`);

// Plannings
export const generatePlanning = (promoId, date_debut) =>
  api.post(`/plannings/generer/${promoId}?date_debut=${date_debut}`);
export const getPlanning = (promoId) => api.get(`/plannings/${promoId}`);
export const exportPlanningExcel = (promoId) =>
  api.get(`/plannings/${promoId}/export`, { responseType: "blob" });

// Student Schedules
export const getStudentSchedules = (promoId) =>
  api.get(`/student_schedules/${promoId}`);
export const getStudentScheduleDetail = (scheduleId) =>
  api.get(`/student_schedules/detail/${scheduleId}`);
export const createStudentSchedule = (data) =>
  api.post("/student_schedules", data);
export const updateStudentSchedule = (id, data) =>
  api.put(`/student_schedules/${id}`, data);
export const deleteStudentSchedule = (id) =>
  api.delete(`/student_schedules/${id}`);

// Specialities
export const getSpecialities = () => api.get("/specialities");
export const createSpeciality = (data) => api.post("/specialities", data);
export const getSpeciality = (id) => api.get(`/specialities/${id}`);
export const updateSpeciality = (id, data) =>
  api.put(`/specialities/${id}`, data);
export const deleteSpeciality = (id) => api.delete(`/specialities/${id}`);

// Promotion-Service Assignments (Legacy - for backward compatibility)
export const assignServiceToPromotion = (promotionId, serviceId) =>
  api.post(`/promotions/${promotionId}/services/${serviceId}`);
export const removeServiceFromPromotion = (promotionId, serviceId) =>
  api.delete(`/promotions/${promotionId}/services/${serviceId}`);
export const getPromotionServices = (promotionId) =>
  api.get(`/promotions/${promotionId}/services`);

// Promotion Years
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
