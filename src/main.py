#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import Session
from src.models.fmp.stock import StockSymbol, CompanyProfile, STOXXEurope600 # pylint: disable=unused-import
from src.business_logic.fmp.database_process import StockService


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
    stock_service = StockService(db_session)

    stock_service.fetch_daily_charts_by_period()
    # stock_service.fetch_daily_chart_for_period('TTE.PA', '2014-12-31', '2015-01-30')

if __name__ == "__main__":
    main()
