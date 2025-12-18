
from typing import Protocol

from agentic.controller import ControllerRequest, ControllerResponse


class ControllerProtocol(Protocol):
    def __call__(self, request: ControllerRequest) -> ControllerResponse:
        ...
