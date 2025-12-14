import subprocess
import time
import requests
import logging
from typing import Optional
from pathlib import Path
from ..schemas.config import RunConfig
from .deploy.generators import DockerComposeGenerator

logger = logging.getLogger(__name__)

class RuntimeManager:
    def __init__(self, config: RunConfig):
        self.config = config
        self.compose_file = "docker-compose.yml"

    def generate_deployment(self, output_path: str = "docker-compose.yml"):
        """
        Translates the agnostic RunConfig into a concrete Docker Compose file.
        """
        self.compose_file = output_path
        generator = DockerComposeGenerator(self.run_config)
        yaml_content = generator.generate()
        
        with open(output_path, "w") as f:
            f.write(yaml_content)
            
        logger.info(f"Deployment generated at {output_path}")

    def start_environment(self):
        """
        Bootstraps the infrastructure using Docker Compose.
        """
        if not Path(self.compose_file).exists():
            raise FileNotFoundError(f"Compose file {self.compose_file} not found. Run generate_deployment() first.")

        logger.info("Starting Docker containers...")
        try:
            # Run docker-compose up -d
            subprocess.run(
                ["docker-compose", "-f", self.compose_file, "up", "-d"], 
                check=True
            )
            logger.info("Containers started successfully.")
            self._wait_for_health()
            
            # Once up, ensure models are loaded
            self.execute_models()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start environment: {e}")
            raise RuntimeError("Docker Compose failed to start.")

    def stop_environment(self):
        """
        Tears down the infrastructure.
        """
        logger.info("Stopping Docker containers...")
        subprocess.run(["docker-compose", "-f", self.compose_file, "down"])

    def execute_models(self):
        """
        Connects to the running engine and loads/pulls the models defined in config.
        """
        provider = self.config.engine.provider
        
        for model in self.config.models:
            logger.info(f"Initializing model: {model.name}...")
            
            if provider == "ollama":
                self._pull_ollama_model(model.name)
            elif provider == "vllm":
                # vLLM loads models at startup via command line, so we just check connectivity
                logger.info(f"vLLM engine should be loading {model.name} automatically.")
            else:
                logger.warning(f"No specific initialization logic for provider: {provider}")

    def _pull_ollama_model(self, model_name: str):
        """
        Ollama starts empty. We must trigger a pull via API.
        """
        # Assuming standard Ollama port if not specified
        base_url = "http://localhost:11434"
        
        logger.info(f"Requesting Ollama to pull '{model_name}' (this may take a while)...")
        try:
            # Trigger the pull
            resp = requests.post(f"{base_url}/api/pull", json={"name": model_name, "stream": False})
            resp.raise_for_status()
            logger.info(f"Successfully pulled {model_name}.")
        except requests.RequestException as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise

    def _wait_for_health(self, timeout: int = 60):
        """
        Simple poll to check if the engine port is listening before proceeding.
        """
        start_time = time.time()
        # Determine port based on provider
        port = 11434 if self.config.engine.provider == "ollama" else 8000
        url = f"http://localhost:{port}"
        
        logger.info(f"Waiting for engine at {url}...")
        
        while time.time() - start_time < timeout:
            try:
                # Just check if we can connect
                requests.get(url, timeout=1)
                logger.info("Engine is responsive.")
                return
            except requests.ConnectionError:
                time.sleep(2)
                continue
        
        raise TimeoutError("Engine failed to become responsive within timeout.")
