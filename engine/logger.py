import sys
from enum import Enum, auto

class LogType(Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

# ANSI color codes for Windows and Unix
LOG_COLORS = {
    LogType.DEBUG: '\033[36m',    # Cyan
    LogType.INFO: '\033[32m',     # Green
    LogType.WARNING: '\033[33m',  # Yellow
    LogType.ERROR: '\033[31m',    # Red
}
LOG_SYMBOLS = {
    LogType.DEBUG: '🐞',
    LogType.INFO: 'ℹ️',
    LogType.WARNING: '⚠️',
    LogType.ERROR: '❌',
}
RESET_COLOR = '\033[0m'

class Logger:
    _enabled_types = {LogType.INFO, LogType.ERROR, LogType.WARNING}

    @classmethod
    def enable(cls, log_type):
        cls._enabled_types.add(log_type)

    @classmethod
    def disable(cls, log_type):
        cls._enabled_types.discard(log_type)

    @classmethod
    def log(cls, message, log_type=LogType.INFO):
        if log_type not in cls._enabled_types:
            return
        prefix = {
            LogType.DEBUG: '[DEBUG]',
            LogType.INFO: '[INFO]',
            LogType.WARNING: '[WARN]',
            LogType.ERROR: '[ERROR]'
        }[log_type]
        color = LOG_COLORS.get(log_type, '')
        symbol = LOG_SYMBOLS.get(log_type, '')
        reset = RESET_COLOR if color else ''
        output = f'{color}{symbol} {prefix} {message}{reset}'
        print(output, file=sys.stderr if log_type == LogType.ERROR else sys.stdout)

    @classmethod
    def debug(cls, message):
        cls.log(message, LogType.DEBUG)

    @classmethod
    def info(cls, message):
        cls.log(message, LogType.INFO)

    @classmethod
    def warning(cls, message):
        cls.log(message, LogType.WARNING)

    @classmethod
    def error(cls, message):
        cls.log(message, LogType.ERROR)
