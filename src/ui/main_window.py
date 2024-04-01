#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-01

@author: Roland VANDE MAELE

@abstract: the main window contains all the application's interface functions.

"""

from PyQt6.QtWidgets import QMainWindow
import src.ui.main_window_UI as window

class MainWindow(QMainWindow, window.Ui_MainWindow):
    """Main application window for the PyQt6 application.

    This class represents the main window of the application, inheriting from
    QMainWindow and the generated Ui_MainWindow class from Qt Designer.
    It initializes the UI components and sets up the main window.

    """
    def __init__(self, parent=None):
        """
        Initializes a new instance of the MainWindow class.

        This constructor sets up the main application window by initializing
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
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
