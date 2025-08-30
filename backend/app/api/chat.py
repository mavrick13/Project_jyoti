from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter()


@router.get("/messages")
async def get_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get chat messages - placeholder endpoint
    """
    return {"message": "Chat messages endpoint - to be implemented", "user": current_user.name}


@router.post("/messages")
async def send_message(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send message - placeholder endpoint
    """
    return {"message": "Send message endpoint - to be implemented"}