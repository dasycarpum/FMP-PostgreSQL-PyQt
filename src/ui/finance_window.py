#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-27

@author: Roland VANDE MAELE

@abstract: the finance window contains all the tools for financial analysis of equities.

"""

from PyQt6.QtWidgets import QMainWindow
from src.models.base import Session
import src.ui.finance_window_UI as window


class FinanceWindow(QMainWindow, window.Ui_MainWindow):
    """Finance application window for the PyQt6 application.

    This class represents the finance window of the application, inheriting 
    from QMainWindow and the generated Ui_MainWindow class from Qt Designer.
    It initializes the UI components and sets up the main window.

    """
    def __init__(self, parent=None):
        """
        Initializes a new instance of the FinanceWindow class.

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
        super(FinanceWindow, self).__init__(parent)
        self.setupUi(self)

        self.setup_finance()

    def setup_finance(self) -> None:
        """Set up the initial configuration by initializing attributes"""
        self.db_session = Session()
