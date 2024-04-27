#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

import os
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def set_qtwebengine_dictionaries_path():
    """Sets the QTWEBENGINE_DICTIONARIES_PATH environment variable.

    This function calculates the path to the 'qtwebengine_dictionaries' 
    directory based on a defined base directory of the project. It ensures the 
    path is set dynamically to accommodate variations in installation 
    environments.

    Raises:
        FileNotFoundError: If the constructed path does not exist on the 
        filesystem.
        Exception: For unspecified exceptions related to environment variable setting.

    No returns and no arguments.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dictionaries_path = os.path.join(project_root, '.venv', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages', 'PyQt6', 'Qt6', 'libexec', 'qtwebengine_dictionaries') # pylint: disable=line-too-long

    if not os.path.exists(dictionaries_path):
        raise FileNotFoundError(f"The specified path does not exist: {dictionaries_path}")

    os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = dictionaries_path

try:
    set_qtwebengine_dictionaries_path()
except Exception as e: # pylint: disable=broad-except
    print(f"An error occurred: {e}")


def main():
    """
    Main script entry point.

    This function serves as the entry point for the script. It takes no 
    arguments, returns nothing. It is intended to be called when the script is 
    executed directly. This function creates the QApplication, initializes the 
    main window, and starts the event loop.

    Args:
        None.

    Returns:
        None.
    """

    app = QApplication(sys.argv)  # Create an instance of QApplication

    main_window = MainWindow()  # Create an instance of the main window
    main_window.show()  # Show the main window

    sys.exit(app.exec())  # Start the event loop and exit when it's finished


if __name__ == "__main__":
    main()
