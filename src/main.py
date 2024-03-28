#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.services.date import create_business_time_series


def main():
    """
    Main script entry point.

    This function serves as the entry point for the script. It takes no 
    arguments, returns nothing. It is intended to be called when the script is 
    executed directly.

    Args:
        None.

    Returns:
        None.
    
    Raises:
        No exception is raised by this function.
    """


    create_business_time_series()


if __name__ == "__main__":
    main()
