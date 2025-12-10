# database/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BenchmarkResult(Base):
    __tablename__ = "benchmark_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)  # UUID for grouping
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Context
    model_name = Column(String)
    engine = Column(String)
    task_type = Column(String)
    dataset_name = Column(String)
    
    # Performance
    latency_ms = Column(Float)
    error_occurred = Column(Boolean, default=False)
    
    # Flexible Data
    parameters = Column(JSONB)  # Store inputs like temp, top_k
    metrics = Column(JSONB)     # Store output scores like BLEU, Confidence
    raw_output = Column(Text)   # Debugging data
