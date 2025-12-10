# benchmarks/base.py
import time
import json
import csv
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Assuming you'll set up a database session factory later
# from database.connection import get_db_session 
# from database.models import BenchmarkResult

logger = logging.getLogger(__name__)

class BaseBenchmark(ABC):
    def __init__(self, 
                 model_name: str, 
                 engine: str, 
                 task_type: str, 
                 dataset_name: str, 
                 config: Dict[str, Any] = None):
        """
        :param model_name: Name of the model (e.g., 'llama3', 'yolov8')
        :param engine: Runtime engine (e.g., 'ollama', 'vllm', 'local_cv2')
        :param task_type: Broad category (e.g., 'translation', 'ocr')
        :param dataset_name: Identifier for the dataset being used
        :param config: Dictionary containing parameters (temp, top_k, confidence, etc.)
        """
        self.run_id = str(uuid.uuid4())
        self.model_name = model_name
        self.engine = engine
        self.task_type = task_type
        self.dataset_name = dataset_name
        self.config = config or {}
        
        # Paths - normally loaded from settings
        self.results_dir = os.getenv("RESULTS_DIR", "./results")
        os.makedirs(f"{self.results_dir}/csv", exist_ok=True)

    @abstractmethod
    def load_data(self) -> List[Any]:
        """Loads inputs (text prompts, image paths) from the dataset."""
        pass

    @abstractmethod
    def run_inference(self, input_item: Any) -> Any:
        """
        Executes the actual model call. 
        Returns the raw output from the model.
        """
        pass

    @abstractmethod
    def calculate_metrics(self, prediction: Any, ground_truth: Any) -> Dict[str, float]:
        """
        Compares prediction vs ground truth.
        Returns dict like {'accuracy': 0.95, 'bleu': 24.5}
        """
        pass

    def execute(self):
        """
        The main orchestration method.
        Iterates over data, times execution, saves results.
        """
        data_items = self.load_data()
        results = []

        logger.info(f"Starting benchmark: {self.task_type} with {self.model_name} on {self.engine}")

        for i, item in enumerate(data_items):
            input_data = item['input']
            ground_truth = item.get('ground_truth')

            # 1. Measurement
            start_time = time.perf_counter()
            try:
                prediction = self.run_inference(input_data)
                error = False
            except Exception as e:
                logger.error(f"Inference failed for item {i}: {e}")
                prediction = str(e)
                error = True
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000

            # 2. Evaluation
            metrics = {}
            if not error and ground_truth:
                metrics = self.calculate_metrics(prediction, ground_truth)

            # 3. Structure the Record
            record = {
                "run_id": self.run_id,
                "timestamp": datetime.utcnow().isoformat(),
                "model_name": self.model_name,
                "engine": self.engine,
                "task_type": self.task_type,
                "dataset_name": self.dataset_name,
                "latency_ms": round(latency_ms, 2),
                "error_occurred": error,
                "parameters": json.dumps(self.config),
                "metrics": json.dumps(metrics),
                "raw_output": str(prediction)[:1000] # Truncate if too huge
            }
            
            results.append(record)

        # 4. Save Results
        self._save_to_csv(results)
        self._save_to_db(results)
        
        return results

    def _save_to_csv(self, results: List[Dict]):
        filename = f"{self.results_dir}/csv/{self.task_type}_{self.engine}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Check if file exists to decide whether to write headers
        file_exists = os.path.isfile(filename)
        
        if not results:
            return

        keys = results[0].keys()
        
        with open(filename, 'a', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            if not file_exists:
                dict_writer.writeheader()
            dict_writer.writerows(results)
        
        logger.info(f"Saved {len(results)} rows to {filename}")

    def _save_to_db(self, results: List[Dict]):
        # Placeholder for DB Logic
        # session = get_db_session()
        # for res in results:
        #     session.add(BenchmarkResult(**res))
        # session.commit()
        logger.info("Database save logic would run here.")
