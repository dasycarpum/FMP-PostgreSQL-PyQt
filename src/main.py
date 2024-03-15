#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import Session
from src.models.fmp.stock import StockSymbol, CompanyProfile, DailyChartEOD # pylint: disable=unused-import
from src.dal.fmp.database_query import StockQuery
from src.business_logic.fmp.data_analytics import   clean_data_for_company_profiles_clustering
from src.services.plot import plot_boxplots, plot_distributions

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

    # Extracting stock data from company profiles table
    data = stock_query.extract_data_for_company_profiles_clustering()

    # Cleaning the data and converting to dataframe
    df = clean_data_for_company_profiles_clustering(data)

    # Outliers management
    variables = ['beta', 'vol_avg', 'mkt_cap']
    plot_boxplots(df, variables)
    plot_distributions(df, variables)


if __name__ == "__main__":
    main()
