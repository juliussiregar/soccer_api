import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from app.core.constants.auth import ROLE_ADMIN, ROLE_HR
from app.schemas.attendance_mgt import IdentifyEmployee
from app.services.attendance import AttendanceService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.utils.logger import logger

router = APIRouter()
attendance_service = AttendanceService()

@router.get('/attendance/by-company', description="Get attendance by company ID")
def get_attendance_by_company(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    company_id: uuid.UUID,
    limit: int = 10,
    page: int = 1,
):
    # Check if the user has the required roles
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access attendance records.")

    # Fetch attendance data for the specified company
    attendances, total_records, total_pages = attendance_service.list_attendances_by_company(company_id, limit, page)

    return {
        'success': True,
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
        ],
        'message': "Attendance list by company",
        'code': 200,
        "meta": {
            "limit": limit,
            "page": page,
            "total_records": total_records,
            "total_pages": total_pages
        }
    }


@router.get('/attendance/by-date', description="Get attendance by date with pagination")
def get_attendance_by_date(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    filter_date: date = Query(
        default=date.today(),
        description="Filter date in YYYY-MM-DD format"
    ),
    limit: int = 10,
    page: int = 1,
):
    # Check if the user has the required roles
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access attendance records.")

    # Fetch attendance data for the specified date with pagination
    attendances, total_records, total_pages = attendance_service.list_attendances_by_date(filter_date, limit, page)

    return {
        'success': True,
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
        ],
        'message': "Attendance list by date",
        'code': 200,
        "meta": {
            "limit": limit,
            "page": page,
            "total_records": total_records,
            "total_pages": total_pages
        }
    }


@router.get('/attendance/by-month', description="Get attendance by month")
def get_attendance_by_month(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., description="Year"),
    limit: int = 10,
    page: int = 1,
):
    # Check if the user has the required roles
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access attendance records.")

    # Fetch attendance data for the specified month and year
    attendances, total_records, total_pages = attendance_service.list_attendances_by_month(month, year, limit, page)

    return {
        'success': True,
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
        ],
        'message': "Attendance list by month",
        'code': 200,
        "meta": {
            "limit": limit,
            "page": page,
            "total_records": total_records,
            "total_pages": total_pages
        }
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
            'success': True,
            'data': {
                'nik': employee_info.get('nik', ''),
                'userName': employee_info.get('user_name', ''),
                'companyID': employee_info.get('company_id', ''),
                'companyName': employee_info.get('company_name', ''),
                'action': employee_info.get('action')
            },
            'message': f"Employee is Valid by Local. {employee_info.get('action')} successful",
            'code': 200
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
                    'success': True,
                    'data': {
                        'nik': employee_info.get('nik', ''),
                        'fullName': employee_info.get('user_name', ''),
                        'companyID': employee_info.get('company_id', ''),
                        'companyName': employee_info.get('company_name', ''),
                        'action': employee_info.get('action')
                    },
                    'message': f"Employee is Valid by RisetAI. {employee_info.get('action')} successful",
                    'code': 200,
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



