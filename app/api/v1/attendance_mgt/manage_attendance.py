import uuid
from datetime import date, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from jose import jwt, JWTError

from app.core.config import settings
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR
from app.repositories.token import TokenRepository
from app.schemas.attendance_mgt import IdentifyEmployee, UpdateAttendance, CreateAttendance, AttendanceFilter
from app.services.attendance import AttendanceService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.services.face_recognition import FaceRecognitionService
from app.utils.logger import logger

router = APIRouter()
attendance_service = AttendanceService()
face_recognition_service = FaceRecognitionService()


@router.post('/attendances', description="Create a new attendance entry")
def create_attendance(
        payload: CreateAttendance,
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can create attendance.")

    attendance = attendance_service.create_attendance(payload)
    return {
        "success": True,
        "data": attendance,
        "message": "Attendance created successfully",
        "code": 201
    }


@router.put('/attendances/{attendance_id}', description="Update an attendance entry")
def update_attendance(
        attendance_id: int,
        payload: UpdateAttendance,
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can update attendance.")

    attendance = attendance_service.update_attendance(attendance_id, payload)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    return {
        "success": True,
        "data": attendance,
        "message": "Attendance updated successfully",
        "code": 200
    }


@router.delete('/attendances/{attendance_id}', description="Delete an attendance entry")
def delete_attendance(
        attendance_id: int,
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can delete attendance.")

    attendance = attendance_service.delete_attendance(attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    return {
        "success": True,
        "data": None,
        "message": "Attendance deleted successfully",
        "code": 200
    }


@router.get('/attendances', description="List all attendances with optional filtering by company_id")
def list_attendances(
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        limit: int = Query(default=10, description="Number of records per page"),
        page: int = Query(default=1, description="Page number"),
        q: Optional[str] = None
):
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        _filter = AttendanceFilter(limit=limit, page=page, search=q)
    elif auth_user.roles and ROLE_HR in auth_user.roles:
        _filter = AttendanceFilter(limit=limit, page=page, search=q, company_id=auth_user.company_id)
    else:
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN or HR roles can view attendances.")

    attendances, total_records, total_pages = attendance_service.list_attendances(_filter)
    return {
        "success": True,
        "data": attendances,
        "message": "Attendances retrieved successfully",
        "code": 200,
        "meta": {
            "limit": limit,
            "page": page,
            "total_records": total_records,
            "total_pages": total_pages
        }
    }


@router.get('/attendances/by-date', description="Get attendances filtered by date and optional company_id")
def get_attendance_by_date(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    filter_date: date = Query(
        default=date.today(),
        description="Filter attendances by specific date in YYYY-MM-DD format"
    ),
    company_id: Optional[uuid.UUID] = Query(
        default=None,
        description="Filter attendances by company_id (optional)"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by employee name or attendance description"
    ),
):
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access this data.")

    attendances, total_records, total_pages = attendance_service.list_attendances_by_date(
        filter_date=filter_date, company_id=company_id, search=search
    )

    return {
        "success": True,
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
                "company": {
                    "id": att.company.id,
                    "name": att.company.name,
                    "created_at": att.company.created_at,
                    "updated_at": att.company.updated_at,
                    "deleted_at": att.company.deleted_at,
                    "logo": att.company.logo,
                    "start_time": att.company.start_time,
                    "end_time": att.company.end_time,
                } if att.company else None,
                "employee": {
                    "id": att.employee.id,
                    "nik": att.employee.nik,
                    "user_name": att.employee.user_name,
                    "email": att.employee.email,
                    "position_id": att.employee.position_id,
                    "company_id": att.employee.company_id,
                    "created_at": att.employee.created_at,
                    "updated_at": att.employee.updated_at,
                    "deleted_at": att.employee.deleted_at,
                } if att.employee else None,
            }
            for att in attendances
        ],
        "message": "Attendance list by date",
        "code": 200,
        "meta": {
            "total_records": total_records,
            "total_pages": total_pages
        },
    }

@router.get('/attendances/by-month', description="Get attendances filtered by month, employee_id, and optional company_id")
def get_attendance_by_month(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    year: int = Query(
        default=datetime.now().year,
        description="Filter attendances by year (default is current year)"
    ),
    month: int = Query(
        default=datetime.now().month,
        description="Filter attendances by month (default is current month)"
    ),
    employee_id: Optional[uuid.UUID] = Query(
        default=None,
        description="Filter attendances by employee_id (optional)"
    ),
    company_id: Optional[uuid.UUID] = Query(
        default=None,
        description="Filter attendances by company_id (optional)"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by employee name or attendance description"
    ),
    limit: int = Query(default=10, description="Number of records per page"),
    page: int = Query(default=1, description="Page number"),
):
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access this data.")

    # Pass employee_id and company_id into the service method
    attendances, total_records, total_pages = attendance_service.list_attendances_by_month(
        year=year, 
        month=month, 
        employee_id=employee_id,
        company_id=company_id, 
        limit=limit, 
        page=page, 
        search=search
    )

    # Construct the response
    return {
        "success": True,
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
                "company": {
                    "id": att.company.id,
                    "name": att.company.name,
                    "created_at": att.company.created_at,
                    "updated_at": att.company.updated_at,
                    "deleted_at": att.company.deleted_at,
                    "logo": att.company.logo,
                    "start_time": att.company.start_time,
                    "end_time": att.company.end_time,
                } if att.company else None,
                "employee": {
                    "id": att.employee.id,
                    "nik": att.employee.nik,
                    "user_name": att.employee.user_name,
                    "email": att.employee.email,
                    "position_id": att.employee.position_id,
                    "company_id": att.employee.company_id,
                    "created_at": att.employee.created_at,
                    "updated_at": att.employee.updated_at,
                    "deleted_at": att.employee.deleted_at,
                } if att.employee else None,
            }
            for att in attendances
        ],
        "message": "Attendance list by month",
        "code": 200,
        "meta": {
            "limit": limit,
            "page": page,
            "total_records": total_records,
            "total_pages": total_pages
        },
    }

