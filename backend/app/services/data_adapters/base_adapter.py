from typing import Optional, Dict, Any
from datetime import datetime


class BaseDataAdapter:
    """Base class for data adapters"""
    
    def __init__(self, mode: str = "demo"):
        self.mode = mode
    
    def _get_metadata(self, source: str, **extra) -> Dict[str, str]:
        """Generate metadata for response"""
        metadata = {
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        metadata.update(extra)
        return metadata
