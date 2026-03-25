from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    """Service health check."""
    return {"status": "ok", "service": "Code Migration Backend"}
