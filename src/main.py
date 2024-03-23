#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import Session
from src.models.fmp.stock import StockSymbol, CompanyProfile, STOXXEurope600 # pylint: disable=unused-import
from src.dal.fmp.database_operation import StockManager


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

    db_session = Session()
    stock_manager = StockManager(db_session)

    stock_manager.update_daily_chart_adj_close_for_dividend(21395, '2024-03-19', 0.74)


if __name__ == "__main__":
    main()
