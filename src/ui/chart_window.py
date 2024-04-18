#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-18

@author: Roland VANDE MAELE

@abstract: the chart window contains all the tools for technical analysis of equities.

"""

from PyQt6.QtWidgets import QMainWindow
import src.ui.chart_window_UI as window

class ChartWindow(QMainWindow, window.Ui_MainWindow):
    """Chart application window for the PyQt6 application.

    This class represents the chart window of the application, inheriting from
    QMainWindow and the generated Ui_MainWindow class from Qt Designer.
    It initializes the UI components and sets up the main window.

    """
    def __init__(self, parent=None):
        """
        Initializes a new instance of the ChartWindow class.

        This constructor sets up the chart application window by initializing
        the user interface components inherited from QMainWindow and 
        Ui_MainWindow. 

        Args:
            parent (QWidget, optional): The parent widget of this main window. 
            If provided, sets the main window's parent to the specified widget, 
            thereby establishing a parent-child relationship in the Qt widget 
            hierarchy. Defaults to None, which means the main window will have 
            no parent.
        
        Returns:
            None

        Note:
            - The `setupUi` method is called to set up the UI components 
            defined in the Ui_MainWindow class.

        """
        super(ChartWindow, self).__init__(parent)
        self.setupUi(self)
