from sqlalchemy import Column, String, Date, Text, Integer, ForeignKey, DateTime, Computed
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class SchemeType(str, enum.Enum):
    MTS = "MTS"
    SADBHAV = "SADBHAV"
    SAYLIP = "SAYLIP"
    CROMPTON = "CROMPTON"


class JSRStatus(str, enum.Enum):
    APPROVED = "Approved"
    PENDING = "Pending" 
    REJECTED = "Rejected"


class DispatchStatus(str, enum.Enum):
    NOT_DISPATCHED = "Not Dispatched"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    DONE = "Done"


class InstallationStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ISSUES = "Issues"
    DONE = "Done"


class ICRStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DONE = "Done"


class Farmer(Base):
    __tablename__ = "farmers"

    beneficiary_id = Column(String(50), primary_key=True, index=True)
    beneficiary_name = Column(String(255), nullable=False)
    phone_no = Column(String(15), nullable=True)
    aadhaar_no = Column(String(20), nullable=True)
    scheme = Column(String(20), nullable=False)
    pumphp = Column(String(20), nullable=True)
    pumphead = Column(String(20), nullable=True)
    pumphp_combined = Column(String(50), Computed("pumphp || '-' || pumphead"))
    selection_date = Column(Date, nullable=True)
    circle_name = Column(String(100), nullable=True)
    taluka_name = Column(String(100), nullable=True)
    village_name = Column(String(100), nullable=True)
    installer_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    ld = Column(String(50), nullable=True)
    jsr_status = Column(String(20), nullable=True)
    dispatch_status = Column(String(50), nullable=True)
    dispatch_date = Column(Date, nullable=True)
    vehicle_no = Column(String(50), nullable=True)
    driver_info = Column(String(255), nullable=True)
    installation_status = Column(String(50), nullable=True)
    installation_remark = Column(Text, nullable=True)
    icr_status = Column(String(50), nullable=True)
    photos = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    installer = relationship("User", foreign_keys=[installer_user_id])