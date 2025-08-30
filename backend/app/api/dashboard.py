from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.farmer import Farmer

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics
    """
    total_farmers = db.query(Farmer).count()
    
    # Installation statistics
    completed_installations = db.query(Farmer).filter(
        Farmer.installation_status == "Done"
    ).count()
    
    pending_installations = db.query(Farmer).filter(
        Farmer.installation_status.in_(["Not Started", "In Progress"])
    ).count()
    
    # Dispatch statistics
    dispatched_today = db.query(Farmer).filter(
        func.date(Farmer.dispatch_date) == func.current_date()
    ).count()
    
    return {
        "totalFarmers": total_farmers,
        "completedInstallations": completed_installations,
        "pendingInstallations": pending_installations,
        "dispatchedToday": dispatched_today,
        "pendingTasks": 0  # Placeholder until tasks are implemented
    }