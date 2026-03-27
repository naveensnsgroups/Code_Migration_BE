import google.generativeai as genai
import json
from app.core.config import settings
from app.core.prompts import MIGRATION_ANALYSIS_PROMPT, PROJECT_ANALYSIS_PROMPT, MIGRATION_EXTRACTION_PROMPT

class GeminiProvider:
    def __init__(self):
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_key_here":
            print("WARNING: Gemini API Key not set correctly.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash') # Using flash for speed

    async def analyze_code(self, code: str, filename: str):
        """Perform real-time code analysis using Gemini."""
        prompt = MIGRATION_ANALYSIS_PROMPT.format(filename=filename, code=code)
        
        try:
            response = self.model.generate_content(prompt)
            # Remove markdown backticks if present
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"Gemini Analysis Error: {str(e)}")
            return {
                "category": "error",
                "logic_units": [],
                "error": str(e)
            }

    async def analyze_project(self, tree: str, samples: dict):
        """Analyze full project structure and stack."""
        formatted_samples = "\n\n".join([f"FILE: {path}\n{content}" for path, content in samples.items()])
        prompt = PROJECT_ANALYSIS_PROMPT.format(tree=tree, samples=formatted_samples)
        
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"Gemini Project Analysis Error: {str(e)}")
            return {
                "stack": {"frontend": "unknown", "backend": "unknown"},
                "logic_units": [],
                "error": str(e)
            }

    async def extract_logic_unit(self, unit_name: str, unit_type: str, unit_description: str, context: str):
        """Extract and modernize a specific logic unit."""
        prompt = MIGRATION_EXTRACTION_PROMPT.format(
            unit_name=unit_name,
            unit_type=unit_type,
            unit_description=unit_description,
            context=context
        )
        
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"Gemini Extraction Error: {str(e)}")
            return {
                "filename": "ext_error.js",
                "content": f"// Extraction failed: {str(e)}",
                "explanation": f"Failed to extract {unit_name} due to AI error."
            }

gemini_provider = GeminiProvider()
