#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-25

@author: Roland VANDE MAELE

@abstract: this additional level of abstraction means that data can be 
manipulated and business operations performed without direct concern for the 
implementation details of data retrieval or database interaction.

"""

from src.models.base import Session
from src.dal.fmp.database_query import StockQuery
from src.services.plot import plot_horizontal_barchart

class StockReporting:
    """Reporting class for analytical tables of stock market databases."""

    def __init__(self, db_session: Session):
        """
        Initializes the StockReporting with a database session.
        
        Args:
            db_session (Session): The database session for performing operations.
        """
        self.db_session = db_session

    def report_stocksymbol_table(self) -> None:
        """
        Generates a report on stock symbols per exchange and plots a horizontal bar chart.

        This method queries the stock symbols by exchange from the database 
        using a predefined query class (StockQuery) and its method 
        (get_stocksymbols_by_exchange). It then prepares the data for 
        visualization by replacing any missing 'exchange' values with 
        'Unknown'. After preparing the data, it calculates the total number of 
        symbols across all exchanges. This total is included in the title of 
        the horizontal bar chart to provide a comprehensive overview of the 
        data. Finally, it utilizes the 'plot_horizontal_barchart' function to 
        generate and save a horizontal bar chart visualization of the number of 
        symbols per exchange, highlighting the distribution of symbols across 
        different exchanges.

        Attributes:
            - Uses an instance of StockQuery for querying the database, which 
            requires a database session (self.db_session) to be passed at 
            initialization.

        Args:
            None

        Returns:
            None

        """
        stock_query = StockQuery(self.db_session)

        df = stock_query.get_stocksymbols_by_exchange()

        # Fill missing 'exchange' values with 'Unknown'
        df['exchange'] = df['exchange'].fillna('Unknown')

        # Calculate the total number of symbols
        sum_symbols = df['count_symbols'].sum()
        title = f"Number of Symbols per Exchange (Total = {str(sum_symbols)})"

        # Generate and save the horizontal bar chart
        plot_horizontal_barchart(df, 'count_symbols', 'exchange', title)
    