#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

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
