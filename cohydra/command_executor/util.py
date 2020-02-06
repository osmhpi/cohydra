"""Internal utility functions."""
import shlex
from datetime import datetime

def stringify_shell_arguments(command):
    if isinstance(command, str):
        return command

    return ' '.join(map(shlex.quote, command))

def split_shell_arguments(command):
    return shlex.split(command)

class LogFile:
    """The logfile helps by prepending timestamps to log lines."""

    def __init__(self, logger, path):
        self.logger = logger
        self.path = path
        self.file = None

    def log(self, level, line):
        self.logger.log(level, '%s', line)
        if self.file is not None:
            now = datetime.now().isoformat()
            self.file.write(f'{now} {line}\n')

    def __enter__(self):
        if self.path is not None:
            self.file = open(self.path, 'a')
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.file is not None:
            self.file.__exit__(exc_type, exc_value, exc_traceback)
            self.file = None
