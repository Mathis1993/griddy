from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ExecutionResult:
    success: bool
    message: str
    result: Optional[Any] = None
