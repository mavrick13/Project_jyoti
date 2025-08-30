from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
import math

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.farmer import Farmer
from ..schemas.farmer import (
    FarmerCreate, 
    FarmerUpdate, 
    FarmerResponse, 
    FarmerListResponse,
    FarmerFilter
)
from ..core.config import settings

router = APIRouter()


@router.get("/", response_model=FarmerListResponse)
async def get_farmers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Page size"),
    scheme: Optional[str] = Query(None, description="Filter by scheme"),
    circle_name: Optional[str] = Query(None, description="Filter by circle"),
    taluka_name: Optional[str] = Query(None, description="Filter by taluka"),
    village_name: Optional[str] = Query(None, description="Filter by village"),
    jsr_status: Optional[str] = Query(None, description="Filter by JSR status"),
    dispatch_status: Optional[str] = Query(None, description="Filter by dispatch status"),
    installation_status: Optional[str] = Query(None, description="Filter by installation status"),
    icr_status: Optional[str] = Query(None, description="Filter by ICR status"),
    installer_user_id: Optional[int] = Query(None, description="Filter by installer"),
    search: Optional[str] = Query(None, description="Search in name, phone, beneficiary_id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of farmers with filtering
    """
    query = db.query(Farmer)
    
    # Apply filters
    if scheme:
        query = query.filter(Farmer.scheme == scheme)
    if circle_name:
        query = query.filter(Farmer.circle_name == circle_name)
    if taluka_name:
        query = query.filter(Farmer.taluka_name == taluka_name)
    if village_name:
        query = query.filter(Farmer.village_name == village_name)
    if jsr_status:
        query = query.filter(Farmer.jsr_status == jsr_status)
    if dispatch_status:
        query = query.filter(Farmer.dispatch_status == dispatch_status)
    if installation_status:
        query = query.filter(Farmer.installation_status == installation_status)
    if icr_status:
        query = query.filter(Farmer.icr_status == icr_status)
    if installer_user_id:
        query = query.filter(Farmer.installer_user_id == installer_user_id)
    
    # Apply search
    if search:
        search_filter = or_(
            Farmer.beneficiary_name.ilike(f"%{search}%"),
            Farmer.phone_no.ilike(f"%{search}%"),
            Farmer.beneficiary_id.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    farmers = query.offset(offset).limit(page_size).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / page_size)
    
    return FarmerListResponse(
        farmers=[FarmerResponse.from_orm(farmer) for farmer in farmers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{beneficiary_id}", response_model=FarmerResponse)
async def get_farmer(
    beneficiary_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get farmer by beneficiary ID
    """
    farmer = db.query(Farmer).filter(Farmer.beneficiary_id == beneficiary_id).first()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    return FarmerResponse.from_orm(farmer)


@router.post("/", response_model=FarmerResponse)
async def create_farmer(
    farmer_data: FarmerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new farmer
    """
    # Check if farmer already exists
    existing_farmer = db.query(Farmer).filter(
        Farmer.beneficiary_id == farmer_data.beneficiary_id
    ).first()
    
    if existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmer with this beneficiary ID already exists"
        )
    
    # Create new farmer
    farmer = Farmer(**farmer_data.dict())
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    
    return FarmerResponse.from_orm(farmer)


@router.put("/{beneficiary_id}", response_model=FarmerResponse)
async def update_farmer(
    beneficiary_id: str,
    farmer_data: FarmerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update farmer information
    """
    farmer = db.query(Farmer).filter(Farmer.beneficiary_id == beneficiary_id).first()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Update farmer with provided data
    update_data = farmer_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farmer, field, value)
    
    db.commit()
    db.refresh(farmer)
    
    return FarmerResponse.from_orm(farmer)


@router.delete("/{beneficiary_id}")
async def delete_farmer(
    beneficiary_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a farmer (admin only)
    """
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete farmers"
        )
    
    farmer = db.query(Farmer).filter(Farmer.beneficiary_id == beneficiary_id).first()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    db.delete(farmer)
    db.commit()
    
    return {"message": "Farmer deleted successfully"}


@router.get("/stats/summary")
async def get_farmers_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get summary statistics for farmers
    """
    total_farmers = db.query(Farmer).count()
    
    # Count by status
    jsr_stats = db.query(
        Farmer.jsr_status, 
        func.count(Farmer.beneficiary_id)
    ).group_by(Farmer.jsr_status).all()
    
    dispatch_stats = db.query(
        Farmer.dispatch_status,
        func.count(Farmer.beneficiary_id)
    ).group_by(Farmer.dispatch_status).all()
    
    installation_stats = db.query(
        Farmer.installation_status,
        func.count(Farmer.beneficiary_id)
    ).group_by(Farmer.installation_status).all()
    
    icr_stats = db.query(
        Farmer.icr_status,
        func.count(Farmer.beneficiary_id)
    ).group_by(Farmer.icr_status).all()
    
    scheme_stats = db.query(
        Farmer.scheme,
        func.count(Farmer.beneficiary_id)
    ).group_by(Farmer.scheme).all()
    
    return {
        "total_farmers": total_farmers,
        "jsr_status": dict(jsr_stats),
        "dispatch_status": dict(dispatch_stats),
        "installation_status": dict(installation_stats),
        "icr_status": dict(icr_stats),
        "scheme_distribution": dict(scheme_stats)
    }