#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-11

@author: Roland VANDE MAELE

@abstract: the MplWidget class inherits directly from QWidget and can be used 
to draw a Matplotlib figure.

@source: Matplotlib for Python Developers, Sandro TOSI - Packt Publishing

"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib

# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')

class MplCanvas(FigureCanvasQTAgg):
    """A class to represent the canvas on which the Matplotlib figure is drawn.

    This class creates a Matplotlib figure and initializes the canvas with this 
    figure. It inherits from FigureCanvasQTAgg to integrate with the PyQt 
    framework, allowing the Matplotlib figure to be embedded within a PyQt widget.

    Attributes:
        fig (Figure): A Matplotlib Figure object where the plot is drawn.
        ax (Axes): A Matplotlib Axes object for the figure, used for plotting.

    """
    def __init__(self):
        """Initializes the canvas with a Matplotlib figure.

        Sets up the Matplotlib Figure and Axes, and initializes the canvas with 
        this figure by calling the parent class constructor with the figure.

        """
        # Setup Matplotlib Figure and Axes
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        # Initialize the canvas with the figure
        super().__init__(self.fig)

class MplWidget(QWidget):
    """A widget for integrating a Matplotlib figure into a PyQt window.

    This class encapsulates a Matplotlib canvas (MplCanvas) within a QWidget to 
    allow Matplotlib figures to be displayed inside a PyQt application. It uses 
    a QVBoxLayout to manage the layout of the canvas within the widget.

    Attributes:
        canvas (MplCanvas): An instance of MplCanvas, which is the canvas where 
        the Matplotlib figure is drawn.
        vBoxLayout (QVBoxLayout): A layout manager to arrange the canvas within 
        the widget.
    """
    def __init__(self, parent=None):
        """Initializes the MplWidget with a Matplotlib canvas and a QVBoxLayout.

        Creates an MplCanvas instance and sets up a QVBoxLayout to hold the 
        canvas. The canvas is then added to the layout, and the layout is 
        applied to the widget.

        Args:
            parent (QWidget, optional): The parent widget to which this 
            MplWidget belongs. Defaults to None.

        """
        super().__init__(parent)  # Initialize the base class (QWidget)

        # Instantiate an MplCanvas object
        self.canvas = MplCanvas()

        # Setup the layout and add the canvas to it
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.canvas)

        # Set the layout to the QWidget
        self.setLayout(self.vBoxLayout)
