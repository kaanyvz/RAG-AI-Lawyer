from datetime import date, datetime
from json import JSONEncoder
from pathlib import Path
from typing import Any


class CustomJsonEncoder(JSONEncoder):
    def default(self, obj: Any) -> str:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)
