import logging
from collections import deque


class ActionLogHandler(logging.Handler):
    def __init__(self, max_logs: int = 1000):
        super().__init__()
        self.logs = deque(maxlen=max_logs)

    def emit(self, record: logging.LogRecord):
        log_entry = self.format(record)
        self.logs.append(log_entry)

    def get_logs(self) -> list[str]:
        return list(self.logs)


def setup_logging() -> ActionLogHandler:
    action_logger = logging.getLogger("mitmproxy-client")
    action_logger.setLevel(logging.INFO)

    # Prevent logs from propagating to the root logger
    action_logger.propagate = False

    handler = ActionLogHandler()
    formatter = logging.Formatter("%(asctime)s - %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)

    # Clear existing handlers to avoid duplicates
    if action_logger.hasHandlers():
        action_logger.handlers.clear()

    action_logger.addHandler(handler)
    return handler
