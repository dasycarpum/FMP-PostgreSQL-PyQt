#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import engine, Session, Base
from src.models.fmp.stock import StockSymbol, CompanyProfile # pylint: disable=unused-import
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

    # Creating tables for imported models
    Base.metadata.create_all(engine)

    # Completing tables with FMP data
    db_session = Session()
    stock_service = StockService(db_session)

    # stock_service.fetch_stock_symbols()
    stock_service.fetch_company_profiles_for_exchange("Lisbon")


if __name__ == "__main__":
    main()
