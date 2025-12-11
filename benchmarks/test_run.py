import time
import random
from typing import Dict, Any, List
from .base import BaseBenchmark

class TestRunBenchmark(BaseBenchmark):
    """
    A dummy benchmark to test system plumbing (API -> Runner -> CSV).
    Does not require Ollama, vLLM, or GPU.
    """
    
    def load_data(self) -> List[Any]:
        # Return 3 dummy items so the test is quick
        return [
            {"input": f"mock_input_{i}", "ground_truth": f"mock_output_{i}"} 
            for i in range(3)
        ]

    def run_inference(self, input_item: Any) -> Any:
        # Simulate a small delay (like a network call)
        time.sleep(0.05) 
        # Return a fake "prediction"
        return f"processed_{input_item}"

    def calculate_metrics(self, prediction: Any, ground_truth: Any) -> Dict[str, float]:
        # Return fake metrics to verify JSON serialization works
        return {
            "mock_accuracy": 1.0,
            "random_score": round(random.uniform(0.5, 0.9), 2)
        }