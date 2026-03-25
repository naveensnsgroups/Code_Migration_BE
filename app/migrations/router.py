from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_migrations():
    """Get list of active migrations."""
    return [
        {"id": "m1", "title": "Legacy PHP to FastAPI", "status": "active"},
        {"id": "m2", "title": "Monolith to Microservices", "status": "planned"}
    ]
