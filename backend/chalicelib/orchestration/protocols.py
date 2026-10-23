from typing import Protocol, Any
from chalicelib.orchestration.logging import EventLogger

class EventHandler(Protocol):
    def __call__(self, event_logger: EventLogger) -> Any:
        ...
