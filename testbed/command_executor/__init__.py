"""A :class:`.CommandExecutor` can be used to run commands during
the simulation and is thereful useful in combination with a :class:`.Workflow`.
"""

from .base import CommandExecutor
from .local import LocalCommandExecutor
from .console import ConsoleCommandExecutor
from .docker import DockerCommandExecutor
from .ssh import SSHCommandExecutor
