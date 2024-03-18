#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-18

@author: Roland VANDE MAELE

@abstract: various assistance functions.

"""

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
