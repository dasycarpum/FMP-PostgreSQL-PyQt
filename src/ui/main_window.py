#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-01

@author: Roland VANDE MAELE

@abstract: the main window contains all the application's interface functions.

"""

import os
from PyQt6.QtWidgets import (QMainWindow, QMenu, QInputDialog, QLineEdit,
    QMessageBox)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from src.business_logic.fmp.database_process import create_new_database
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

        self.setup_signal_connections()

    def setup_signal_connections(self):
        """Set up the signal connections for the UI elements."""
        self.action_postgresql_install.triggered.connect(self.set_pdf_to_open)
        self.action_postgresql_update.triggered.connect(self.set_pdf_to_open)
        self.action_timescaledb_install.triggered.connect(self.set_pdf_to_open)
        self.action_create_new_database.triggered.connect(self.setup_new_database)

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
        the given name by calling `create_new_database`. If the database 
        creation is successful or fails due to a validation or SQLAlchemy error,
        appropriate feedback should be given to the user (not covered in this snippet).

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
                create_new_database(database_name)
                # Show a success message to the user
                QMessageBox.information(self, "Success", "Database created successfully!")
            except RuntimeError as e:
                # Show an error message to the user
                QMessageBox.critical(self, "Database Creation Failed", str(e))