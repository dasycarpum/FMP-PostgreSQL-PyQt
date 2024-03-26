#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-25

@author: Roland VANDE MAELE

@abstract: this additional level of abstraction means that data can be 
manipulated and business operations performed without direct concern for the 
implementation details of data retrieval or database interaction.

"""

from sqlalchemy.exc import SQLAlchemyError
from src.models.base import Session
from src.dal.fmp.database_query import StockQuery
from src.services import plot


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
        Generates and saves visual reports for stock symbols categorized by 'exchange' and 'type_'.

        This method iterates over specified columns ('exchange' and 'type_') to 
        generate reports on stock symbols. For each category, it queries the 
        database using the StockQuery class and its method 
        get_stocksymbols_by_column, ensuring any missing values are replaced 
        with 'Unknown'. Depending on the category, it either generates a 
        horizontal bar chart or a treemap to visualize the distribution of 
        stock symbols.

        Attributes:
            Uses an instance attribute `db_session` for database queries, which 
            must be initialized with a valid database session before calling this method.

        Args:
            None

        Returns:
            None

        Raises:
            RuntimeError: If there's a database error or unexpected error during the update process.

        """
        try:
            stock_query = StockQuery(self.db_session)

            columns = ['exchange', 'type_']

            for column in columns:
                df = stock_query.get_stocksymbols_by_column(column)

                # Fill missing 'exchange' values with 'Unknown'
                df[column] = df[column].fillna('Unknown')

                # Calculate the total number of symbols
                sum_symbols = df['count_symbols'].sum()
                title = f"Number of symbols per {column} (Total = {str(sum_symbols)})"

                # Generate and save the plot
                if column == columns[0]:
                    plot.plot_horizontal_barchart(df, 'count_symbols', column, title)
                else:
                    plot.plot_treemap(df[['count_symbols', column]], title)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report stocksymbol table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report stocksymbol table due to an unexpected error: {e}") from e

    def report_companyprofile_table(self) -> None:
        """
        Generates and saves visual reports for company profiles categorized by 
        'currency', 'sector' and 'country'

        This method iterates over specified columns to generate reports on 
        stock ids. For each category, it queries the database using the 
        StockQuery class and its method get_companyprofiles_by_column, ensuring 
        any missing values are replaced with 'Unknown'. It generates a 
        horizontal bar chart to visualize the distribution of stock ids.

        Attributes:
            Uses an instance attribute `db_session` for database queries, which 
            must be initialized with a valid database session before calling this method.

        Args:
            None

        Returns:
            None

        Raises:
            RuntimeError: If there's a database error or unexpected error during the update process.

        """
        try:
            stock_query = StockQuery(self.db_session)

            columns = ['currency', 'sector', 'country']

            for column in columns:
                df = stock_query.get_companyprofiles_by_column(column)

                # Fill missing 'exchange' values with 'Unknown'
                df[column] = df[column].fillna('Unknown')

                # Calculate the total number of symbols
                sum_symbols = df['count_stock_ids'].sum()
                title = f"Number of stock ids per {column} (Total = {str(sum_symbols)})"

                # Generate and save the plot
                plot.plot_horizontal_barchart(df, 'count_stock_ids', column, title)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report companyprofile table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report companyprofile table due to an unexpected error: {e}") from e
