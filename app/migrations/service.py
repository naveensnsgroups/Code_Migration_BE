import os
from pathlib import Path
from app.files.service import file_system_service, SOURCE_DIR
from app.core.llm import gemini_provider
from app.core.prompts import PROJECT_ANALYSIS_PROMPT

class ProjectAnalysisService:
    async def analyze_full_project(self):
        """Recursively scan all files and perform a project-level AI analysis."""
        project_tree = self._get_project_tree(SOURCE_DIR)
        key_files_content = self._get_important_files_content(SOURCE_DIR)
        
        analysis = await gemini_provider.analyze_project(project_tree, key_files_content)
        return analysis

    def _get_project_tree(self, directory: Path) -> str:
        tree_lines = []
        for root, dirs, files in os.walk(directory):
            # Filter directories in-place
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            rel_path = os.path.relpath(root, directory)
            level = 0 if rel_path == "." else rel_path.count(os.sep) + 1
            indent = '  ' * level
            tree_lines.append(f"{indent}{os.path.basename(root)}/")
            
            sub_indent = '  ' * (level + 1)
            for f in files:
                tree_lines.append(f"{sub_indent}{f}")
        return "\n".join(tree_lines)

    def _get_important_files_content(self, directory: Path) -> dict:
        important_exts = {'.html', '.js', '.py', '.json', '.ts', '.tsx'}
        contents = {}
        
        file_count = 0
        for root, _, files in os.walk(directory):
            for f in files:
                if any(f.endswith(ext) for ext in important_exts) and file_count < 15:
                    path = Path(root) / f
                    rel_path = path.relative_to(directory)
                    try:
                        text = path.read_text(encoding='utf-8')
                        contents[str(rel_path)] = text[:3000] # Increased limit
                        file_count += 1
                    except Exception:
                        continue
        return contents

    async def migrate_logic_unit(self, unit_id: str, unit_name: str, unit_type: str, unit_description: str):
        """Perform the actual surgical extraction of a logic unit."""
        # For simulation/demo, we use the key_files_content as context
        context = self._get_important_files_content(SOURCE_DIR)
        context_str = "\n\n".join([f"FILE: {k}\n{v}" for k, v in context.items()])
        
        extraction = await gemini_provider.extract_logic_unit(
            unit_name=unit_name,
            unit_type=unit_type,
            unit_description=unit_description,
            context=context_str
        )
        
        # Save to 'proper' workspace
        proper_dir = SOURCE_DIR.parent / "proper"
        extracted_dir = proper_dir / "extracted"
        extracted_dir.mkdir(parents=True, exist_ok=True)
        
        filename = extraction.get("filename", f"extracted_{unit_id}.js")
        file_path = extracted_dir / filename
        
        # In a real scenario, we'd be more careful with paths
        # For now, we write the modernization result
        file_path.write_text(extraction.get("content", ""), encoding='utf-8')
        
        return {
            "id": unit_id,
            "filename": filename,
            "status": "migrated",
            "path": str(file_path.relative_to(SOURCE_DIR.parent)),
            "explanation": extraction.get("explanation", "")
        }

project_analysis_service = ProjectAnalysisService()
