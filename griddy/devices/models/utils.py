from dataclasses import dataclass
from typing import Any, Optional

from execution_conditions.models import ExecutionCondition


@dataclass
class ExecutionResult:
    success: bool
    message: str
    failed_execution_condition: Optional[ExecutionCondition] = None
    result: Optional[Any] = None