@router.post('/identify-face-employee', description="Identify employee and handle attendance")
def identify_face(
        request_body: IdentifyEmployee,
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access this data.")

    try:
        logger.info("Attempting to create attendance (check-in or check-out) via Local method...")

        # First, attempt to create attendance using the Local method
        attendance, employee_info = face_recognition_service.create(request_body)

        logger.info(f"Successfully completed {employee_info.get('action')} attendance via Local method.")
        return {
            'success': True,
            'data': {
                'nik': employee_info.get('nik', ''),
                'userName': employee_info.get('user_name', ''),
                'companyID': employee_info.get('company_id', ''),
                'companyName': employee_info.get('company_name', ''),
                'action': employee_info.get('action'),
                'timestamp': employee_info.get('timestamp')
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
                attendance, employee_info = face_recognition_service.identify_face_employee(request_body, user_company_id)

                logger.info(f"Successfully completed {employee_info.get('action')} attendance via RisetAI.")
                return {
                    'success': True,
                    'data': {
                        'nik': employee_info.get('nik', ''),
                        'fullName': employee_info.get('user_name', ''),
                        'companyID': employee_info.get('company_id', ''),
                        'companyName': employee_info.get('company_name', ''),
                        'action': employee_info.get('action'),
                        'timestamp': employee_info.get('timestamp')
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

@router.post('/detect-face', description="Detect face and return matched employee details")
def detect_face(
        request_body: IdentifyEmployee,
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access this data.")

    try:
        logger.info("Starting face detection process...")
        employee_info = face_recognition_service.detect_face(request_body)

        logger.info("Face successfully detected and matched.")
        return {
            'success': True,
            'data': employee_info,
            'message': "Face successfully detected and matched.",
            'code': 200
        }

    except HTTPException as e:
        logger.error(f"Face detection failed: {str(e)}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error in detect_face: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post('/identify-face-employee-wfh', description="Identify employee WFH and handle attendance")
def identify_face_wfh(
    request_body: IdentifyEmployee,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    """
    Endpoint untuk memvalidasi WFH Employee melalui face recognition dan mengelola absensi.
    """
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access this data.")

    # Validasi token
    token = request_body.token
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    try:
        token_repo = TokenRepository()
        if token_repo.is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token has already been used or is invalid")

        # Decode the token
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

        # Periksa kesesuaian company ID dalam token
        token_company_id = payload.get("company_id")
        if str(token_company_id) != str(auth_user.company_id):
            raise HTTPException(status_code=403, detail="Token is not valid for this user's company")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        logger.info("Starting attendance process via Local method...")

        # Proses absensi menggunakan metode lokal
        attendance, employee_info = face_recognition_service.create_wfh(request_body)

        # Tandai token sebagai revoked
        token_repo.add_revoked_token(token)

        logger.info(f"Successfully completed {employee_info.get('action')} attendance via Local method.")
        return {
            'success': True,
            'data': {
                'nik': employee_info.get('nik', ''),
                'userName': employee_info.get('user_name', ''),
                'companyID': employee_info.get('company_id', ''),
                'companyName': employee_info.get('company_name', ''),
                'action': employee_info.get('action'),
                'timestamp': employee_info.get('timestamp')
            },
            'message': f"Employee is Valid by Local. {employee_info.get('action')} successful",
            'code': 200
        }

    except HTTPException as e:
        # Jika Local method gagal, coba fallback ke RisetAI
        logger.warning(f"Local method failed with status {e.status_code}: {e.detail}")

        if e.status_code == 404:
            try:
                logger.info("Attempting RisetAI fallback for face identification...")

                # user_company_id = uuid.UUID(auth_user.company_id)
                # attendance, employee_info = face_recognition_service.identify_face_employee(request_body, user_company_id)
                #
                # # Tandai token sebagai revoked
                # token_repo.add_revoked_token(token)
                #
                # logger.info(f"Successfully completed {employee_info.get('action')} attendance via RisetAI.")
                # return {
                #     'success': True,
                #     'data': {
                #         'nik': employee_info.get('nik', ''),
                #         'userName': employee_info.get('user_name', ''),
                #         'companyID': employee_info.get('company_id', ''),
                #         'companyName': employee_info.get('company_name', ''),
                #         'action': employee_info.get('action'),
                #         'timestamp': employee_info.get('timestamp')
                #     },
                #     'message': f"Employee is Valid by RisetAI. {employee_info.get('action')} successful",
                #     'code': 200
                # }
            except Exception as riset_err:
                logger.error(f"RisetAI method failed: {str(riset_err)}")
                raise HTTPException(status_code=500, detail="Failed to process attendance via RisetAI")

    except Exception as err:
        logger.error(f"Error in identify_face_wfh: {str(err)}")
        raise HTTPException(status_code=500, detail="Failed to process attendance")



