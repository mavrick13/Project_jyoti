from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class SchemeType(str, Enum):
    MTS = "MTS"
    SADBHAV = "SADBHAV"
    SAYLIP = "SAYLIP"
    CROMPTON = "CROMPTON"


class JSRStatus(str, Enum):
    APPROVED = "Approved"
    PENDING = "Pending"
    REJECTED = "Rejected"


class DispatchStatus(str, Enum):
    NOT_DISPATCHED = "Not Dispatched"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    DONE = "Done"


class InstallationStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ISSUES = "Issues"
    DONE = "Done"


class ICRStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DONE = "Done"


# Base Farmer schema
class FarmerBase(BaseModel):
    beneficiary_name: str = Field(..., min_length=2, max_length=255)
    phone_no: Optional[str] = Field(None, max_length=15)
    aadhaar_no: Optional[str] = Field(None, max_length=20)
    scheme: str = Field(..., max_length=20)
    pumphp: Optional[str] = Field(None, max_length=20)
    pumphead: Optional[str] = Field(None, max_length=20)
    selection_date: Optional[date] = None
    circle_name: Optional[str] = Field(None, max_length=100)
    taluka_name: Optional[str] = Field(None, max_length=100)
    village_name: Optional[str] = Field(None, max_length=100)
    installer_user_id: Optional[int] = None
    ld: Optional[str] = Field(None, max_length=50)
    jsr_status: Optional[str] = Field(None, max_length=20)
    dispatch_status: Optional[str] = Field(None, max_length=50)
    dispatch_date: Optional[date] = None
    vehicle_no: Optional[str] = Field(None, max_length=50)
    driver_info: Optional[str] = Field(None, max_length=255)
    installation_status: Optional[str] = Field(None, max_length=50)
    installation_remark: Optional[str] = None
    icr_status: Optional[str] = Field(None, max_length=50)
    photos: Optional[str] = None


# Schema for creating a farmer
class FarmerCreate(FarmerBase):
    beneficiary_id: str = Field(..., min_length=1, max_length=50)


# Schema for updating a farmer
class FarmerUpdate(BaseModel):
    beneficiary_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_no: Optional[str] = Field(None, max_length=15)
    aadhaar_no: Optional[str] = Field(None, max_length=20)
    scheme: Optional[str] = Field(None, max_length=20)
    pumphp: Optional[str] = Field(None, max_length=20)
    pumphead: Optional[str] = Field(None, max_length=20)
    selection_date: Optional[date] = None
    circle_name: Optional[str] = Field(None, max_length=100)
    taluka_name: Optional[str] = Field(None, max_length=100)
    village_name: Optional[str] = Field(None, max_length=100)
    installer_user_id: Optional[int] = None
    ld: Optional[str] = Field(None, max_length=50)
    jsr_status: Optional[str] = Field(None, max_length=20)
    dispatch_status: Optional[str] = Field(None, max_length=50)
    dispatch_date: Optional[date] = None
    vehicle_no: Optional[str] = Field(None, max_length=50)
    driver_info: Optional[str] = Field(None, max_length=255)
    installation_status: Optional[str] = Field(None, max_length=50)
    installation_remark: Optional[str] = None
    icr_status: Optional[str] = Field(None, max_length=50)
    photos: Optional[str] = None


# Schema for farmer response
class FarmerResponse(FarmerBase):
    beneficiary_id: str
    pumphp_combined: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for farmer list response with pagination
class FarmerListResponse(BaseModel):
    farmers: list[FarmerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Schema for farmer filters
class FarmerFilter(BaseModel):
    scheme: Optional[str] = None
    circle_name: Optional[str] = None
    taluka_name: Optional[str] = None
    village_name: Optional[str] = None
    jsr_status: Optional[str] = None
    dispatch_status: Optional[str] = None
    installation_status: Optional[str] = None
    icr_status: Optional[str] = None
    installer_user_id: Optional[int] = None
    search: Optional[str] = None  # Search in name, phone, beneficiary_id