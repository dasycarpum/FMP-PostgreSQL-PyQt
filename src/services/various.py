#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-18

@author: Roland VANDE MAELE

@abstract: various assistance functions.

"""

from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox


def safe_convert_to_int(value, default=0):
    """
    Safely converts a value to an integer, returning a default value if the conversion fails.

    Args:
        value: The value to be converted to integer.
        default (int): The value to return if conversion fails. The default is 0.

    Returns:
        int: The value converted to integer, or the default value if conversion fails.

    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def generate_dividend_signature(stock_id: int, dividend_date: str,
    dividend_amount: float) -> str:
    """
    Generates a signature string for a stock's dividend event.

    This function creates a signature string that uniquely identifies a 
    dividend event for a given stock. The signature is composed of the stock's 
    ID, the date of the dividend, and the amount of the dividend.

    Args:
        stock_id (int): The ID of the stock. Must be an integer.
        dividend_date (str): The date of the dividend. Expected to be a string 
        in the format "YYYY-MM-DD", but not strictly enforced by this function.
        dividend_amount (int, float): The amount of the dividend. Can be an integer or a float.

    Returns:
        str: A signature string in the format "{stock_id}-{dividend_date}-{dividend_amount}".

    Raises:
        RuntimeError: If the `stock_id` is not an integer, or if the 
        `dividend_amount` is neither an integer nor a float, a `ValueError` is 
        raised and caught within the function. Additionally, if any unexpected 
        exception occurs during the execution of the function, it is caught and 
        a `RuntimeError` is raised with a message indicating that an unexpected 
        error occurred.

    Examples:
        >>> generate_dividend_signature(123, "2023-04-01", 1.5)
        '123-2023-04-01-1.5'

        >>> generate_dividend_signature("AAPL", "2023-04-01", "2.0")
        RuntimeError: Stock ID must be an integer and dividend amount must be an integer or float.
    """
    try:

        if not isinstance(stock_id, int) or not isinstance(dividend_amount, (int, float)):
            raise ValueError(
                "Stock ID must be an integer and dividend amount must be an integer or float.")

        # Creation of the chain representing the dividend event
        signature = f"{stock_id}-{dividend_date}-{dividend_amount}"

        return signature

    except ValueError as e:
        # Handling errors related to inappropriate values
        raise RuntimeError(e) from e

    except Exception as e:
        # Handling any other unexpected errors
        raise RuntimeError(f"An unexpected error occurred: {e}") from e


class CheckableComboBox(QComboBox):
    """
    A subclass of QComboBox that allows items within the dropdown to be checkable.
    
    Attributes:
        None explicitly set beyond base class defaults.
    """
    def __init__(self, parent=None):
        """
        Initializes the combo box with a standard item model supporting checkable items.
        
        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super(CheckableComboBox, self).__init__(parent)
        self.setModel(QStandardItemModel(self))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def add_check_item(self, item_text, is_checked=False):
        """
        Adds a checkable item to the combo box with optional initial checked state.
        
        Args:
            item_text (str): The text label for the new item.
            is_checked (bool, optional): Initial check state of the item. Defaults to False.
        """
        item = QStandardItem(item_text)
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        check_state = Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked
        item.setData(check_state, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)

    def checked_items(self):
        """
        Returns a list of the text labels of all checked items in the combo box.
        
        Returns:
            list of str: The text labels of checked items.
        """
        checked_items = []
        for index in range(self.model().rowCount()):
            item = self.model().item(index)
            if item.checkState() == Qt.CheckState.Checked:
                checked_items.append(item.text())
        return checked_items
