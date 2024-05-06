#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-25

@author: Roland VANDE MAELE

@abstract: this additional level of abstraction means that data can be 
manipulated and business operations performed without direct concern for the 
implementation details of data retrieval or database interaction.

"""

from datetime import datetime
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from PyQt6.QtWidgets import QTableWidget
from src.models.base import Session
from src.dal.fmp.database_query import StockQuery
from src.services import plot
pd.set_option('future.no_silent_downcasting', True)


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

    def report_stocksymbol_table(self, reports: dict) -> None:
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
            reports (dict): A dictionary where the key is the name of the topic 
            report, and the value a MplWidget to display the topic's plot.

        Returns:
            None

        Raises:
            RuntimeError: If there's a database error or unexpected error during the update process.

        """
        try:
            for column, mpl_widget in reports.items():

                # Data query
                df = self.stock_query.get_stocksymbols_by_column(column)

                # Fill missing values with 'Unknown'
                df[column] = df[column].fillna('Unknown')

                # Calculate the total number of symbols and edit title
                sum_ = df['count_symbols'].sum()
                title = f"Stock symbols : number / {column} - Total = {str(sum_)}"

                # Plotting
                canvas = mpl_widget.canvas
                if column == "exchange":
                    plot.plot_horizontal_barchart_widget(
                        canvas, df, 'count_symbols', column, title)
                elif column == "type_":
                    plot.plot_treemap_widget(
                        canvas, df[[column, 'count_symbols']], title)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report stocksymbol table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report stocksymbol table due to an unexpected error: {e}") from e

    def report_companyprofile_table(self, reports: dict) -> None:
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
            reports (dict): A dictionary where the key is the name of the topic 
            report, and the value a MplWidget to display the topic's plot.

        Returns:
            None

        Raises:
            RuntimeError: If there's a database error or unexpected error during the update process.

        """
        try:
            for column, mpl_widget in reports.items():
                # Data query
                df = self.stock_query.get_companyprofiles_by_column(column)

                # Fill missing values with 'Unknown'
                df[column] = df[column].fillna('Unknown')

                # Calculate the total number of stock ids and edit title
                sum_ = df['count_stock_ids'].sum()
                title = f"Company profiles : number / {column} - Total = {str(sum_)}"

                # Plotting
                canvas = mpl_widget.canvas
                plot.plot_horizontal_barchart_widget(
                    canvas, df, 'count_stock_ids', column, title)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report companyprofile table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report companyprofile table due to an unexpected error: {e}") from e

    def report_sxxp_table(self, reports: dict) -> None:
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
            reports (dict): A dictionary where the key is the name of the topic 
            report, and the value a MplWidget to display the topic's plot.

        Returns:
            None

        Raises:
            RuntimeError: If there is a database-related error during the query 
            execution, encapsulating the original SQLAlchemyError. Also raised 
            if there is any other unexpected error during the execution of this 
            method, with details of the caught exception.

        """
        try:
            # Data query
            df = self.stock_query.get_sxxp_by_company_profile()

            # Calculate the total number of stock ids
            sum_ = df.shape[0]

            # Plotting
            for topic, mpl_widget in reports.items():

                title = (
                    f"STOXX Europe 600 components : number / {topic.lower()} - Total = {str(sum_)}")

                canvas = mpl_widget.canvas
                if topic == "Metric":
                    plot.plot_distributions_widget(
                        canvas, df, ['beta', 'vol_avg', 'mkt_cap'],
                        "STOXX Europe 600 components : distribution of 3 economic variables")
                elif topic == "Currency":
                    df_currency = df['currency'].value_counts(sort=True).reset_index()
                    plot.plot_treemap_widget(canvas, df_currency, title)
                elif topic == "Sector":
                    df_sector = df['sector'].value_counts(sort=True).reset_index()
                    plot.plot_treemap_widget(canvas, df_sector, title)
                elif topic == "Country":
                    df_country = df['country'].value_counts().reset_index().sort_values(
                        by='count', ascending=True)
                    plot.plot_horizontal_barchart_widget(canvas, df_country,
                    'count', 'country', title)
                elif topic == "Type":
                    df_bool = df[['is_etf', 'is_actively_trading',
                                'is_adr', 'is_fund']].apply(pd.Series.value_counts)
                    plot.plot_grouped_barchart_widget(canvas, df_bool, title)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report sxxp table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report sxxp table due to an unexpected error: {e}") from e

    def report_dailychart_table(self, reports: dict) -> None:
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
            reports (dict): A dictionary where the key is the name of the topic 
            report, and the value a MplWidget to display the topic's plot.

        Returns:
            None
        
        Raises:
            RuntimeError: If any database error occurs, wrapping the original
            SQLAlchemyError, or for any unexpected error during the reporting process.

        """
        try:
            # Data query 1
            df_update = self.stock_query.get_dailychart_missing_update()

            # Data qyery 2
            df_zero = pd.DataFrame()
            columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume',
                       'unadjusted_volume', 'vwap']

            for column in columns:
                df = self.stock_query.get_table_missing_value_by_column('dailychart', column)
                df['column_name'] = column
                df_zero = pd.concat([df_zero, df], ignore_index=True)

            df_zero['is_actively_trading'] = df_zero[
                'is_actively_trading'].fillna(False).astype(bool)

            df_zero_by_stock = df_zero[df_zero[
                'is_actively_trading']].groupby('stock_id')['zero_column_count'].sum().reset_index().sort_values('zero_column_count', ascending=False) # pylint: disable=line-too-long

            df_zero_by_column = df_zero[df_zero['is_actively_trading']
            ].groupby('column_name')['zero_column_count'].sum().reset_index().sort_values('zero_column_count', ascending=False) # pylint: disable=line-too-long

            # Plotting
            for topic, widget in reports.items():
                if topic == "NaN -> Plot":
                    canvas = widget.canvas
                    plot.plot_distributions_widget(canvas, df_zero_by_stock,
                        ['zero_column_count'],
                        "Daily chart : distribution of null values / stock")
                elif topic == "Missing update -> Table":
                    plot.populate_tablewidget_with_df(widget, df_update)
                elif topic == "NaN by stock -> Table":
                    plot.populate_tablewidget_with_df(widget, df_zero_by_stock)
                elif topic == "NaN by column -> Table":
                    plot.populate_tablewidget_with_df(widget, df_zero_by_column)

            # Data query 3
            df_gap = self.stock_query.get_dailychart_finding_gap_by_stock(21412)
            print(df_gap)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report dailychart table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report dailychart table due to an unexpected error: {e}") from e

    def report_dividend_table(self, reports: dict) -> None:
        """
        Reports on the status of dividend data in the database for various stocks.

        This function performs a series of data retrieval and processing tasks 
        to generate reports on the completeness and quality of dividend data. 
        It identifies stocks with missing values in critical fields

        Attributes:
            Uses an instance attribute `db_session` for database queries, which 
            must be initialized with a valid database session before calling this method.

        Args:
            reports (dict): A dictionary where the key is the name of the topic 
            report, and the value a MplWidget to display the topic's plot.

        Returns:
            None
        
        Raises:
            RuntimeError: If any database error occurs, wrapping the original
            SQLAlchemyError, or for any unexpected error during the reporting process.

        """
        try:
            # Data query 1
            df_zero = pd.DataFrame()
            columns = ['adj_dividend', 'dividend']

            for column in columns:
                df = self.stock_query.get_table_missing_value_by_column('dividend', column)
                df['column_name'] = column
                df_zero = pd.concat([df_zero, df], ignore_index=True)

            df_zero_by_stock = df_zero[df_zero['is_actively_trading']
            ].groupby('stock_id')['zero_column_count'].sum().reset_index().sort_values('zero_column_count', ascending=False) # pylint: disable=line-too-long

            df_zero_by_column = df_zero[df_zero['is_actively_trading']
            ].groupby('column_name')['zero_column_count'].sum().reset_index().sort_values('zero_column_count', ascending=False) # pylint: disable=line-too-long

            # Data query 2
            df = self.stock_query.get_table_date('dividend')
            sum_ = df.shape[0]

            # Plotting
            for topic, widget in reports.items():
                if topic == "Latest dates -> Plot":
                    canvas = widget.canvas
                    plot.plot_distributions_widget(canvas, df, ['max_date'],
                        f"Dividend : distribution of latest payment date - Total = {sum_}")
                elif topic == "NaN by stock -> Table":
                    plot.populate_tablewidget_with_df(widget, df_zero_by_stock)
                elif topic == "NaN by column -> Table":
                    plot.populate_tablewidget_with_df(widget, df_zero_by_column)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to report dividend table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to report dividend table due to an unexpected error: {e}") from e

    def report_keymetrics_table(self, reports: dict) -> None:
        """
        Reports on the status of key metrics data in the database for various stocks.

        This function performs a series of data retrieval and processing tasks 
        to generate reports on the completeness and quality of key metrics 
        data. It identifies stocks with missing values in critical fields

        Attributes:
            Uses an instance attribute `db_session` for database queries, which 
            must be initialized with a valid database session before calling this method.

        Args:
            reports (dict): A dictionary where the key is the name of the topic 
            report, and the value a MplWidget to display the topic's plot.

        Returns:
            None
        
        Raises:
            RuntimeError: If any database error occurs, wrapping the original
            SQLAlchemyError, or for any unexpected error during the reporting process.

        """
        try:
            # Data query
            df_zero = pd.DataFrame()

            columns = self.stock_query.get_keymetrics_columns()

            for column in columns[5:]:
                df = self.stock_query.get_table_missing_value_by_column('keymetrics', column)
                df['column_name'] = column
                df_zero = pd.concat([df_zero, df], ignore_index=True)

            df_zero = df_zero.dropna(subset=['is_actively_trading'])

            df_zero_by_column = df_zero[df_zero['is_actively_trading']
            ].groupby('column_name')['zero_column_count'].sum().reset_index().sort_values('zero_column_count', ascending=False) # pylint: disable=line-too-long

            df_zero_by_stock = df_zero[df_zero['is_actively_trading']
            ].groupby('stock_id')['zero_column_count'].sum().reset_index().sort_values('zero_column_count', ascending=False) # pylint: disable=line-too-long

            # Data query 2
            df = self.stock_query.get_table_date('keymetrics')
            sum_ = df.shape[0]

            # Plotting
            for topic, widget in reports.items():
                if topic == "Latest dates -> Plot":
                    canvas = widget.canvas
                    plot.plot_distributions_widget(canvas, df, ['max_date'],
                        f"Key metrics : distribution of latest publication date - Total = {sum_}")
                elif topic == "NaN -> Plot":
                    canvas = widget.canvas
                    plot.plot_distributions_widget(canvas, df_zero_by_stock,
                        ['zero_column_count'],
                        "Key metrics : distribution of null values / stock")
                elif topic == "NaN by stock -> Table":
                    plot.populate_tablewidget_with_df(widget, df_zero_by_stock)
                elif topic == "NaN by column -> Table":
                    plot.populate_tablewidget_with_df(widget, df_zero_by_column)

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

    def get_sql_query_result(self, table_widget: QTableWidget, query_text: str) -> None:
        """
        Executes a given SQL query using a database interface, converts the 
        results to a DataFrame, and populates a specified QTableWidget with the 
        DataFrame.

        This function takes an SQL query as a string, executes it to fetch 
        data, and then uses this data to populate a QTableWidget using a helper 
        function. It handles both database-specific errors and other unexpected 
        errors by re-raising them as RuntimeError with appropriate messages.

        Args:
            table_widget (QTableWidget): The QTableWidget instance where the 
            results will be displayed.
            query_text (str): The SQL query string to be executed.

        Raises:
            RuntimeError: If the SQL query fails due to a database error or any 
            other unexpected error, encapsulating the original exception.

        """
        try:
            df_result = self.stock_query.fetch_sql_query_as_dataframe(query_text)

            plot.populate_tablewidget_with_df(table_widget, df_result)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to execute the SQL query due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to execute the SQL query due to an unexpected error: {e}") from e

    def get_stock_dictionary(self) -> dict[int, list[str]]:
        """
        Retrieves a dictionary of stock information.

        This function is a higher-level business logic function that fetches a 
        dictionary mapping stock ids to a list of attributes (name, symbol, 
        ISIN). It internally calls another method (`fetch_stock_dictionary`) 
        which handles the database query. The function abstracts away the 
        details of the database operation, providing a clean interface for 
        obtaining stock data.

        Returns:
            dict[int, list[str]]: A dictionary where each key is a stock id and 
            the value is a list containing the stock's name, symbol, and ISIN. 

        Raises:
            RuntimeError: If an error occurs during the SQL query execution, 
            either due to a database-specific error or an unexpected general 
            error.

        """
        try:
            stock_dict = self.stock_query.fetch_stock_dictionary()

            return stock_dict

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to create a stock dictionary due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to create a stock dictionary due to an unexpected error: {e}") from e

    def get_dailychart_data(self, stock_id: int, start_date: str) -> pd.DataFrame:
        """
        Retrieves daily chart data for a specified stock from a starting date.

        This function acts as a wrapper around `fetch_dailychart_data` method 
        of the `stock_query` attribute within the class. It handles any 
        database-related errors and general exceptions to provide a clear 
        error message to the caller. If successful, it returns the data as a 
        pandas DataFrame.

        Args:
            stock_id (int): The stock ID for which to retrieve daily chart data.
            start_date (str): The start date from which to begin fetching the 
            data, in a format that can be interpreted by the database.

        Returns:
            pd.DataFrame: A DataFrame containing daily chart data from the 
            specified start date for the given stock ID.

        Raises:
            RuntimeError: If there's a SQLAlchemy database-related error or an 
            unexpected exception during the operation, a runtime error is 
            raised with a detailed explanation.

        """
        try:
            df = self.stock_query.fetch_dailychart_data(stock_id, start_date)

            return df

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to get dailychart data due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to get dailychart data due to an unexpected error: {e}") from e

    def get_dividend_data(self, stock_id: int, period: int=10) -> pd.DataFrame:
        """
        Retrieves and processes dividend data for a given stock ID, summing 
        dividends annually over a specified period.

        This method fetches raw dividend data for the specified stock ID by 
        calling another method in the class that performs the SQL query. It 
        then processes this data by converting dates from strings to datetime 
        objects, extracting the year, and grouping the data by year and 
        stock_id to sum the dividends for each year. It ensures that data for 
        each year within the specified period is included, even if no dividends 
        were paid, by filling such years with zeros.

        Args:
            stock_id (int): The ID of the stock for which to retrieve and 
            process dividend data.
            period (int, optional): The number of years from the current year 
            backwards for which to calculate dividends. Defaults to 10 years.

        Returns:
            pd.DataFrame: A DataFrame with columns 'year', 'stock_id', and 
            'dividend'. The 'dividend' column contains the sum of dividends 
            paid each year, with years having no data filled with zero.

        Raises:
            RuntimeError: An error occurs during the database operation or 
            during the data processing steps, including database connectivity 
            issues, SQL errors, or unexpected issues during data manipulation 
            in pandas. The specific error message is included in the exception.

        """
        try:
            # Fetch dividend data for the specified stock_id
            df = self.stock_query.fetch_stock_data_from_table('dividend',stock_id)

            # Convert 'date' to datetime
            df['date'] = pd.to_datetime(df['date'])

            # Extract year from 'date'
            df['year'] = df['date'].dt.year

            # Calculate the current year and determine the start year for the last 10 years
            current_year = datetime.now().year
            start_year = current_year - period

            # Group by 'year' and 'stock_id', then sum 'dividend'
            annual_dividend_sum = df.groupby(['year', 'stock_id'])['dividend'].sum().reset_index()

            # Ensure all years in the last 10 years are represented in the DataFrame
            all_years = pd.DataFrame({'year': range(start_year, current_year + 1)})
            annual_dividend_sum = pd.merge(all_years, annual_dividend_sum, on='year', how='left')

            # Fill missing 'stock_id' and 'dividend' values
            annual_dividend_sum['stock_id'] = annual_dividend_sum['stock_id'].fillna(stock_id)
            annual_dividend_sum['dividend'] = annual_dividend_sum['dividend'].fillna(0)

            return annual_dividend_sum

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to get dividend data due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to get dividend data due to an unexpected error: {e}") from e

    def get_company_profile(self, stock_id: int) -> pd.DataFrame:
        """
        Retrieves the company profile for a given stock ID from the 
        'companyprofile' table in the database.

        This function fetches specific columns from the company profile data, 
        including currency, sector, country, IPO date, and description.

        Args:
            stock_id (int): The unique identifier of the stock for which the 
            company profile is to be retrieved.

        Returns:
            pd.DataFrame: A DataFrame containing the requested company profile 
            information.

        Raises:
            RuntimeError: If there is a database-related error (handled by 
            SQLAlchemyError) or another unexpected exception, a RuntimeError is 
            raised with a description of the error.

        """
        try:
            # Fetch company profile for the specified stock_id
            df = self.stock_query.fetch_stock_data_from_table('companyprofile',stock_id)

            return df[['currency', 'sector', 'country', 'ipo_date',
                     'description']]

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to get company profile due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to get company profile due to an unexpected error: {e}") from e

    def get_key_metric_data(self, stock_id: int, key_metrics: list[str],
        quarter: bool, nb_of_period: int=10) -> pd.DataFrame:
        """
        Retrieves and computes statistical metrics for specified financial key 
        metrics from the database for a given stock.

        This function fetches the stock data for the given `stock_id`, and 
        calculates various statistical metrics for the requested key metrics 
        over the specified number of periods.

        Args:
            stock_id (int): The ID of the stock for which the key metrics are to be fetched.
            key_metrics (list[str]): A list of strings specifying which key 
            metrics to fetch and compute statistics for.
            quarter (bool): A boolean flag to indicate whether the data should 
            be considered quarterly (True) or annually (False).
            nb_of_period (int, optional): The number of latest periods to 
            consider for the metrics. Defaults to 10.

        Returns:
            pd.DataFrame: A DataFrame containing statistical metrics for the 
            requested key metrics such as:
                - 'first date': the earliest date in the data
                - 'max': maximum value of each metric
                - 'min': minimum value of each metric
                - 'mean': mean of each metric
                - 'median': median of each metric
                - 'std': standard deviation of each metric
                - 'last date': the most recent date in the data
                - 'last value': the last recorded value of each metric

        Raises:
            RuntimeError: If there is a database-related error (handled by 
            SQLAlchemyError) or another unexpected exception, a RuntimeError is 
            raised with a description of the error.

        """
        try:
            # Fetch key metrics for the specified stock_id
            df_ = self.stock_query.fetch_stock_data_from_table('keymetrics',stock_id)

            # Select the period : quarter or annual
            if quarter:
                df_ = df_.loc[df_['period'] != 'FY']
            else:
                df_ = df_.loc[df_['period'] == 'FY']

            # Sort the DataFrame by date descending
            df_sorted = df_.sort_values(by='date', ascending=False)

            # Select the last x records
            df_last_ = df_sorted.head(nb_of_period)

            # Select only key metrics list, and set 'date' as the index
            df = df_last_.set_index('date')[key_metrics]

            # Calculating the statistics
            stats = pd.DataFrame({
                'first date': df.index.min(),
                'min': round(df.min(),3),
                'max': round(df.max(), 3),
                'mean': round(df.mean(),3),
                'median': round(df.median(), 3),
                'std' : round(df.std(), 3),
                'last date': df.index.max(),
                'last value' : round(df.iloc[0], 3)
            })

            return stats

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to get key metric data due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to get key metric data due to an unexpected error: {e}") from e

    def get_distinct_company_profiles(self) -> pd.DataFrame:
        """
        Retrieves a DataFrame containing the profiles of companies listed in 
        the STOXX Europe 600 index. This function queries the database for 
        company profile data, and returns the results directly as a DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the distinct profiles of 
            companies, including details such as company ID, sector, currency 
            and country.

        Raises:
            RuntimeError: An error encapsulating any exceptions thrown during 
            the execution, particularly database-related issues such as 
            connectivity or syntax errors in SQL queries, or other unexpected exceptions.

        """
        try:
            # Fetch STOXX Europe 600 index company profiles
            df = self.stock_query.fetch_companyprofile_data()

            return df

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to get distinct company profiles due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to get distinct company profiles due to an unexpected error: {e}") from e

    def get_sector_study_data(self, setting: dict) -> pd.DataFrame:
        """
        Retrieves and processes sector-specific study data based on 
        user-defined settings, such as period type and number of periods. This 
        function fetches the data from the database, filters it according to 
        the specified period ('quarterly' or 'annual'), and computes the median
        of the last three metrics for each stock symbol over the most recent 
        periods specified.

        Args:
            setting (dict): A dictionary containing the configuration for 
            fetching and processing the data:
                - period (str): The period type to filter the data. Values can 
                be 'quarter' for quarterly data excluding fiscal year (FY) or 
                'FY' for annual data.
                - nb_of_period (int): The number of recent periods to consider 
                for each stock symbol.
                - other keys : For fetching the data
        
        Returns:
            pd.DataFrame: A DataFrame where each row represents a stock symbol, 
            and columns include the symbol and the median values of the 3 
            metrics from the data fetched, processed, and grouped by the symbol.

        Raises:
            RuntimeError: An error encapsulating any exceptions thrown during 
            the execution, particularly database-related issues like 
            connectivity or syntax errors in SQL queries, or other unexpected exceptions.

        """
        try:
            # Fetch sector study data
            df = self.stock_query.fetch_sector_study_data(setting)

            # Select the period : quarter or annual
            if setting['period'] == 'quarter':
                df = df.loc[df['period'] != 'FY']
            else:
                df = df.loc[df['period'] == 'FY']

            # Function to sort by date and return the top x rows
            def get_top_recent(group):
                return group.sort_values(by='date', ascending=False).head(setting['nb_of_period'])

            # Apply the function to each symbol
            df_recent = df.groupby('symbol').apply(get_top_recent)
            df_recent.reset_index(drop=True, inplace=True)

            # Get the names of the last three columns
            last_3_columns = df_recent.columns[-3:]

            # Group by the 'symbol' column and calculate the median for the last three columns
            result_df = df_recent.groupby('symbol').agg(
                {col: 'median' for col in last_3_columns})

            # Resetting index if you want 'symbol' as a column and not an index
            result_df.reset_index(inplace=True)

            # Round only the floating point columns to 3 decimal places
            result_df[result_df.select_dtypes(include=['float']).columns] = result_df.select_dtypes(include=['float']).round(3) # pylint: disable=line-too-long

            return result_df

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to get sector study data due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to get sector study data due to an unexpected error: {e}") from e
