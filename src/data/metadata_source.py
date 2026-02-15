from typing import Dict, Any

class MetadataSource:

    def load(self) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError
