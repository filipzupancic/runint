# api/routes.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Import your benchmark classes
from benchmarks.nlp.translation import TranslationBenchmark

router = APIRouter()

class BenchmarkRequest(BaseModel):
    task_type: str       # "translation", "ocr"
    model_name: str      # "llama3", "mistral"
    engine: str          # "ollama", "vllm"
    dataset_name: str    # "standard_test_v1"
    config: Optional[Dict[str, Any]] = {}

def run_benchmark_task(request: BenchmarkRequest):
    """Background task wrapper"""
    # 1. Select the correct class based on task_type
    if request.task_type == "translation":
        # In a real app, inject URL from settings
        request.config["api_url"] = "http://ollama:11434" 
        
        benchmark = TranslationBenchmark(
            model_name=request.model_name,
            engine=request.engine,
            task_type=request.task_type,
            dataset_name=request.dataset_name,
            config=request.config
        )
        benchmark.execute()
    else:
        print(f"Task {request.task_type} not implemented yet")

@router.post("/run")
async def trigger_benchmark(request: BenchmarkRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to start a benchmark run asynchronously.
    """
    valid_tasks = ["translation"]
    if request.task_type not in valid_tasks:
        raise HTTPException(status_code=400, detail="Invalid task type")

    # Run in background so API doesn't hang
    background_tasks.add_task(run_benchmark_task, request)
    
    return {"status": "accepted", "message": f"Benchmark for {request.model_name} started."}
