# benchmarks/nlp/translation.py
import requests
import json
from ..base import BaseBenchmark
# Optional: import specific metric libraries
# from sacrebleu.metrics import BLEU 

class TranslationBenchmark(BaseBenchmark):
    def load_data(self):
        """
        Example: Loads a JSON file with source text and target translations.
        Real implementation might load from data/prepared/wmt14_en_de.json
        """
        # Mock data for demonstration
        return [
            {"input": "Hello world", "ground_truth": "Hallo Welt"},
            {"input": "The cat sits on the mat", "ground_truth": "Die Katze sitzt auf der Matte"}
        ]

    def run_inference(self, input_text: str) -> str:
        """
        Calls Ollama or vLLM based on self.engine
        """
        prompt = f"Translate the following text to German. Output only the translation.\n\nText: {input_text}"

        if self.engine == "ollama":
            # API call to Ollama container
            url = f"{self.config.get('api_url')}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.get("temperature", 0)
                }
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()

        elif self.engine == "vllm":
            # API call to vLLM container (OpenAI compatible endpoint usually)
            url = f"{self.config.get('api_url')}/v1/completions"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": 100,
                "temperature": self.config.get("temperature", 0)
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['text'].strip()
        
        else:
            raise ValueError(f"Unsupported engine: {self.engine}")

    def calculate_metrics(self, prediction: str, ground_truth: str) -> Dict[str, float]:
        """
        Simple string matching for now, but ready for BLEU/ROUGE.
        """
        # Simple exact match for demo
        exact_match = 1.0 if prediction.lower() == ground_truth.lower() else 0.0
        
        # Length ratio (simple proxy for quality sometimes)
        len_ratio = len(prediction) / len(ground_truth) if len(ground_truth) > 0 else 0
        
        return {
            "exact_match": exact_match,
            "length_ratio": round(len_ratio, 2)
        }