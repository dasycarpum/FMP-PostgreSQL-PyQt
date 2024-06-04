#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-18

@author: Roland VANDE MAELE

@abstract: the chart window contains all the tools for technical analysis of equities.

"""

from datetime import datetime, timedelta
import pandas as pd
from PyQt6.QtWidgets import QMainWindow
from src.models.base import Session
import src.ui.chart_window_UI as window
from src.business_logic.fmp.database_reporting import StockReporting
from src.services import plot, chart


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
        self.checkBox_bollinger.stateChanged.connect(self.bollinger_changed)
        self.spinBox_window_size.valueChanged.connect(self.bollinger_changed)
        self.doubleSpinBox_num_std.valueChanged.connect(self.bollinger_changed)
        self.checkBox_sma.stateChanged.connect(self.moving_average_changed)
        self.spinBox_sma_1.valueChanged.connect(self.moving_average_changed)
        self.spinBox_sma_2.valueChanged.connect(self.moving_average_changed)

    def setup_charting(self) -> None:
        """Set up the initial charting configuration by initializing attributes"""
        self.lineEdit_search.setFocus()
        self.db_session = Session()
        self.stock_reporting = StockReporting(self.db_session)
        self.stock_dict = self.stock_reporting.get_stock_dictionary()
        self.setting = {}
        self.setting['log_scale'] = False
        self.setting['bollinger'] = False
        self.setting['sma'] = False

        # Populate the combo box with the updated table list
        period = ['3 months', '18 months', '3 years', '9 years', '18 years', 'max period']
        self.comboBox_period.addItems(period)
        interval = ['daily', 'weekly', 'monthly']
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
            name, symbol, isin, cik = self.stock_dict[matched_key]
            self.label_stock_name.setText(name)
            if isin is not None:
                self.label_stock_isin.setText(isin)
            else:
                self.label_stock_isin.setText(cik)
            self.label_stock_symbol.setText(symbol)
            self.label_stock_id.setText('ID = ' + str(matched_key))
            self.setting['stock_id'] = matched_key
        else:
            self.label_stock_name.clear()
            self.label_stock_isin.clear()
            self.label_stock_symbol.clear()
            self.label_stock_id.clear()

    def period_to_date(self, period_str: str) -> str:
        """Convert a period string to a date that is the number of days before today.

        Args:
            period_str (str): The period string to convert (e.g., '2 months').

        Returns:
            str: The date in 'YYYY-MM-DD' format corresponding to the current 
            date minus the number of days, or '1985-01-01' on error.
        """
        try:
            # Split the string into number and period type
            num, unit = period_str.split()
            num = int(num)  # Convert the number part to an integer

            # Calculate the number of days from the period
            if 'month' in unit:
                # Assume an average of 30 days per month
                days = num * 30
            elif 'year' in unit:
                # Assume an average of 365 days per year
                days = num * 365

            # Calculate the date by subtracting the calculated days from today's date
            target_date = datetime.today() - timedelta(days=days)
            # Format the date as 'YYYY-MM-DD'
            return target_date.strftime('%Y-%m-%d')

        except ValueError:
            return '1985-01-01'

    def period_changed(self, text: str) -> None:
        """Update the period setting when the period combo box value changes.

        Args:
            text (str): The new period text from the combo box.
        """
        self.setting['period'] = self.period_to_date(text)
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

    def bollinger_changed(self) -> None:
        """Toggle the Bollinger setting based on the checkbox state and spinbox values."""

        self.setting['bollinger'] = self.checkBox_bollinger.isChecked()
        self.setting['window_size'] = self.spinBox_window_size.value()
        self.setting['num_std'] = self.doubleSpinBox_num_std.value()
        self.handle_setting_validation()

    def moving_average_changed(self) -> None:
        """Toggle the moving average setting based on the checkbox state and spinbox values."""

        self.setting['sma'] = self.checkBox_sma.isChecked()
        self.setting['sma_1'] = self.spinBox_sma_1.value()
        self.setting['sma_2'] = self.spinBox_sma_2.value()
        self.handle_setting_validation()

    def handle_setting_validation(self):
        """Validate the current settings, get the data and display the charts."""
        required_keys = ['stock_id', 'period', 'interval']
        if all(key in self.setting for key in required_keys): # Minimum settings are assigned
            # Retrieve daily chart data for a stock from a starting date
            df = self.stock_reporting.get_dailychart_data(
                self.setting['stock_id'], self.setting['period'])

            # Convert the 'date' column to datetime and set it as the index
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            # Resample accordingly
            if self.setting['interval'] != 'daily':
                df = df.resample(self.setting['interval'][0].upper()).agg(
                       {'open':'first','high':'max','low':'min','close':'last','volume':'sum'})
            else:
                df.sort_index(inplace=True)

            # Optimal moving averages
            if len(df) > 60:
                optimal_days = chart.calculate_optimal_moving_averages(df['close'])
                optimal_stds =chart.calculate_optimal_stds(df, optimal_days)

                optimal_days = list(map(str, optimal_days))
                formatted_string = ', '.join(optimal_days[:-1]) + ' or ' + optimal_days[-1]
                self.textBrowser.setText(f"Optimal MA : {formatted_string} days")

                optimal_stds = list(map(str, optimal_stds))
                formatted_string = ', '.join(optimal_stds[:-1]) + ' or ' + optimal_stds[-1]
                self.textBrowser.append(f"Optimal std : {formatted_string} days")
            else:
                self.textBrowser.clear()

            # Draw a candlestick chart
            plot.draw_a_plotly_candlestick_chart(self.verticalLayout_chart, df, self.setting)
