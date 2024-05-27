#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-01

@author: Roland VANDE MAELE

@abstract: the main window contains all the application's interface functions.

"""

import os
import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QMainWindow, QMenu, QInputDialog, QLineEdit,
    QMessageBox, QApplication, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QFileDialog, QTreeWidgetItem)
from PyQt6.QtGui import QDesktopServices, QCursor
from PyQt6.QtCore import QUrl, Qt, QThread, QDate
from src.models.base import Session
from src.business_logic.fmp.database_process import DBService, StockService
from src.business_logic.fmp.database_reporting import StockReporting
from src.services.sql import backup_database
import src.ui.main_window_UI as window
from src.ui.worker import Worker
from src.ui.mplwidget import MplWidget
from src.ui.chart_window import ChartWindow
from src.ui.finance_window import FinanceWindow


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

        self.db_service = None
        self.db_session = Session()
        self.stock_service = StockService(self.db_session)
        self.stock_reporting = StockReporting(self.db_session)
        self.worker = None
        self.chart_window = None
        self.finance_window = None

        self.setup_reporting()
        self.setup_dividend()
        self.setup_signal_connections()

    def setup_signal_connections(self):
        """Set up the signal connections for the UI elements."""
        self.action_postgresql_install.triggered.connect(self.set_pdf_to_open)
        self.action_postgresql_update.triggered.connect(self.set_pdf_to_open)
        self.action_timescaledb_install.triggered.connect(self.set_pdf_to_open)
        self.action_env_file.triggered.connect(self.set_pdf_to_open)
        self.action_create_new_database.triggered.connect(
            self.setup_new_database)
        self.action_create_tables.triggered.connect(self.setup_stock_tables)
        self.action_fetch_stock_symbols.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_dow_jones.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_sp_500.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_nasdaq.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_stoxx_600.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_company_profile.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_dividend.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_key_metrics_annual.triggered.connect(
            self.fetch_fmp_data)
        self.action_fetch_key_metrics_quarter.triggered.connect(
            self.fetch_fmp_data)
        self.action_historical_daily_chart.triggered.connect(
            self.fetch_fmp_data)
        self.action_update_daily_chart_.triggered.connect(self.fetch_fmp_data)
        self.action_backup.triggered.connect(self.create_dump)
        self.comboBox_reporting.currentTextChanged.connect(
            self.choice_reporting)
        self.comboBox_reporting.textHighlighted.connect(self.help_reporting)
        self.pushButton_query_clear.clicked.connect(self.clear_sql_query)
        self.pushButton_query_ok.clicked.connect(self.display_query_results)
        self.stock_service.update_signal.connect(
            self.update_text_browser_process)
        self.action_chart_window.triggered.connect(self.open_chart_window)
        self.action_finance_window.triggered.connect(self.open_finance_window)
        self.calendarWidget_dividend.clicked.connect(self.detail_dividends)
        self.tableWidget_dividend.cellClicked.connect(
            self.analyze_stock_dividend)
        self.pushButton_next_stock.clicked.connect(self.move_on_to_next_stock)
        self.pushButton_adjust_close.clicked.connect(self.update_adjusted_close)

    def set_pdf_to_open(self):
        """
        Opens a specific PDF file based on the UI action triggered by the user.

        This method determines the PDF file to open based on the context of 
        the action triggered by the user. It identifies the action and its 
        associated objects to derive the filename of the PDF document. The 
        filename is constructed from the titles of the action and its parent 
        menu, lowercased and concatenated with an underscore. The method then 
        attempts to open the PDF document using the `open_pdf` method. If the 
        operation is unsupported or fails, it prints an appropriate error 
        message.

        Raises:
            AttributeError: If no action is associated with the sender or no 
            associated objects are found.
            ValueError: If no parent `QMenu` is found among the associated 
            objects or if the operation to open the PDF is unsupported.
            Exception: For any other unexpected error that occurs.

        Note:
            - The method assumes that the PDF documents are stored in a `docs` 
            directory within the current working directory.
            - The expected naming convention for the PDF documents is `
            {menu_text}_{action_text}.pdf`, where `menu_text` and `action_text` 
            are the lowercased titles of the parent menu and the action, respectively.
            - Errors are caught and printed to the console, and the function 
            does not return a value upon encountering an error.
        """
        try:
            action = self.sender()
            if action is None:
                raise AttributeError("No action associated with the sender.")

            associated_objects = action.associatedObjects()
            if associated_objects is None:
                raise AttributeError("No associated objects found.")

            parent_menu = None
            for ass_object in associated_objects:
                if isinstance(ass_object, QMenu):
                    parent_menu = ass_object
                    break

            if parent_menu is None:
                raise ValueError("No parent QMenu found among associated objects.")

            action_text = action.text().lower().replace(" ", "_")
            menu_text = parent_menu.title().lower()

            if not self.open_pdf(f"docs/{menu_text}_{action_text}.pdf"):
                raise ValueError(f"Unsupported operation: {menu_text} - {action_text}")

        except AttributeError as e:
            print(f"Attribute error occurred: {e}")
        except TypeError as e:
            print(f"Type error occurred: {e}")
        except ValueError as e:
            print(f"Value error occurred: {e}")
        except Exception as e: # pylint: disable=broad-except
            print(f"An unexpected error occurred: {e}")

    def open_pdf(self, filepath):
        """
        Opens a PDF file with the system's default PDF viewer.

        This method attempts to open a PDF file located at `filepath` using the 
        system's default PDF viewer. It checks if the `filepath` is a string 
        and verifies the existence of the file at the given path. If the file 
        exists, it tries to open it with the default PDF viewer. If any step 
        fails, an appropriate error message is printed to the console.

        Args:
            filepath (str): The path to the PDF file that needs to be opened.

        Returns:
            bool: True if the file was successfully opened with the default PDF 
            viewer, False otherwise.

        Raises:
            FileNotFoundError: If the file at `filepath` does not exist.
            TypeError: If the `filepath` is not a string.
            OSError: If the file exists but failed to be opened with the default PDF viewer.
            AttributeError: If an attribute error occurs during the process.
            Exception: If an unexpected error occurs.

        """
        try:
            if not isinstance(filepath, str):
                raise TypeError("The filepath must be a string.")

            absolute_path = os.path.abspath(filepath)
            if not os.path.exists(absolute_path):
                raise FileNotFoundError(f"The file {absolute_path} does not exist.")

            url = QUrl.fromLocalFile(absolute_path)
            if not QDesktopServices.openUrl(url):
                raise OSError("Failed to open the PDF file with the default PDF viewer.")
            else:
                return True

        except FileNotFoundError as e:
            print(f"File not found error: {e}")
        except TypeError as e:
            print(f"Type error: {e}")
        except OSError as e:
            print(f"OS error: {e}")
        except AttributeError as e:
            print(f"Attribute error: {e}")
        except Exception as e: # pylint: disable=broad-except
            print(f"An unexpected error occurred: {e}")

    def setup_new_database(self):
        """
        Opens a dialog to prompt the user for a new database name and attempts to create it.

        This function displays a modal input dialog asking the user to enter 
        the name of a new database they wish to create. If the user provides a 
        name and clicks OK, the function attempts to create the database with 
        the given name by calling `create_new_database` function of the 
        DBService class. If the database creation is successful or fails due to 
        a validation or SQLAlchemy error, appropriate feedback should be given 
        to the user (not covered in this snippet).

        Raises:
            RuntimeError: Propagated from `create_new_database(database_name)` 
            if database creation fails for any reason, such as invalid name 
            format or database connection issues.

        """
        # Open an input dialog to ask the user for the database name
        database_name, ok_pressed = QInputDialog.getText(
            self, "Create New Database", "Enter database name:", QLineEdit.EchoMode.Normal, ""
        )

        # Check if the user pressed OK and provided a non-empty name
        if ok_pressed and database_name:
            try:
                # Attempt to create the new database with the provided name
                self.db_service = DBService(database_name)
                self.db_service.create_new_database()

                # Show a success message to the user
                QMessageBox.information(
                    self, "Success", "Database created successfully!\nThe application will now restart.") # pylint: disable=line-too-long

                # Restart the application
                os.execl(sys.executable, sys.executable, *sys.argv)

            except RuntimeError as e:
                # Show an error message to the user
                QMessageBox.critical(self, "Database Creation Failed", str(e))

    def setup_stock_tables(self):
        """
        Attempts to create stock tables and business time series table in the 
        database, convert some tables in TimescaleDB hypertables, and notifies 
        the user of the outcome.

        This function calls the `create_stock_tables` and 
        `create_business_time_series` method of the `stock_service` object to 
        initiate the creation of stock-related tables in the database. If the 
        operation is successful, a success message is displayed to the user. If 
        an error occurs, the function catches the exception and displays an 
        error message with the details of the failure.

        Args:
            None.

        Raises:
            Exception: Captures any exceptions raised during the table creation 
            process and displays an error message to the user. The exception is 
            not re-raised; instead, execution continues after displaying the 
            message.

        """
        # Set the mouse cursor to hourglass
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        try:
            self.stock_service.create_stock_tables()
            self.stock_service.convert_date_tables_to_hypertables()

            self.stock_service.create_business_time_series()

            self.display_performance_all_tables()

            # Show a success message to the user
            QMessageBox.information(self, "Success", "Stock tables created successfully!")

        except Exception as e: # pylint: disable=broad-except
            QMessageBox.critical(self, "Error",
            f"Failed to create stock tables due to an unexpected error: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def fetch_fmp_data(self) -> None:
        """
        Initiates the process to fetch financial market data based on the 
        selected action.

        This method retrieves the action initiated by the user, creates a new 
        background thread, and a worker object tasked with carrying out the 
        selected financial market data operation. The operation is executed in 
        a background thread to keep the UI responsive. It handles any errors 
        that occur during the setup and communicates back to the main UI thread 
        about the success or failure of the operation. Upon completion, it 
        updates the UI to reflect that the operation has finished.

        Args:
            None.

        Raises:
            AttributeError: If no action is associated with the sender, 
            indicating an issue with how the action was triggered.

        Note:
            This method connects several signals and slots to manage the 
            thread's lifecycle and to update the UI based on the worker's 
            progress and completion status. It also ensures the application's 
            cursor is set to indicate a loading state while the operation is ongoing.

        """
        try:
            action = self.sender()
            if action is None:
                raise AttributeError("No action associated with the sender.")

            associated_objects = action.associatedObjects()
            if associated_objects is None:
                raise AttributeError("No associated objects found.")

            parent_menu = None
            for ass_object in associated_objects:
                if isinstance(ass_object, QMenu):
                    parent_menu = ass_object
                    break

            if parent_menu is None:
                raise ValueError("No parent QMenu found among associated objects.")

            action_text = action.text()
            menu_text = parent_menu.title()

            self.thread = QThread()  # Create a QThread object
            self.worker = Worker(self.stock_service, menu_text, action_text)  # Create a worker

            # Move the worker to the thread
            self.worker.moveToThread(self.thread)

            # Connect signals and slots
            self.thread.started.connect(self.worker.run_fetch_fmp_data)
            self.worker.finished.connect(self.thread.quit)  # Clean up the thread when done
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            # Connect to restore cursor
            self.worker.finished.connect(lambda: QApplication.restoreOverrideCursor()) # pylint: disable=W0108

            # Connect to show success message
            self.worker.finished.connect(self.show_success_message)

            # Connect the worker's update signal to update the text browser
            self.worker.update_signal.connect(self.update_text_browser_process)

            # Start the thread
            self.thread.start()

            # Change cursor to indicate processing
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        except Exception as e:  # pylint: disable=broad-except
            # Log the error, show an error message, or both
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            QApplication.restoreOverrideCursor()

    def update_text_browser_process(self, message: str) -> None:
        """
        Appends a given message to the QTextBrowser widget.

        This method is primarily used as a slot connected to signals that emit
        messages indicating the progress or result of background operations. It
        updates the QTextBrowser in the main GUI to display messages in 
        real-time, allowing users to track the progress of tasks or see 
        informational messages as they are generated.

        Args:
            message (str): The message to be displayed in the QTextBrowser. 
            This could be any text, including status updates, error messages, 
            or results from operations performed by background threads or other 
            parts of the application.

        """
        self.textBrowser_process.append(message)

    def show_success_message(self, message: str) -> None:
        """
        Displays a success message in a QMessageBox.

        This function is called upon the successful completion of a background 
        task, such as fetching data or processing information. The message is 
        intended to be dynamic, reflecting the specific action that was 
        completed, providing the user with feedback about the task that was 
        executed.

        Args:
            message (str): The success message to be displayed. This message is 
            expected to be passed from the signal emitted by the Worker class 
            upon the completion of its task, and it can be customized to 
            reflect the specifics of the completed action.

        """
        QMessageBox.information(self, "Success", message)

    def setup_reporting(self):
        """Initializes the reporting section of the UI.

        This method populates the reporting combo box with a predefined list of 
        tables available for reporting from the `stock_reporting` service. It 
        ensures the user has a clear set of options for generating reports, 
        including an option to generate reports for all tables. The method 
        begins by inserting a placeholder item at the beginning of the combo 
        box to prompt the user to make a selection, followed by an option to 
        select all tables for a comprehensive report.

        """
        table_list = self.stock_reporting.table_list.copy()
        # Insert an option to select all tables for reporting
        table_list.insert(0, "PostgreSQL table performance")

        # Populate the combo box with the updated table list
        self.comboBox_reporting.addItems(table_list)

    def help_reporting(self, highlighted_text):
        """Updates the information text field based on the user's highlighted selection.

        This function provides immediate, contextual help to the user by 
        displaying a descriptive text message in a designated text field. When 
        the user highlights an option in the reporting combo box, this function 
        is triggered and updates the text field with a helpful message relevant 
        to the highlighted option. Otherwise, it clears the text field.

        Args:
            highlighted_text (str): The text that is currently highlighted by 
            the user in the combo box.

        """

        help_text = ""

        if highlighted_text == "PostgreSQL table performance":
            help_text = "Generate a performance report for each table in the database"
        elif highlighted_text == "sxxp":
            help_text = "Generates plots to report on the STOXX Europe 600 index components"
        else:
            help_text = f"Generates plots to report on the {highlighted_text} table"

        self.lineEdit_reporting.setText(help_text)

    def choice_reporting(self, current_text):
        """Handles the user's choice from the reporting options combo box.

        When a user selects an option from the reporting combo box, this method
        is invoked to process the selection. This method sets the application's
        cursor to an hourglass (indicating a process is running), attempts to 
        generate the requested report, and ensures the cursor is restored 
        afterward. If an error occurs during report generation, an error 
        message will be displayed to the user.

        Args:
            current_text (str): The currently selected text from the combo box, 
            which indicates the user's choice of report to generate.

        Raises:
            Exception: Re-raises any exception that occurs during the report 
            generation process after displaying an error message to the user. 
            This allows for higher-level error handling or logging.

        """
        # Set the mouse cursor to hourglass
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        try:
            if current_text == "PostgreSQL table performance":
                self.display_performance_all_tables()
            else:
                self.display_report_table(current_text)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error", f"An error occurred while generating the report : {e}. Please try again.")
            # Log the exception and show an error message
            raise(f"Error during reporting: {e}") from e

        finally:
            # Restore the mouse cursor to its default state
            QApplication.restoreOverrideCursor()

    def display_performance_all_tables(self):
        """
        Updates the QTextBrowser with the latest performance data for each table.

        This function retrieves the latest performance data for each table in 
        the database by calling `report_on_tables_performance` from the 
        `stock_reporting` object. It formats this data into HTML and displays 
        it in a QTextBrowser widget within the GUI. The performance data 
        includes the timestamp of the report, the table name, whether the table 
        is a hypertable, the execution time for queries on the table, and the 
        disk size used by the table.

        Raises:
            RuntimeError: If an error occurs while retrieving the performance 
            data or while formatting it for display. The error message is shown 
            to the user in a message box.

        """
        try:
            performance_data = self.stock_reporting.report_on_tables_performance()

            # Assuming you have a QTableWidget named tableWidget_tables in your GUI
            self.tableWidget_tables.setColumnCount(6)  # Set the number of columns
            self.tableWidget_tables.setRowCount(len(performance_data))  # Set the number of rows

            # Set headers for the QTableWidget
            self.tableWidget_tables.setHorizontalHeaderLabels(
                ["Timestamp", "Table Name", "Hypertable",
                 "Dimension (r x c)", "Execution Time (s)", "Disk Size"])
            self.tableWidget_tables.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch)

            for row, record in enumerate(performance_data):
                (timestamp, table_name, hypertable, row_count, column_count,
                 execution_time, disk_size) = record
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                # Create QTableWidgetItem for each piece of data
                self.tableWidget_tables.setItem(row, 0, QTableWidgetItem(formatted_timestamp))
                self.tableWidget_tables.setItem(row, 1, QTableWidgetItem(table_name))
                self.tableWidget_tables.setItem(row, 2, QTableWidgetItem(str(hypertable)))
                self.tableWidget_tables.setItem(row, 3,
                 QTableWidgetItem(str(row_count) + ' x ' + str(column_count)))
                self.tableWidget_tables.setItem(row, 4, QTableWidgetItem(str(execution_time)))
                self.tableWidget_tables.setItem(row, 5, QTableWidgetItem(str(disk_size)))

            self.tabWidget_reporting.setCurrentIndex(1)

        except RuntimeError as e:
            QMessageBox.critical(self, "Error", str(e))

    def remove_tab_above_index(self, tab_widget: QTabWidget,
        index: int) -> None:
        """
        Removes all tabs in a QTabWidget that have an index greater than the specified index.

        This function iterates over the tabs of a given QTabWidget, starting 
        from the last tab and moving backwards. It removes each tab that has an 
        index higher than the specified index. The function operates safely 
        even if the index is out of the normal range by ensuring that only 
        valid indices are targeted for removal.

        Args:
            tab_widget (QTabWidget): The QTabWidget from which tabs will be 
            removed.
            index (int): The index above which all tabs will be removed. Tabs 
            at this index and lower will remain.

        Returns:
            None: This function does not return a value but modifies the 
            QTabWidget directly.

        Raises:
            RuntimeError: If an error occurs during the tab removal process.
            This is caught and re-raised from any underlying Qt exceptions.

        """
        try:
            for i in range(tab_widget.count() - 1, index, -1):
                tab_widget.removeTab(i)
        except Exception as e:
            raise RuntimeError("Failed to remove tabs properly.") from e

    def create_widget_instance(self, topics: list) -> dict:
        """
        Creates and returns a dictionary of widgets based on the topics provided.

        Each topic in the list will lead to the creation of a specific type of 
        widget: if the topic contains the word 'table', a QTableWidget is 
        created; otherwise, an MplWidget is created and associated with the 
        topic.

        Args:
            topics (list): A list of topics, each a string that determines the 
            type of widget to be created.

        Returns:
            dict: A dictionary mapping each topic to its corresponding widget.

        Raises:
            Exception: Describes an error that occurred during the widget creation process.

        """
        reports = {}
        try:
            for topic in topics:
                if 'table' in topic.lower():
                    table_widget = QTableWidget()
                    reports[topic] = table_widget
                else:
                    mpl_widget = MplWidget(self)
                    reports[topic] = mpl_widget

        except Exception as e:
            raise RuntimeError(f"Failed to create widget for topic '{topic}'.") from e

        return reports

    def display_report_table(self, table_name):
        """
        Generates and displays a series of report tabs for various topics.

        This method creates and adds new tabs to a tab widget within the 
        application, each tab containing a graphical representation of 
        different topics. It handles the creation of the graphical widgets and 
        manages the display within the user interface. If an error occurs 
        during the generation of the reports, it will display an error message.

        Raises:
            Exception: An error dialog will pop up if an exception is caught 
            during the generation of the report tabs.

        """
        try:
            self.remove_tab_above_index(self.tabWidget_reporting, 2)

            # Define topics based on the table name
            if table_name == "sxxp":
                topics = ["Metric", "Currency", "Sector", "Country", "Type"]
                report_fct = self.stock_reporting.report_sxxp_table
            elif table_name == "usindex":
                topics = ["Metric", "Sector", "Type"]
                report_fct = self.stock_reporting.report_usindex_table
            elif table_name == "dividend":
                topics = ["Latest dates -> Plot", "NaN by stock -> Table", "NaN by column -> Table"]
                report_fct = self.stock_reporting.report_dividend_table
            elif table_name == "dailychart":
                topics = ["Missing update -> Table", "NaN -> Plot",
                "NaN by stock -> Table", "NaN by column -> Table"]
                report_fct = self.stock_reporting.report_dailychart_table
            elif table_name == "stocksymbol":
                topics = ['exchange', 'type_']
                report_fct = self.stock_reporting.report_stocksymbol_table
            elif table_name == "companyprofile":
                topics = ['currency', 'sector', 'country']
                report_fct = self.stock_reporting.report_companyprofile_table
            elif table_name == "keymetrics":
                topics = ["Latest dates -> Plot", "NaN -> Plot",
                "NaN by stock -> Table", "NaN by column -> Table"]
                report_fct = self.stock_reporting.report_keymetrics_table
            else:
                raise ValueError(f"Unsupported report type: {table_name}")

            # Create Widget instances
            report_widget = self.create_widget_instance(topics)

            # Generate reports and pass them to the reporting handler
            report_fct(report_widget)

            # Add MplWidget instances as new tabs in the reporting tab widget
            for topic, widget in report_widget.items():
                self.tabWidget_reporting.addTab(widget, f"{topic}")

            # Set the default active tab index
            self.tabWidget_reporting.setCurrentIndex(3)

        except Exception as e: # pylint: disable=broad-except
            QMessageBox.critical(
                self, "Error",
                f"An error occurred while generating the report : {e}. Please try again."
            )

    def clear_sql_query(self):
        """ Clear the text in the QTextEdit """
        self.textEdit_query.clear()

    def display_query_results(self):
        """
        Executes a SQL SELECT query from the text input provided in a QTextEdit 
        and displays the results.

        This function retrieves the text from a QTextEdit, processes it to 
        remove new line characters, and checks if the query starts with 
        'SELECT'. If the query is valid, it is executed and the results are
        displayed. If the query is invalid or fails due to a syntax error, a 
        critical error message is shown using a QMessageBox.

        Raises:
            ValueError: If the query does not start with 'SELECT'.
            Exception: If there is a syntax or execution error in the SQL query.

        Side Effects:
            - Shows a QMessageBox if an error is detected.
            - Executes a SQL query on the associated database.

        Note:
            This function only allows SELECT queries to prevent potential 
            modification or deletion of data. It is designed to handle basic 
            SQL queries and may not handle complex SQL syntax without errors.

        """
        # Retrieve text from QTextEdit
        raw_text = self.textEdit_query.toPlainText()

        # Remove all new line characters
        query_text = raw_text.replace('\n', ' ').replace('\r', ' ')

        # Check if the query is a SELECT query
        if not query_text.strip().lower().startswith('select'):
            QMessageBox.critical(self, 'Invalid Query', 'Only SELECT queries are allowed.')
            return

        try:
            # Execute the SQL query
            self.stock_reporting.get_sql_query_result(self.tableWidget_query, query_text)
        except Exception as e:  # pylint: disable=broad-except
            # Display a critical error message about the syntax error
            QMessageBox.critical(self, 'Query Error', f'Syntax error in SQL query: {e}')

    def open_chart_window(self):
        """
        Opens the chart window.

        This method creates and shows an instance of ChartWindow. It includes 
        error handling to manage potential issues during window initialization and display.

        Args:
            None
        """
        try:
            self.chart_window = ChartWindow(self)
            self.chart_window.show()

        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to open the chart window: {str(e)}")

    def open_finance_window(self):
        """
        Opens the finance window.

        This method creates and shows an instance of FinanceWindow. It includes 
        error handling to manage potential issues during window initialization and display.

        Args:
            None
        """
        try:
            self.finance_window = FinanceWindow(self)
            self.finance_window.show()

        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to open the finance window: {str(e)}")

    def create_dump(self):
        """
        Opens a file dialog allowing the user to specify the file path and name 
        for saving a database dump. 
        
        If the user does not specify a '.sql' extension, it is automatically 
        appended. This function handles the entire process of creating the 
        database dump using the 'backup_database' function and provides user 
        feedback via message boxes indicating success or error.

        This method modifies the application's cursor to an hourglass during 
        the dump operation to indicate processing and restores it afterwards. 
        Errors are caught and displayed in a critical error message box.

        Returns:
            None. The result of the operation is communicated to the user via 
            GUI dialog boxes.

        """
        # Open a file dialog to let the user choose where to save the dump
        file_name, _ = QFileDialog.getSaveFileName(self,
                "Save Dump File",
                "",
                "SQL Files (*.sql);;All Files (*)",
                options=QFileDialog.Option.DontUseNativeDialog)

        if file_name:
            # Check if the file name ends with '.sql', if not, append it
            if not file_name.lower().endswith('.sql'):
                file_name += '.sql'

            # Set the mouse cursor to hourglass
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

            try:
                success = backup_database(file_name)
                QMessageBox.information(self, "Success", success)
            except Exception as e:  # pylint: disable=broad-except
                QMessageBox.critical(
                    self, 'Error', f'An error occurred while saving the dump file: {e}')
            finally:
                # Restore the mouse cursor to its default state
                QApplication.restoreOverrideCursor()
        else:
            QMessageBox.warning(self, 'No File Selected', 'No file was selected for the backup.')

    def setup_dividend(self):
        """Sets up the dividend information in the UI's tree widget.

        This method initializes the display for a list of dividend-paying 
        companies in a tree widget, spanning from one week before today to one 
        week after today. It fetches the dividend data using a method from 
        `stock_reporting`, formats it, and populates the tree widget with this 
        data, organizing it by date and listing companies under each date. 
        Additionally, the current date's data is expanded by default for 
        immediate visibility.

        Args:
            None

        """
        today = datetime.today()
        week = 7
        start_date = today - timedelta(days=week)
        end_date = today + timedelta(days=week)

        try:
            df = self.stock_reporting.get_dividend_paying_companies(
                start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

            self.treeWidget_dividend.setColumnCount(1)
            self.treeWidget_dividend.setHeaderLabels(['Current dividend-paying companies'])

            for _, row in df.iterrows():
                # Create a parent item for each date
                parent = QTreeWidgetItem(self.treeWidget_dividend)
                parent.setText(0, str(row['date']))
                if str(row['date']) == today.strftime('%Y-%m-%d'):
                    parent.setExpanded(True)

                # Create a child item for each stock symbol in the list
                for symbol in row['list_stock_names']:
                    child = QTreeWidgetItem(parent)
                    child.setText(0, symbol)

        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to setup dividend: {str(e)}")

    def detail_dividends(self, calendar_date: QDate):
        """Displays the dividend details for a selected date in a table widget within the UI.

        This method is typically triggered by a user action in the UI, such as 
        selecting a date from a calendar widget. It converts the selected date 
        to a string format suitable for querying dividend details, then calls 
        another method to fetch these details and display them in a designated 
        table widget.

        Args:
            calendar_date (QDate): The date selected by the user, represented 
            as a QDate object.

        """
        self.textBrowser_dividend.clear()

        try:
            self.stock_reporting.get_dividend_details(
                self.tableWidget_dividend, calendar_date.toString('yyyy-MM-dd'))

        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to detail dividend: {str(e)}")

    def analyze_stock_dividend(self, row_number):
        """
        Analyzes the dividend details for a specific stock based on the 
        selected date and stock ID from the user interface elements. Updates 
        the text browser with the results of the analysis.

        Args:
            row_number (int): The row index in the table widget from which the 
            stock ID is extracted.

        Raises:
            Exception: Generic exceptions captured during the dividend analysis 
            process are caught and logged to the console.

        """
        try:
            self.textBrowser_dividend.clear()

            calendar_date = self.calendarWidget_dividend.selectedDate().toString('yyyy-MM-dd')
            stock_id = int(self.tableWidget_dividend.verticalHeader().model().headerData(
                row_number, Qt.Orientation.Vertical))

            # Generate the dividend analysis using the selected date and stock ID
            output, _, _ = self.stock_reporting.generate_dividend_analysis(calendar_date, stock_id)

            # Update the text browser with the results
            self.textBrowser_dividend.setText(output)

        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to detail dividend: {str(e)}")

    def move_on_to_next_stock(self):
        """
        Advances the current selection in the tableWidget dividend to the next 
        row and analyzes the stock dividend for that row. 

        """
        if self.tableWidget_dividend is not None:
            current_row = self.tableWidget_dividend.currentRow()
            next_row = current_row + 1  # Calculate the next row index

            # Check if the next row index is within the range of existing rows
            if next_row < self.tableWidget_dividend.rowCount():
                self.analyze_stock_dividend(next_row)
                self.tableWidget_dividend.setCurrentCell(next_row, 0)
            else:
                print("Reached the last row of the table or empty table.")
        else:
            print("The table widget does not exist.")

    def update_adjusted_close(self):
        """Updates the adjusted closing prices in the daily charts for a 
        selected stock.

        This method fetches and updates the adjusted closing prices for the 
        stock currently selected in the `tableWidget_dividend`. It retrieves 
        the stock ID and symbol from the table, and calls a service to update 
        the daily charts. Upon completion, a message box informs the user that 
        the update has completed.

        The cursor is set to a waiting cursor during the operation to indicate 
        that the application is busy. If the operation fails, it will catch and 
        print the exception.

        Raises:
            Exception: If there is any error during the fetching or updating 
            process, it catches a broad exception and prints an error message.

        """
        self.tabWidget.setCurrentIndex(0)
        QApplication.processEvents()  # Update the UI immediately

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            stock_id = int(
                self.tableWidget_dividend.verticalHeader().model().headerData(
                    self.tableWidget_dividend.currentRow(), Qt.Orientation.Vertical))

            symbol = self.tableWidget_dividend.item(
                self.tableWidget_dividend.currentRow(), 1).text()

            self.stock_service.fetch_daily_charts_by_stock(stock_id, symbol)

            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, 'Update Completed',
                'Adjusted closing update in dailychart completed')

        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to update adjusted close: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()
