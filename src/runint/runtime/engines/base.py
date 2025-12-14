from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseEngine(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def get_docker_service_config(self) -> Dict[str, Any]:
        """
        Returns a dictionary representing a service in docker-compose.yml
        """
        pass