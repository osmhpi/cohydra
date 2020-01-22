import logging

logger = logging.getLogger(__name__)

class CommandExecutor:
    """! The CommandExecutor abstracts away the code for running
        code on a Node.
    """

    def __init__(self, name='unnamed'):
        """! Create a new command executor.

        @param You can specify a name for logging purposes."""
        ## The name of the CommandExecutor.
        self.name = name
        ## A counter for loggers.
        self.counter = 0

    def get_logger(self):
        """! Retrieve the logger for this command executor."""
        num = self.counter
        self.counter += 1
        return logging.getLogger(self.name).getChild(str(num))

    def execute(self, command, user=None, shell=None, stdout_logfile=None, stderr_logfile=None):
        """! Execute a command.

        @param command The command to run.
        @param user The user to run the command as.
        @param shell The type of shell to use (`sh`, `bash`, ...).
        @param stdout_logfile The path to the log file to append the stdout output.
        @param stderr_logfile The path to the log file to append the stderr output.
        """
        raise NotImplementedError

class ExitCode(Exception):
    """! An ExitCode is a container for storing a commands exit code."""

    def __init__(self, code: int, command: str):
        """! Create a new ExitCode.
        
        @param code The exit code.
        @param command The command that was executed.
        """
        super().__init__(code)
        self.code = code
        self.command = command
