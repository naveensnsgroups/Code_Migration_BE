from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

class AnalysisRequest(BaseModel):
    path: str

@router.get("/")
async def list_migrations():
    """Get list of active migrations."""
    return [
        {"id": "m1", "title": "Legacy PHP to FastAPI", "status": "active"},
        {"id": "m2", "title": "Monolith to Microservices", "status": "planned"}
    ]

class LogicUnit(BaseModel):
    id: str
    name: str
    type: str # ui_component, api_logic, business_rule
    priority: str # high, medium, low
    description: str

from app.core.llm import gemini_provider
from app.files.service import file_system_service

from app.migrations.service import project_analysis_service

@router.post("/analyze-project")
async def analyze_project():
    """Perform a deep AI analysis of the entire repository."""
    try:
        analysis = await project_analysis_service.analyze_full_project()
        
        return {
            "status": "success",
            "stack": analysis.get("stack", {"frontend": "unknown", "backend": "unknown"}),
            "logic_units": analysis.get("logic_units", []),
            "logs": [
                "Recursively scanned repository structure...",
                "Detected project-wide patterns and tech stack.",
                "Gemini Architect completed global analysis.",
                "Ready for cross-file migration mapping."
            ]
        }
    except Exception as e:
        print(f"Project analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Project analysis failed: {str(e)}")
class MigrationExecuteRequest(BaseModel):
    selected_units: list[LogicUnit]

@router.post("/execute")
async def execute_migration(request: MigrationExecuteRequest):
    """Perform selective migration of selected logic units."""
    if not request.selected_units:
        raise HTTPException(status_code=400, detail="No items selected for migration")
        
    results = []
    logs = [
        f"Initializing surgical extraction for {len(request.selected_units)} units...",
        "Connecting to Gemini Intelligence for code modernization..."
    ]
    
    for unit in request.selected_units:
        try:
            logs.append(f"Extracting {unit.name} ({unit.type})...")
            result = await project_analysis_service.migrate_logic_unit(
                unit_id=unit.id,
                unit_name=unit.name,
                unit_type=unit.type,
                unit_description=unit.description
            )
            results.append(result)
            logs.append(f"Successfully migrated {unit.name} to {result['filename']}")
        except Exception as e:
            logs.append(f"FAILED to migrate {unit.name}: {str(e)}")
            results.append({"id": unit.id, "status": "error", "error": str(e)})

    return {
        "status": "success",
        "message": f"Successfully processed {len(request.selected_units)} units.",
        "results": results,
        "logs": logs + [
            "All selected units processed.",
            "Files available in 'proper/extracted/' directory."
        ]
    }
