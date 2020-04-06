"""Visualisations to display simulation results."""

from abc import ABC, abstractmethod

class Visualisation(ABC):
    """The Visualisation class is the abstract super class of all visualisations.

    To set a new visualisation or to get the current visualisation object use:

    .. code-block:: python

        from cohydra.visualisation import Visualisation, NoVisualisation
        Visualisation.set_visualisation(NoVisualisation())
        Visualisation.get_visualisation().set_node_size(5.0)
    """

    __current_visualisation = None

    @staticmethod
    def get_visualisation():
        """Return the current visualisation. Default is no visualisation"""
        if Visualisation.__current_visualisation is None:
            Visualisation.set_visualisation(NoVisualisation())
        return Visualisation.__current_visualisation

    @staticmethod
    def set_visualisation(visualisation):
        """Sets a new visualisation.

        Parameters
        ----------
        node : :class:`.Visualisation`
            The new visualisation object.
        """
        Visualisation.__current_visualisation = visualisation

    def __init__(self):
        #: The size of each node in the visualisation
        self.node_size = 4
        #: The output directory
        self.output_directory = None

    def set_node_size(self, new_node_size: float):
        """Sets a new node size

        Parameters
        ----------
        new_node_size : float
            The new node size.
        """
        self.node_size = new_node_size

    def set_output_directory(self, new_output_directory: str):
        """Sets a new output directory

        Parameters
        ----------
        new_output_directory : str
            The new output directory
        """
        self.output_directory = new_output_directory

    @abstractmethod
    def prepare_node(self, node):
        """Gives the visualisation the oppertunity to prepare a node

        Parameters
        ----------
        node : :class:`.Node`
            The related node.
        """
        pass

    @abstractmethod
    def set_node_position(self, node, x, y, z=0):
        """Set the position of the node in the visualisation.

        Parameters
        ----------
        node : :class:`.Node`
            The related node.
        x : float
            The x-position.
        y : float
            The y-position.
        z : float
            The z-position.
        """
        pass


class NoVisualisation(Visualisation):
    """The NoContext is a Null-Object and therefore **does nothing**.

    There is no visualisation at all and all calls to the visualisation class
    will be ignored.
    """

    def prepare_node(self, node):
        pass

    def set_node_position(self, node, x, y, z=0):
        pass
