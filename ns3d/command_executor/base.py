import logging

logger = logging.getLogger(__name__)

class CommandExecutor:

    def __init__(self, name='unnamed'):
        self.name = name
        self.counter = 0

    def get_logger(self):
        num = self.counter
        self.counter += 1
        return logging.getLogger(self.name).getChild(str(num))

    def execute(self, command, user=None, shell=None, stdout_logfile=None, stderr_logfile=None):
        raise NotImplementedError

class ExitCode(Exception):

    def __init__(self, code: int, command: str):
        super().__init__(code)
        self.code = code
        self.command = command
