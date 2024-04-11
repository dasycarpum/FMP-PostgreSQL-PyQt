#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-25

@author: Roland VANDE MAELE

@abstract: this additional level of abstraction means that data can be 
manipulated and business operations performed without direct concern for the 
implementation details of data retrieval or database interaction.

"""

import pandas as pd
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
        self.stock_query = StockQuery(self.db_session)
        self.table_list = self.stock_query.get_list_of_tables()

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
            columns = ['exchange', 'type_']

            for column in columns:
                df = self.stock_query.get_stocksymbols_by_column(column)

                # Fill missing 'exchange' values with 'Unknown'
                df[column] = df[column].fillna('Unknown')

                # Calculate the total number of symbols
                sum_symbols = df['count_symbols'].sum()
                title = f"Number of symbols per {column} (Total = {str(sum_symbols)})"

                # Generate and save the plot
                if column == columns[0]:
                    plot.plot_horizontal_barchart(df, 'count_symbols', column, title)
                else:
                    plot.plot_treemap(df[[column, 'count_symbols']], title)

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
            columns = ['currency', 'sector', 'country']

            for column in columns:
                df = self.stock_query.get_companyprofiles_by_column(column)

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

    def report_sxxp_table(self) -> None:
        """
        Generates various plots to report on the STOXX Europe 600 index by 
        querying the company profile data.

        This method retrieves data related to the STOXX Europe 600 index from 
        the database, focusing on company profiles. It visualizes this data 
        through several plots:
        - Distribution plots for beta, vol_avg (average volume), and mkt_cap 
        (market capitalization).
        - A treemap showing the number of stocks per currency.
        - Another treemap displaying the number of stocks per sector.
        - A horizontal bar chart indicating the number of stocks per country.
        - A table showing counts of boolean values like is_etf, 
        is_actively_trading, is_adr, and is_fund.

        Attributes:
            Uses an instance attribute `db_session` for database queries, which 
            must be initialized with a valid database session before calling this method.

        Args:
            None

        Returns:
            None

        Raises:
            RuntimeError: If there is a database-related error during the query 
            execution, encapsulating the original SQLAlchemyError. Also raised 
            if there is any other unexpected error during the execution of this 
            method, with details of the caught exception.

        """
        try:
            # Retrieve DataFrame with STOXX Europe 600 index company profiles.
            df = self.stock_query.get_sxxp_by_company_profile()

            # Plotting distributions of beta, vol_avg, and mkt_cap for the retrieved companies.
            plot.plot_distributions(df, ['beta', 'vol_avg', 'mkt_cap'],
            "STOXX Europe 600 index : distributions of 3 variables")

            # Creating and plotting a treemap of the number of stocks per currency.
            df_currency = df['currency'].value_counts(sort=True).reset_index()
            plot.plot_treemap(df_currency, "STOXX Europe 600 index : number of stocks per currency")

            # Creating and plotting a treemap of the number of stocks per sector.
            df_sector = df['sector'].value_counts(sort=True).reset_index()
            plot.plot_treemap(df_sector, "STOXX Europe 600 index : number of stocks per sector")

            # Sorting the count of stocks per country and plotting a horizontal bar chart.
            df_country = df['country'].value_counts().reset_index().sort_values(
                by='count', ascending=True)
            plot.plot_horizontal_barchart(
                df_country, 'count', 'country',
                "STOXX Europe 600 index : number of stocks per country")

            # Counting boolean values and preparing a DataFrame for plotting.
            df_bool = df[['is_etf', 'is_actively_trading',
                          'is_adr', 'is_fund']].apply(pd.Series.value_counts)
            print(df_bool)
            print(df[~df['is_actively_trading']])
            print(df[df['is_fund']])

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report sxxp table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report sxxp table due to an unexpected error: {e}") from e

    def report_dailychart_table(self) -> None:
        """
        Reports on the status of daily chart data in the database for various stocks.

        This function performs a series of data retrieval and processing tasks 
        to generate reports on the completeness and quality of daily chart 
        data. It checks for stocks that haven't been updated to the latest 
        date, identifies stocks with missing values in critical fields, and 
        detects any gaps in the daily chart records over the last year for a 
        specified stock.

        Attributes:
            Uses an instance attribute `db_session` for database queries, which 
            must be initialized with a valid database session before calling this method.

        Args:
            None

        Returns:
            None
        
        Raises:
            RuntimeError: If any database error occurs, wrapping the original
            SQLAlchemyError, or for any unexpected error during the reporting process.

        """
        try:
            # Retrieves a list of stock_ids that have not been updated to the latest date
            df_update = self.stock_query.get_dailychart_missing_update()
            print(df_update)

            # Retrieves a list of stock_ids which has at least one null value in the columns
            df_zero = pd.DataFrame()
            columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume',
                       'unadjusted_volume', 'vwap']

            for column in columns:
                df = self.stock_query.get_table_missing_value_by_column('dailychart', column)
                df['column_name'] = column
                df_zero = pd.concat([df_zero, df], ignore_index=True)

            print(df_zero)

            df_zero_by_stock = df_zero[df_zero['is_actively_trading']
            ].groupby('stock_id')['zero_column_count'].sum().reset_index()
            print(df_zero_by_stock.sort_values('zero_column_count'))
            plot.plot_distributions(df_zero_by_stock, ['zero_column_count'])

            df_zero_by_column = df_zero[df_zero['is_actively_trading']
            ].groupby('column_name')['zero_column_count'].sum().reset_index()
            print(df_zero_by_column.sort_values('zero_column_count'))

            # Retrieves dates within the last year for which there are no daily
            # chart records for the specified stock
            df_gap = self.stock_query.get_dailychart_finding_gap_by_stock(21412)
            print(df_gap)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report dailychart table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report dailychart table due to an unexpected error: {e}") from e

    def report_dividend_table(self) -> None:
        """
        Reports on the status of dividend data in the database for various stocks.

        This function performs a series of data retrieval and processing tasks 
        to generate reports on the completeness and quality of dividend data. 
        It identifies stocks with missing values in critical fields

        Attributes:
            Uses an instance attribute `db_session` for database queries, which 
            must be initialized with a valid database session before calling this method.

        Args:
            None

        Returns:
            None
        
        Raises:
            RuntimeError: If any database error occurs, wrapping the original
            SQLAlchemyError, or for any unexpected error during the reporting process.

        """
        try:
            # Retrieves a list of stock_ids which has at least one null value in the columns
            df_zero = pd.DataFrame()
            columns = ['adj_dividend', 'dividend']

            for column in columns:
                df = self.stock_query.get_table_missing_value_by_column('dividend', column)
                df['column_name'] = column
                df_zero = pd.concat([df_zero, df], ignore_index=True)

            print(df_zero)

            df_zero_by_stock = df_zero[df_zero['is_actively_trading']
            ].groupby('stock_id')['zero_column_count'].sum().reset_index()
            print(df_zero_by_stock.sort_values('zero_column_count'))

            df_zero_by_column = df_zero[df_zero['is_actively_trading']
            ].groupby('column_name')['zero_column_count'].sum().reset_index()
            print(df_zero_by_column.sort_values('zero_column_count'))

            # Retrieves the most recent date by stock_id
            df_max_date = self.stock_query.get_table_date('dividend')
            plot.plot_distributions(df_max_date, ['max_date'])

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report dividend table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report dividend table due to an unexpected error: {e}") from e

    def report_keymetrics_table(self) -> None:
        """
        Reports on the status of key metrics data in the database for various stocks.

        This function performs a series of data retrieval and processing tasks 
        to generate reports on the completeness and quality of key metrics 
        data. It identifies stocks with missing values in critical fields

        Attributes:
            Uses an instance attribute `db_session` for database queries, which 
            must be initialized with a valid database session before calling this method.

        Args:
            None

        Returns:
            None
        
        Raises:
            RuntimeError: If any database error occurs, wrapping the original
            SQLAlchemyError, or for any unexpected error during the reporting process.

        """
        try:
            # Retrieves a list of stock_ids which has at least one null value in the columns
            df_zero = pd.DataFrame()

            columns = self.stock_query.get_keymetrics_columns()

            for column in columns[5:]:
                df = self.stock_query.get_table_missing_value_by_column('keymetrics', column)
                df['column_name'] = column
                df_zero = pd.concat([df_zero, df], ignore_index=True)
            print(df_zero.sort_values('is_actively_trading'))

            df_zero = df_zero.dropna(subset=['is_actively_trading'])

            df_zero_by_stock = df_zero[df_zero['is_actively_trading']
            ].groupby('stock_id')['zero_column_count'].sum().reset_index()
            print(df_zero_by_stock.sort_values('zero_column_count'))
            plot.plot_distributions(df_zero_by_stock, ['zero_column_count'])

            df_zero_by_column = df_zero[df_zero['is_actively_trading']
            ].groupby('column_name')['zero_column_count'].sum().reset_index()
            print(df_zero_by_column.sort_values('zero_column_count'))

            # Retrieves the most recent date by stock_id
            df_max_date = self.stock_query.get_table_date('keymetrics')
            plot.plot_distributions(df_max_date, ['max_date'])

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report keymetrics table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report keymetrics table due to an unexpected error: {e}") from e

    def report_on_tables_performance(self):
        """
        Generates a performance report for each table in the database by 
        iterating over all tables and returns a list of tuples with the performance metrics.

        The performance metrics for each table include execution time of a 
        SELECT query and the disk space used by the table, both printed to the 
        standard output.

        Args:
            None

        Returns:
            List[Tuple[datetime, str, bool, float, str]]: A list of tuples, 
            each containing the timestamp, table name, TimescaleDB hypertable 
            or not, execution time in seconds, and disk space used by the table 
            in bytes.

        Raises:
            RuntimeError: If any SQLAlchemy database operation fails, a 
            RuntimeError is raised with details of the database-related error. 
            Additionally, if any other unexpected error occurs, it is also 
            caught and raised as a RuntimeError with an appropriate error 
            message.

        """
        try:
            performance_data = []

            for table in self.table_list:
                result = self.stock_query.get_table_performance(table)
                performance_data.append(result)

            return performance_data

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report on table performance due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report on table performance due to an unexpected error: {e}") from e
