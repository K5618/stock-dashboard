# src/providers/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseDataProvider(ABC):
    @abstractmethod
    def fetch_data(self, **kwargs) -> Any:
        """
        Fetch data from the provider.
        Must be implemented by subclasses.
        """
        pass
