#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-11

@author: Roland VANDE MAELE

@abstract: this function attempts to parse a string into a date.

"""

from datetime import datetime

def parse_date(date_str):
    """
    Attempts to convert a string into a date object according to several formats.

    This function attempts to parse the given string (`date_str`) using several
    date formats. If the string can be correctly converted to a date in one of 
    the formats, the function returns the corresponding date object. If no 
    format matches, or if another error occurs error occurs, the function 
    returns `None`.

    Args:
        date_str (str): The string representing the date to be parsed.

    Returns:
        datetime.date | None: The date object resulting from successful 
        parsing, or `None` if parsing fails.

    Examples:
        >>> parse_date("2023-03-11")
        datetime.date(2023, 3, 11)
        >>> parse_date("11/03/2023")
        datetime.date(2023, 3, 11)
        >>> parse_date("not a date")
        None

    Note:
        Currently supported date formats are "%Y-%m-%d" (e.g. "2023-03-11") and 
        "%d/%m/%Y" (e.g. "11/03/2023").

    """
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None
