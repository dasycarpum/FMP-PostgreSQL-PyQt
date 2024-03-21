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

    stock_symbol_query = stock_query.extract_list_of_symbols_from_sxxp()

    symbols_ids = {symbol[0]:symbol[1] for symbol in stock_symbol_query}
    print(dict(list(symbols_ids.items())[:5]))


if __name__ == "__main__":
    main()
