#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import engine, Session, Base
from src.models.fmp.stock import StockSymbol, CompanyProfile, STOXXEurope600 # pylint: disable=unused-import
from src.business_logic.fmp.database_process import StockService
from src.services.sql import convert_stock_table_to_hypertable


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

    # Hypertable (TimeScaleDB)
    convert_stock_table_to_hypertable('sxxp')

    db_session = Session()
    stock_service = StockService(db_session)

    stock_service.fetch_sxxp_historical_components('20240301')


if __name__ == "__main__":
    main()
