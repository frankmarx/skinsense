from typing import Protocol, Any
from chalicelib.orchestration.logging import JobDetailLogger

class JobHandler(Protocol):
    def __call__(self, app: Any, job_id: str, logger: JobDetailLogger) -> Any:
        ...
