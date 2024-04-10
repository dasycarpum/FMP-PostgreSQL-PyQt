#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-01

@author: Roland VANDE MAELE

@abstract: the main window contains all the application's interface functions.

"""

import os
from PyQt6.QtWidgets import (QMainWindow, QMenu, QInputDialog, QLineEdit,
    QMessageBox, QApplication)
from PyQt6.QtGui import QDesktopServices, QCursor
from PyQt6.QtCore import QUrl, Qt, QThread
from src.models.base import Session
from src.business_logic.fmp.database_process import DBService, StockService
from src.business_logic.fmp.database_reporting import StockReporting
import src.ui.main_window_UI as window
from src.ui.worker import Worker


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

        self.setup_signal_connections()

    def setup_signal_connections(self):
        """Set up the signal connections for the UI elements."""
        self.action_postgresql_install.triggered.connect(self.set_pdf_to_open)
        self.action_postgresql_update.triggered.connect(self.set_pdf_to_open)
        self.action_timescaledb_install.triggered.connect(self.set_pdf_to_open)
        self.action_create_new_database.triggered.connect(
            self.setup_new_database)
        self.action_create_tables.triggered.connect(self.setup_stock_tables)
        self.action_fetch_stock_symbols.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_stoxx_europe.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_company_profile.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_dividend.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_key_metrics.triggered.connect(self.fetch_fmp_data)
        self.action_fetch_daily_chart.triggered.connect(self.fetch_fmp_data)
        self.action_update_stoxx_europe.triggered.connect(self.fetch_fmp_data)
        self.action_update_dividend.triggered.connect(self.fetch_fmp_data)
        self.action_update_key_metrics.triggered.connect(self.fetch_fmp_data)
        self.action_update_daily_chart.triggered.connect(self.fetch_fmp_data)

        self.stock_service.update_signal.connect(
            self.update_text_browser_process)

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

            action_text = action.text().lower()
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
                QMessageBox.information(self, "Success", "Database created successfully!")
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

            self.update_performance_report()

            # Show a success message to the user
            QMessageBox.information(self, "Success", "Stock tables created successfully!")

        except Exception as e: # pylint: disable=broad-except
            QMessageBox.critical(self, "Error",
            f"Failed to create stock tables due to an unexpected error: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def update_performance_report(self):
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
            report_html = "<html><head><title>Table Performance Report</title></head><body>"
            report_html += "<h2>Table Performance Report</h2>"
            report_html += "<table border='1'><tr><th>Timestamp</th><th>Table Name</th><th>Hypertable</th><th>Execution Time (s)</th><th>Disk Size (bytes)</th></tr>" # pylint: disable=line-too-long

            for record in performance_data:
                timestamp, table_name, hypertable, execution_time, disk_size = record
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                report_html += f"<tr><td>{formatted_timestamp}</td><td>{table_name}</td><td>{hypertable}</td><td>{execution_time}</td><td>{disk_size}</td></tr>" # pylint: disable=line-too-long

            report_html += "</table></body></html>"
            self.textBrowser_tables.setHtml(report_html)
            self.tabWidget_reporting.setCurrentIndex(1)

        except RuntimeError as e:
            QMessageBox.critical(self, "Error", str(e))

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
