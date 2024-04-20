#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-18

@author: Roland VANDE MAELE

@abstract: the chart window contains all the tools for technical analysis of equities.

"""

from PyQt6.QtWidgets import QMainWindow
from src.models.base import Session
import src.ui.chart_window_UI as window
from src.business_logic.fmp.database_reporting import StockReporting

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

        self.db_session = Session()
        self.stock_reporting = StockReporting(self.db_session)
        self.stock_dict = self.stock_reporting.get_stock_dictionary()
        self.setting = {}

        self.setup_signal_connections()

    def setup_signal_connections(self):
        """Set up the signal connections for the UI elements."""
        self.lineEdit_search.textChanged.connect(self.on_text_changed)
        self.pushButton_setting.clicked.connect(self.handle_setting_validation)

    def on_text_changed(self, text):
        """
        Handles text changes in a QLineEdit widget by searching for matching 
        stock details in the stock dictionary and updating UI components with 
        the matched stock's details.

        This method performs a case-insensitive search through the stock 
        dictionary to find the first stock where any of the stock details 
        (name, symbol, or ISIN) starts with the input text. If a match is 
        found, the corresponding asset details are used to update the values of 
        multiple QLabel widgets. If no match is found, the method resets these 
        widgets to their default state.

        Args:
            text (str): The current text from the QLineEdit widget where the 
            text change occurred.

        """
        # Convert the input text to lower case for case-insensitive comparison
        text_lower = text.lower()

        # Find the first matching key where any word in the list matches the input text
        matched_key = None
        for key, value_list in self.stock_dict.items():
            # Check if any word in the list starts with the input text (case-insensitive)
            if any(word.lower().startswith(text_lower) for word in value_list if word is not None):
                matched_key = key
                break

        if matched_key is not None:
            name, symbol, isin = self.stock_dict[matched_key]
            self.label_stock_name.setText(name)
            self.label_stock_isin.setText(isin)
            self.label_stock_symbol.setText(symbol)
            self.label_stock_id.setText('ID = ' + str(matched_key))
            self.setting['stock_id'] = matched_key
        else:
            self.label_stock_name.clear()
            self.label_stock_isin.clear()
            self.label_stock_symbol.clear()
            self.label_stock_id.clear()

    def handle_setting_validation(self):

        print(self.setting)