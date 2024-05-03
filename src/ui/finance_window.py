#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-27

@author: Roland VANDE MAELE

@abstract: the finance window contains all the tools for financial analysis of equities.

"""

from PyQt6.QtWidgets import QMainWindow, QMessageBox
from src.models.base import Session
import src.ui.finance_window_UI as window
from src.dal.fmp.database_query import StockQuery
from src.business_logic.fmp.database_reporting import StockReporting
from src.services import plot
from src.services.various import CheckableComboBox


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
        self.setup_signal_connections()

    def setup_signal_connections(self) -> None:
        """Set up the signal connections for the UI elements."""
        self.lineEdit_search.textChanged.connect(self.on_text_changed)
        self.pushButton_stock.clicked.connect(self.handle_stock_validation)
        self.spinBox_dividend.valueChanged.connect(self.handle_stock_validation)
        self.radioButton_quarter.clicked.connect(self.handle_stock_validation)
        self.radioButton_annual.clicked.connect(self.handle_stock_validation)
        self.spinBox_metrics.valueChanged.connect(self.handle_stock_validation)
        self.comboBox_metrics.textHighlighted.connect(
            self.handle_stock_validation)


    def setup_finance(self) -> None:
        """Set up the initial configuration by initializing attributes"""
        self.db_session = Session()
        self.stock_reporting = StockReporting(self.db_session)
        self.stock_dict = self.stock_reporting.get_stock_dictionary()
        self.setting = {}
        self.stock_query = StockQuery(self.db_session)
        keymetrics_columns = self.stock_query.get_keymetrics_columns()
        self.comboBox_metrics = CheckableComboBox(self) # pylint: disable=invalid-name
        self.comboBox_metrics.setPlaceholderText('Full list')
        for metric in keymetrics_columns[5:]:
            is_checked = metric in ['pe_ratio', 'pb_ratio', 'dividend_yield', 'roe']
            self.comboBox_metrics.add_check_item(metric, is_checked)
        self.verticalLayout_metrics.addWidget(self.comboBox_metrics)

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

    def handle_stock_validation(self):
        """
        Validate the current stock, get the data and display chart + tables.
        
        """
        if self.setting.get('stock_id') is not None:
            # Draw historical dividends
            df_dividend = self.stock_reporting.get_dividend_data(
                self.setting['stock_id'], self.spinBox_dividend.value())
            plot.plot_vertical_barchart(self.widget_dividend.canvas,
                df_dividend, 'year', 'dividend', "Historical dividends")

            # Display company profile
            df_profile = self.stock_reporting.get_company_profile(
                self.setting['stock_id'])
            self.textBrowser_profile.setHtml(df_profile.to_html(index=False))

            # Populate historical key metrics
            quarter = True
            if self.radioButton_quarter.isChecked():
                self.spinBox_metrics.setSuffix(' quarters')
            else:
                self.spinBox_metrics.setSuffix(' years')
                quarter = False

            key_metrics = self.comboBox_metrics.checked_items()
            df_metrics = self.stock_reporting.get_key_metric_data(
                self.setting['stock_id'], key_metrics, quarter, self.spinBox_metrics.value())
            plot.populate_tablewidget_with_df(self.tableWidget_key_metrics,
                df_metrics)
        else:
            QMessageBox.warning(self, "ID problem !", "A stock identifier is required.")
