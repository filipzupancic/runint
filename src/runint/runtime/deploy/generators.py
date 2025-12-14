import yaml
from typing import Dict, Any
from ...schemas.config import RunConfig
from ..engines.ollama import OllamaEngine
from ..engines.vllm import VLLMEngine

class DockerComposeGenerator:
    def __init__(self, run_config: RunConfig):
        self.run_config = run_config

    def generate(self) -> str:
        """
        Generates the full docker-compose.yml content as a string.
        """
        provider = self.run_config.engine.provider
        engine_conf = self.run_config.engine.model_dump() # Convert Pydantic to dict

        # 1. Select Engine
        service_def = {}
        if provider == "ollama":
            engine = OllamaEngine(engine_conf)
            service_def = engine.get_docker_service_config()
            service_name = "ollama"
        elif provider == "vllm":
            engine = VLLMEngine(engine_conf)
            service_def = engine.get_docker_service_config()
            service_name = "vllm"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # 2. Build Compose Structure
        compose_dict = {
            "version": "3.8",
            "services": {
                service_name: service_def
            },
            "volumes": {}
        }

        # Add named volumes if needed
        if "volumes" in service_def:
            for vol in service_def["volumes"]:
                vol_name = vol.split(":")[0]
                # Only add if it's a named volume (not a path)
                if "/" not in vol_name and "~" not in vol_name:
                    compose_dict["volumes"][vol_name] = {}

        # 3. Dump to YAML
        return yaml.dump(compose_dict, sort_keys=False, default_flow_style=False)
        