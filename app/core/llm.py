import google.generativeai as genai
import json
from app.core.config import settings
from app.core.prompts import MIGRATION_ANALYSIS_PROMPT, PROJECT_ANALYSIS_PROMPT, MIGRATION_EXTRACTION_PROMPT

class GeminiProvider:
    def __init__(self):
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_key_here":
            print("WARNING: Gemini API Key not set correctly.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash') # High context, better JSON

    def _clean_json_response(self, text: str):
        """Robustly extract JSON from AI response, handling markdown blocks and junk text."""
        if not text:
            return None
        
        text = text.strip()
        
        # 1. Try to find JSON inside markdown blocks
        import re
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        else:
            # 2. Try to find the first { and last } if no markdown blocks
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                text = text[start:end+1]

        try:
            return json.loads(text)
        except Exception as e:
            print(f"FAILED TO PARSE LLM RESPONSE: {str(e)}")
            safe_text = str(text)
            print(f"RAW TEXT START: {safe_text[:200]}...")
            print(f"RAW TEXT END: {safe_text[-200:]}...")
            return None

    async def analyze_code(self, code: str, filename: str):
        """Perform real-time code analysis using Gemini."""
        prompt = MIGRATION_ANALYSIS_PROMPT.format(filename=filename, code=code)
        try:
            response = self.model.generate_content(prompt)
            data = self._clean_json_response(response.text)
            return data or {"category": "error", "logic_units": []}
        except Exception as e:
            return {"category": "error", "logic_units": [], "error": str(e)}

    async def analyze_project(self, tree: str, ingested_payload: str):
        """Analyze full project structure and stack using the Gitingest payload."""
        prompt = PROJECT_ANALYSIS_PROMPT.format(tree=tree, samples=ingested_payload)
        try:
            response = self.model.generate_content(prompt)
            data = self._clean_json_response(response.text)
            return data or {
                "purpose": "General project analysis",
                "architecture": "Undefined architecture",
                "mapped_structure": "Structure mapping failed",
                "stack": {"frontend": "Unknown", "backend": "Unknown"},
                "logic_units": []
            }
        except Exception as e:
            return {"error": str(e), "logic_units": []}

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
            data = self._clean_json_response(response.text)
            return data or {
                "filename": "ext_error.js",
                "content": f"// Extraction failed: AI response was not valid JSON",
                "explanation": "Extraction failed due to parsing error."
            }
        except Exception as e:
            return {"error": str(e), "content": "// Extraction failed"}

gemini_provider = GeminiProvider()
