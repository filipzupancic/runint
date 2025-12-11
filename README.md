# RUNINT Benchmarks

A modular benchmarking harness designed to evaluate various AI models (LLMs, Vision) across different runtimes (Ollama, vLLM, etc.).

## 🚀 Quick Start

### Prerequisites
* Docker & Docker Compose
* (Optional) NVIDIA GPU drivers if running vLLM

### 1. Setup Infrastructure
Start the API, Database, and Ollama containers:
```bash
docker-compose up -d --build
```

### 2. Download a Model
Since Ollama starts empty, you need to pull a model (one-time setup):

```bash
docker exec -it runint_ollama ollama pull llama3
```

### 3. Run a Benchmark
Trigger a translation benchmark via the API:
```bash
curl -X POST "http://localhost:8000/run" \
     -H "Content-Type: application/json" \
     -d '{
           "task_type": "translation",
           "model_name": "llama3",
           "engine": "ollama",
           "dataset_name": "quick_check_v1",
           "config": {"temperature": 0.1}
         }'
```

## 📂 Project Structure

- **api/** : FastAPI application handling requests and background tasks.

- **benchmarks/** : Core logic.

    - **base.py** : The abstract base class all benchmarks must inherit from.

    - **nlp/** : Tasks like Translation, Summarization.

    - **vision/** : Tasks like OCR, Face Detection.

- **results/** :

    - **csv/** : Auto-generated CSV reports for quick analysis.

- **docker/** : Dockerfiles and configuration scripts.

## 📊 Data Storage
Results are stored in two places for redundancy and flexibility:

1. **PostgreSQL**: For structured queries and long-term history.

    - **Table**: benchmark_runs

    - **Flexible columns**: metrics (JSONB) and parameters (JSONB) allow storing task-specific data without schema migrations.

2. **CSV**: Located in results/csv/. Useful for quick verification or Excel analysis.

## 🛠 Adding a New Benchmark

1. Create a new file in benchmarks/<category>/<task>.py.

2. Inherit from BaseBenchmark.

3. Implement the required methods:

    - load_data()

    - run_inference()

    - calculate_metrics()

4. Register the new task type in api/routes.py.

## 🧪 Development
To run tests:

```bash
docker-compose run runint-api pytest
```

To format code:
```bash
docker-compose run runint-api black .
```
