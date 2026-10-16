from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import time

class AgentExecutionContext(BaseModel):
    user_id: str
    run_id: str
    start_time: float
    state: Dict[str, Any] = {}

class AgentExecutionResult(BaseModel):
    agent_name: str
    success: bool
    execution_time_ms: float
    output: Dict[str, Any]
    warnings: list[str] = []
    error_message: Optional[str] = None

class BaseProofGraphAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        """Execute the agent's core task using the shared execution context."""
        pass

    def record_success(self, start_time: float, output: BaseModel, warnings: list[str] = None) -> AgentExecutionResult:
        elapsed = (time.time() - start_time) * 1000.0
        return AgentExecutionResult(
            agent_name=self.name,
            success=True,
            execution_time_ms=round(elapsed, 2),
            output=output.model_dump(),
            warnings=warnings or []
        )

    def record_failure(self, start_time: float, error: str) -> AgentExecutionResult:
        elapsed = (time.time() - start_time) * 1000.0
        return AgentExecutionResult(
            agent_name=self.name,
            success=False,
            execution_time_ms=round(elapsed, 2),
            output={},
            error_message=error
        )
