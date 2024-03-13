#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import engine, Session, Base
from src.models.fmp.stock import StockSymbol, CompanyProfile, DailyChartEOD # pylint: disable=unused-import
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

    # Converting in hypertable (TimeScaleDB)
    hypertable_candidates = ['dailychart', 'dividend']
    for table in hypertable_candidates:
        convert_stock_table_to_hypertable(table)

    # Completing tables with FMP data
    db_session = Session()
    stock_service = StockService(db_session)

    # stock_service.fetch_stock_symbols()
    # stock_service.fetch_company_profiles_for_exchange("Lisbon")
    symbols = ['AAPL', 'MSFT']
    for symbol in symbols:
        stock_service.fetch_daily_chart_for_period(symbol, "1990-01-01", "1995-01-01")
        stock_service.fetch_historical_dividend(symbol)


if __name__ == "__main__":
    main()
