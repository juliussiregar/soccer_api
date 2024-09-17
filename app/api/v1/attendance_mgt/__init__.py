from fastapi import APIRouter

from app.api.v1.attendance_mgt import manage_attendance


router = APIRouter(tags=["Attendance Management"])

router.include_router(manage_attendance.router)
