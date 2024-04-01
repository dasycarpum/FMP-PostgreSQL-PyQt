#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import Session
from src.dal.fmp.database_query import StockQuery
# from src.business_logic.fmp.database_reporting import StockReporting

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

    stock_query = StockQuery(db_session)
    result = stock_query.get_table_performance('keymetrics')
    print(result)

    # stock_reporting = StockReporting(db_session)
    # stock_reporting.report_keymetrics_table()


if __name__ == "__main__":
    main()
