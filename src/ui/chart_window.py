#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-18

@author: Roland VANDE MAELE

@abstract: the chart window contains all the tools for technical analysis of equities.

"""

import os
import pandas as pd
import numpy as np
from plotly.offline import plot
import plotly.graph_objects as go
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from src.models.base import Session
import src.ui.chart_window_UI as window
from src.business_logic.fmp.database_reporting import StockReporting

os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = '/home/roland/Bureau/FMP-PostgreSQL-PyQt/.venv/lib/python3.11/site-packages/PyQt6/Qt6/libexec/qtwebengine_dictionaries' # pylint: disable=line-too-long

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

        self.setup_charting()
        self.setup_signal_connections()

    def setup_signal_connections(self) -> None:
        """Set up the signal connections for the UI elements."""
        self.lineEdit_search.textChanged.connect(self.on_text_changed)
        self.comboBox_period.currentTextChanged.connect(self.period_changed)
        self.comboBox_interval.currentTextChanged.connect(self.interval_changed)
        self.checkBox_log_scale.stateChanged.connect(self.log_scale_changed)
        self.pushButton_setting.clicked.connect(self.handle_setting_validation)

    def setup_charting(self) -> None:
        """Set up the initial charting configuration by initializing attributes"""
        self.db_session = Session()
        self.stock_reporting = StockReporting(self.db_session)
        self.stock_dict = self.stock_reporting.get_stock_dictionary()
        self.setting = {}
        self.setting['log_scale'] = False

        period = ['3 months', '18 months', '3 years', '9 years', '18 years', 'max period']
        interval = ['daily', 'weekly', 'monthly']
        # Populate the combo box with the updated table list
        self.comboBox_period.addItems(period)
        self.comboBox_interval.addItems(interval)

    def on_text_changed(self, text: str) -> None :
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

    def period_to_days(self, period_str: str) -> int:
        """Convert a period string into an equivalent number of days.

        Args:
            period_str (str): The period string to convert.

        Returns:
            int: The number of days corresponding to the period string, or 0 on error.
        """
        try:
            # Split the string into number and period type
            num, unit = period_str.split()
            num = int(num)  # Convert the number part to an integer

            # Define the average lengths
            if 'month' in unit:
                # Average days in a month
                return num * 30
            elif 'year' in unit:
                # Average days in a year
                return num * 365
        except ValueError:
            # Return 0 if there's any error during parsing or conversion
            return 0

    def period_changed(self, text: str) -> None:
        """Update the period setting when the period combo box value changes.

        Args:
            text (str): The new period text from the combo box.
        """
        self.setting['period'] = self.period_to_days(text)
        self.handle_setting_validation()

    def interval_changed(self, text: str) -> None:
        """Update the interval setting when the interval combo box value changes.

        Args:
            text (str): The new interval text from the combo box.

        """
        self.setting['interval'] = text
        self.handle_setting_validation()

    def log_scale_changed(self) -> None:
        """Toggle the log scale setting based on the checkbox state."""

        self.setting['log_scale'] = self.checkBox_log_scale.isChecked()
        self.handle_setting_validation()

    def handle_setting_validation(self):
        """Validate the current settings and print them if they are complete."""

        if len(self.setting) == 4:
            print(self.setting)
            self.draw_a_plotly_bar_plot()

    def draw_a_plotly_bar_plot(self):
        """Draws a bar plot in the PyQt application using Plotly.
        
        This function creates a bar plot using Plotly based on hardcoded x and 
        y values. It then displays this plot within a QWebEngineView that is 
        inserted into the existing QVBoxLayout (`verticalLayout_plotly`).

        """
        # Prepare data
        data = pd.DataFrame({
            'x': 0.5 + np.arange(8),
            'y': [4.8, 5.5, 3.5, 4.6, 6.5, 6.6, 2.6, 3.0]
        })

        # Create a Plotly figure
        fig = go.Figure(
            data=[go.Bar(x=data['x'], y=data['y'],
            marker_line_color='white', marker_line_width=0.7)])

        # Generate HTML representation of the Plotly figure
        plot_html = plot(fig, output_type='div', include_plotlyjs='cdn')

        # Create a QWebEngineView to display the HTML
        webview = QWebEngineView()
        webview.setHtml(plot_html)

        # Add the QWebEngineView to the QVBoxLayout
        self.verticalLayout_chart.addWidget(webview)
