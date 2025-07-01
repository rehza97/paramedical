from fastapi import APIRouter
from .endpoints import promotions, services, plannings, student_schedules, specialities, promotion_years

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(promotions.router, prefix="/promotions", tags=["promotions"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(plannings.router, prefix="/plannings", tags=["plannings"])
api_router.include_router(student_schedules.router, prefix="/student-schedules", tags=["student-schedules"])
api_router.include_router(specialities.router, prefix="/specialities", tags=["specialities"])
api_router.include_router(promotion_years.router, prefix="/promotion-years", tags=["promotion-years"]) 
from .endpoints import promotions, services, plannings, student_schedules, specialities, promotion_years

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(promotions.router, prefix="/promotions", tags=["promotions"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(plannings.router, prefix="/plannings", tags=["plannings"])
api_router.include_router(student_schedules.router, prefix="/student-schedules", tags=["student-schedules"])
api_router.include_router(specialities.router, prefix="/specialities", tags=["specialities"])
api_router.include_router(promotion_years.router, prefix="/promotion-years", tags=["promotion-years"]) 
 
 