#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-09

@author: Roland VANDE MAELE

@abstract: Worker class allows QThread to be integrated into the PyQt6 
application for background processing and maintaining the user interface 
responsive while executing time-consuming tasks

"""

from PyQt6.QtCore import QObject, pyqtSignal

class Worker(QObject):
    """
    A worker class for performing database operations in a separate thread.

    This class is designed to perform various stock service actions in the 
    background, emitting signals to communicate with the main GUI thread.

    Attributes:
        finished (pyqtSignal): Signal to indicate the task is done.
        update_signal (pyqtSignal): Signal to emit messages with string data.

    """
    finished = pyqtSignal(str)  # Signal to indicate the task is done
    update_signal = pyqtSignal(str)  # To emit messages

    def __init__(self, stock_service, menu, action):
        """
        Initializes the Worker object with a stock service instance and a specified action.

        Args:
            stock_service: The stock service instance to perform database operations.
            menu (str): The specific menu of the action.
            action (str): The specific action to be performed by the worker.

        """
        super().__init__()
        self.stock_service = stock_service
        self.menu = menu
        self.action = action

    def run_fetch_fmp_data(self):
        """ 
        Connect the worker's update signal to the stock_service's update signal
        and fetch initial FMP data based on the action initiated by the user.

        Depending on the 'action' attribute, it calls a different method on the
        stock_service to perform various tasks such as fetching stock symbols, 
        company profiles, historical components of STOXX Europe 600, dividends, 
        key metrics, or daily charts. It handles exceptions to avoid crashes 
        and ensure smooth operation. Upon completion or error, it emits the 
        'finished' signal.

        Args:
            None.

        Raises:
            Exception: For any unexpected errors during the fetch process.
        
        """
        try:
            if self.menu == "Fetch initial data":
                if self.action == "Stock symbols":
                    self.stock_service.fetch_stock_symbols()
                elif self.action == "Company profile":
                    self.stock_service.fetch_company_profiles()
                elif self.action == "STOXX Europe 600":
                    self.stock_service.fetch_sxxp_historical_components('20240301')
                elif self.action == "Dividend":
                    self.stock_service.fetch_dividends_in_batches()
                elif self.action == "Key metrics":
                    self.stock_service.fetch_keys_metrics_in_batches()
                elif self.action == "Daily chart":
                    self.stock_service.fetch_daily_charts_by_period()
            elif self.menu == "Update time data":
                if self.action == "Daily chart":
                    self.stock_service.fetch_daily_chart_updating()

        except Exception as e: # pylint: disable=broad-except
            # Optionally, log the exception or emit it using update_signal
            self.update_signal.emit(f"Error during '{self.action}': {str(e)}")
        finally:
            self.finished.emit(f"FMP data : {self.action} fetched successfully!")
