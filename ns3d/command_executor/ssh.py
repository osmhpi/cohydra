import logging
import threading
from paramiko import SSHClient

from . import util
from .base import CommandExecutor

def log_file(logger, level, file, logfile):
    with file, util.LogFile(logger, logfile) as log:
        for line in file:
            log.log(level, line)

class SSHCommandExecutor(CommandExecutor):

    def __init__(self, name, client: SSHClient, sudo=False):
        super().__init__(name)
        self.client = client
        self.sudo = sudo
        self.counter = 0

    def execute(self, command, user=None, shell=None, stdout_logfile=None, stderr_logfile=None):
        command = util.stringify_shell_arguments(command)
        if user is None:
            if shell is not None:
                command = [shell, '-c', command]
        else:
            if self.sudo:
                command_end = util.split_shell_arguments(command)
                command = ['sudo', '-u', user]
            else:
                command_end = ['-c', command]
                command = ['su', user]
            if shell is not None:
                command.extend(['-s', shell])
            command.extend(command_end)

        command = util.stringify_shell_arguments(command)
        logger = self.get_logger()
        logger.debug('%s', command)
        (stdin, stdout, stderr) = self.client.exec_command(command)

        stdin.close()

        out_thread = threading.Thread(target=log_file, args=(logger, logging.INFO, stdout, stdout_logfile))
        err_thread = threading.Thread(target=log_file, args=(logger, logging.ERROR, stderr, stderr_logfile))

        out_thread.start()
        err_thread.start()

        out_thread.join()
        err_thread.join()
