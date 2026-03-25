from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_migrations():
    return {"migrations": [], "message": "No migrations found yet. Waiting for Step 1."}
