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
