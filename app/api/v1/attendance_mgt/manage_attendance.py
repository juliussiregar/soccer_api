import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from app.schemas.attendance_mgt import CreateCheckIn, UpdateCheckOut, IdentifyEmployee
from app.services.attendance import AttendanceService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.utils.exception import UnprocessableException, InternalErrorException
from app.utils.logger import logger

router = APIRouter()
attendance_service = AttendanceService()

# @router.post('/attendance/check-in')
# def check_in(
#     payload: CreateCheckIn,
#     auth_user: AuthUser = Depends(jwt_middleware)
# ):
#     try:
#         attendance = attendance_service.create_check_in(payload)
#     except UnprocessableException as e:
#         raise HTTPException(status_code=422, detail=str(e))
#     except InternalErrorException as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#     return {
#         "message": "Check-in successful",
#         "attendance": {
#             "employee_id": attendance.employee_id,
#             "check_in": attendance.check_in,
#             "location": attendance.location,
#             "type": attendance.type,
#             "created_at": attendance.created_at
#         }
#     }
#
# @router.put('/attendance/check-out')
# def check_out(
#     payload: UpdateCheckOut,
#     auth_user: AuthUser = Depends(jwt_middleware)
# ):
#     try:
#         attendance = attendance_service.update_check_out(payload)
#     except UnprocessableException as e:
#         raise HTTPException(status_code=422, detail=str(e))
#     except InternalErrorException as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#     return {
#         "message": "Check-out successful",
#         "attendance": {
#             "employee_id": attendance.employee_id,
#             "check_out": attendance.check_out,
#             "location": attendance.location,
#             "late": attendance.late,
#             "overtime": attendance.overtime,
#             "description": attendance.description,
#             "updated_at": attendance.updated_at
#         }
#     }

@router.get('/attendance/by-date')
def get_attendance_by_date(
    filter_date: date = Query(
        default=date.today(),
        description="Filter date in YYYY-MM-DD format"
    ),
    auth_user: AuthUser = Depends(jwt_middleware)
):
    attendances = attendance_service.list_attendances_by_date(filter_date)

    return {
        "data": [
            {
                "id": att.id,
                "employee_id": att.employee_id,
                "company_id": att.company_id,
                "check_in": att.check_in,
                "check_out": att.check_out,
                "photo_in": att.photo_in,
                "photo_out": att.photo_out,
                "location": att.location,
                "type": att.type,
                "late": att.late,
                "overtime": att.overtime,
                "description": att.description,
                "total_time": str(att.check_out - att.check_in) if att.check_out else None,
                "created_at": att.created_at,
            }
            for att in attendances
        ]
    }

@router.post('/identify-face-employee', description="Identify employee and handle attendance")
def identify_face(
        request_body: IdentifyEmployee,
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    try:
        logger.info("Attempting to create attendance (check-in or check-out) via Local method...")

        # First, attempt to create attendance using the Local method
        attendance, employee_info = attendance_service.create(request_body)

        logger.info(f"Successfully completed {employee_info.get('action')} attendance via Local method.")
        return {
            'status': 200,
            'message': f"Employee is Valid by Local. {employee_info.get('action')} successful",
            'data': {
                'nik': employee_info.get('nik', ''),
                'userName': employee_info.get('user_name', ''),
                'companyID': employee_info.get('company_id', ''),
                'companyName': employee_info.get('company_name', ''),
                'action': employee_info.get('action')
            }
        }

    except HTTPException as e:
        # If Local method fails with a 404, attempt RisetAI
        logger.info(f"Attendance creation failed via Local method with status {e.status_code}")

        if e.status_code == 404:
            try:
                logger.info("Local method failed; attempting fallback to RisetAI for face identification...")

                # Extract the company_id of the authenticated user
                user_company_id = uuid.UUID(auth_user.company_id)

                # Attempt to identify the face via RisetAI and perform check-in/check-out
                attendance, employee_info = attendance_service.identify_face_employee(request_body, user_company_id)

                logger.info(f"Successfully completed {employee_info.get('action')} attendance via RisetAI.")
                return {
                    'status': 200,
                    'message': f"Employee is Valid by RisetAI. {employee_info.get('action')} successful",
                    'data': {
                        'nik': employee_info.get('nik', ''),
                        'fullName': employee_info.get('user_name', ''),
                        'companyID': employee_info.get('company_id', ''),
                        'companyName': employee_info.get('company_name', ''),
                        'action': employee_info.get('action')
                    }
                }
            except Exception as identify_err:
                logger.error(f"Fallback identification via RisetAI failed: {str(identify_err)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Both identification methods failed: {str(identify_err)}"
                )
        else:
            logger.error(f"Non-fallback HTTP error occurred: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Unexpected error in identify_face: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )



