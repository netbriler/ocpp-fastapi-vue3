from enum import Enum


class ConnectionStatus(str, Enum):
    NEW_CONNECTION = "new_connection"
    LOST_CONNECTION = "lost_connection"
    DISCONNECT = "disconnect"


class SessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"