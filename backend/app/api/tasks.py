from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter()


@router.get("/")
async def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tasks - placeholder endpoint
    """
    return {"message": "Tasks endpoint - to be implemented", "user": current_user.name}


@router.post("/")
async def create_task(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create task - placeholder endpoint
    """
    return {"message": "Create task endpoint - to be implemented"}