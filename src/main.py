#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import Session
from src.models.fmp.stock import StockSymbol, CompanyProfile, STOXXEurope600 # pylint: disable=unused-import
from src.dal.fmp.database_query import StockQuery


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

    stock_list = stock_query.extract_list_of_symbols_from_sxxp()

    print(stock_list[:5])
    print(len(stock_list))

if __name__ == "__main__":
    main()
