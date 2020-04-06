"""Visualisation offers multiple visualisations and
has an interface for user defined visualisations.
"""
from .visualisation import Visualisation, NoVisualisation
# Do not import NetAnimVisualisation here, since otherwise it would load the dependencies
