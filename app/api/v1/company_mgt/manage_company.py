import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated

from app.repositories.company import CompanyRepository
from app.schemas.company import CreateNewCompany, CompanyFilter, UpdateCompany
from app.schemas.position import PositionFilter
from app.services.company import CompanyService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR

router = APIRouter()
company_service = CompanyService()
company_repo = CompanyRepository()

@router.post('/companies', description="Create a new Company with FaceGallery")
def create_company(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    request_body: CreateNewCompany
):
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can create a new company."
        )

    # Check if the company name is already taken
    if company_repo.is_name_used(request_body.name):
        raise HTTPException(
            status_code=400,
            detail="Error: A company with this name already exists."
        )

    company = company_service.create_company(request_body)
    return {
        "success": True,
        "data": {
                "id": company.id,
                "name": company.name,
                "logo": company.logo,
                "start_time": company.start_time,
                "end_time": company.end_time,
                "created_at": company.created_at
        },
        "message": "Company created successfully",
        "code": 200
    }

@router.get('/companies')
def get_companies(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 100,
    page: int = 1,
    q: Optional[str] = None
):
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        _filter = PositionFilter(limit=limit, page=page, search=q)
    else:
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN role can get all companies.")

    _filter = CompanyFilter(limit=limit, page=page, search=q)
    companies, total_rows, total_pages = company_service.list_companies(_filter)

    return {
        "success": True,
        "data": [
            {
                "id": company.id,
                "name": company.name,
                "logo": company.logo,
                "start_time": company.start_time,
                "end_time": company.end_time,
                "created_at": company.created_at,
                "updated_at": company.updated_at
            }
            for company in companies
        ],
        "message": "Companies retrieved successfully",
        "code": 200,
        "meta": {
            "limit": limit,
            "page": page,
            "total_rows": total_rows,
            "total_pages": total_pages
        }
    }

@router.get('/companies/{company_id}')
def get_company_by_id(
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        company_id: uuid.UUID
):
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        company = company_service.get_company(company_id)
        logging.info(f"Access granted to ADMIN for company_id {company_id}")
    elif auth_user.roles and ROLE_HR in auth_user.roles:
        company = company_service.get_company(company_id)
        logging.info(f"HR access attempt for company_id {company_id}")
        logging.info(f"Company retrieved: {company.id if company else 'None'}, Auth user company_id: {auth_user.company_id}")

        if not company or str(company.id) != str(auth_user.company_id):
            logging.warning("Access denied: HR role attempted to access another company's data.")
            raise HTTPException(
                status_code=403,
                detail="Access denied: HR role can only access data for their assigned company."
            )
    else:
        logging.warning("Access denied: user lacks necessary role.")
        raise HTTPException(status_code=403, detail="Access denied for this role")

    if company is None:
        logging.error("Company not found.")
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "success": True,
        "data": {
            "id": company.id,
            "name": company.name,
            "logo": company.logo,
            "start_time": company.start_time,
            "end_time": company.end_time,
            "created_at": company.created_at,
            "updated_at": company.updated_at
        },
        "message": "Company details retrieved successfully",
        "code": 200
    }

@router.put('/companies/{company_id}')
def update_company(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    company_id: uuid.UUID,
    request_body: UpdateCompany
):
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can update company."
        )

    company = company_service.update_company(company_id, request_body)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found or could not be updated")

    return {
        "success": True,
        "data": {
            "id": company.id,
            "name": company.name,
            "logo": company.logo,
            "start_time": company.start_time,
            "end_time": company.end_time,
            "updated_at": company.updated_at
        },
        "message": "Company updated successfully",
        "code": 200
    }

@router.delete('/companies/{company_id}', description="Delete a company and its FaceGallery")
def delete_company(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    company_id: uuid.UUID
):
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can delete a company."
        )

    company = company_service.delete_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "success": True,
        "data": None,
        "message": "Company and its FaceGallery deleted successfully",
        "code": 200
    }
