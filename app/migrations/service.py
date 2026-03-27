import os
from pathlib import Path
from app.files.service import file_system_service, SOURCE_DIR
from app.core.llm import gemini_provider
from app.core.prompts import PROJECT_ANALYSIS_PROMPT

class ProjectAnalysisService:
    async def analyze_full_project(self):
        """Perform a deep Gitingest-style project mapping using master files and tree structure."""
        project_tree = self._get_project_tree(SOURCE_DIR)
        deep_context = self._get_important_files_content(SOURCE_DIR)
        
        # Construct the 'God-eye view' context string
        ingested_payload = f"FULL PROJECT TREE:\n{project_tree}\n\nCORE CONFIGURATION & ENTRY POINTS:\n"
        for path, content in deep_context.items():
            ingested_payload += f"--- START FILE: {path} ---\n{content}\n--- END FILE: {path} ---\n\n"
            
        analysis = await gemini_provider.analyze_project(project_tree, ingested_payload)
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
        """Surgically select structural 'Master Files' for deep context."""
        master_files = {
            'package.json', 'composer.json', 'requirements.txt', 'setup.py', 'pyproject.toml',
            'index.html', 'index.php', 'index.js', 'main.py', 'app.js', 'app.py',
            'tsconfig.json', 'tailwind.config.js', 'webpack.config.js', 'vite.config.ts',
            'Dockerfile', 'docker-compose.yml', '.env.example'
        }
        contents = {}
        
        # 1. Grab all master files regardless of count (prioritizing architecture)
        for root, _, files in os.walk(directory):
            # Skip noise
            if any(part in root for part in ['node_modules', 'vendor', '.git']):
                continue
                
            for f in files:
                if f in master_files:
                    path = Path(root) / f
                    rel_path = path.relative_to(directory)
                    try:
                        # Full content for master files (up to 10k chars)
                        text = path.read_text(encoding='utf-8')
                        contents[str(rel_path)] = text[:10000]
                    except Exception:
                        continue
        
        # 2. Add samples of core logic files if we have room
        logic_exts = {'.js', '.py', '.php', '.ts', '.tsx'}
        file_count = len(contents)
        if file_count < 25:
            for root, _, files in os.walk(directory):
                if any(part in root for part in ['node_modules', 'vendor', '.git']):
                    continue
                for f in files:
                    if any(f.endswith(ext) for ext in logic_exts) and f not in contents and file_count < 25:
                        path = Path(root) / f
                        rel_path = path.relative_to(directory)
                        try:
                            text = path.read_text(encoding='utf-8')
                            contents[str(rel_path)] = text[:3000]
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
