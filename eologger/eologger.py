from enum import Enum

class LogLevel(Enum):
    INFO = 1
    ERROR = 2

    def tag(self):
        if self.name == "INFO":
            return "[INFO]"
        if self.name == "ERROR":
            return "[ERROR]"


class EOLogger:
    def __init__(self):
        print("Stating logger!")
    
    def log(self, message, log_level: LogLevel = LogLevel.INFO, source=None):
        print("{0}[{2}]: {1}".format(
            log_level.tag(),
            message,
            source if source is not None else ""
        ))