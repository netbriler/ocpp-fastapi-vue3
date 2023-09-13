from enum import Enum


class ConnectionStatus(str, Enum):
    NEW_CONNECTION = "new_connection"
    LOST_CONNECTION = "lost_connection"
    DISCONNECT = "disconnect"