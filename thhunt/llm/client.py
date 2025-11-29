import requests
import json
from typing import Dict, Any, Optional
from ..config.loader import LLMConfig
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url
        self.model = config.model

    def generate(self, prompt: str) -> Optional[str]:
        """
        Generates text using the local LLM API.
        Assumes Ollama/OpenAI-like format.
        """
        try:
            # Example for Ollama /api/generate
            if "ollama" in self.config.provider:
                url = f"{self.base_url}/api/generate"
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
                response = requests.post(url, json=payload, timeout=self.config.timeout)
                response.raise_for_status()
                return response.json().get("response")
            
            # Example for OpenAI-compatible (LM Studio, etc.)
            else:
                url = f"{self.base_url}/v1/chat/completions"
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                response = requests.post(url, json=payload, timeout=self.config.timeout)
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None

    def enrich_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates enrichment data for an alert.
        """
        prompt = self._construct_prompt(alert)
        response_text = self.generate(prompt)
        
        if not response_text:
            return {}

        # Parse the response (assuming LLM returns structured text or JSON)
        # For now, we just return the raw text as summary
        return {
            "summary": response_text,
            "severity_score": 5, # Placeholder
            "threat_category": "Unknown", # Placeholder
            "recommendations": "Review logs." # Placeholder
        }

    def _construct_prompt(self, alert: Dict[str, Any]) -> str:
        return f"""
        You are a security analyst. Analyze the following alert and provide a summary, severity score (1-10), threat category, and recommendations.
        
        Alert: {json.dumps(alert, indent=2)}
        
        Output format:
        Summary: ...
        Severity: ...
        Category: ...
        Recommendations: ...
        """
