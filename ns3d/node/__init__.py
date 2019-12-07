import logging

from .base import Node
from .switch import SwitchNode
from .docker import DockerNode
from .external import ExternalNode
from .ssh import SSHNode

class BridgeNode(SwitchNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.getLogger(__name__).warning('The BridgeNode has been renamed to SwitchNode')
