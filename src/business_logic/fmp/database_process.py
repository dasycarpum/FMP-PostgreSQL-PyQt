#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-10

@author: Roland VANDE MAELE

@abstract: this additional level of abstraction means that data can be 
manipulated and business operations performed without direct concern for the 
implementation details of data retrieval or database interaction.

"""

import os
import time
from datetime import datetime, timedelta
import csv
import re
from dotenv import load_dotenv
from sqlalchemy import func, text
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError
from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication
from src.models.base import Session
from src.models.fmp.stock import StockSymbol, DailyChartEOD
from src.services.api import get_jsonparsed_data
from src.services.date import generate_business_time_series, parse_date
from src.services.sql import convert_table_to_hypertable
from src.dal.fmp.database_operation import DBManager, StockManager
from src.dal.fmp.database_query import StockQuery

load_dotenv()
API_KEY_FMP = os.getenv('API_KEY_FMP')

class DBService:
    """Service class for managing database operations."""

    def __init__(self, database_name: str):
        """Initializes the DBMService with a database name."""
        self.database_name = database_name

    def create_new_database(self) -> None:
        """
        Validates the database name for conformity to naming rules, creates a 
        new database and adds it the TimescaleDB extension.

        This function validates the given database name to ensure it contains 
        only alphanumeric characters and underscores, which conforms to typical 
        database naming conventions. If the validation passes, it proceeds to 
        create the database by calling a Data Access Layer (DAL) functions 
        `create_database` and `add_timescaledb_extension`. If any step fails, 
        it raises a RuntimeError with a descriptive message about the failure.

        Args:
            None

        Returns:
            None.

        Raises:
            RuntimeError: If the database name is invalid (contains spaces or 
            special characters), or if there's a SQLAlchemy error during the 
            database creation process, or if any unexpected error occurs.

        """
        try:
            # Verify no spaces or special characters
            if not re.match("^[a-zA-Z0-9_]+$", self.database_name):
                raise ValueError(
                    "Database name must contain only alphanumeric characters and underscores."
                )

            # Create an instance of DBManager
            db_manager = DBManager(self.database_name.lower())

            # Create the new database
            db_manager.create_database()

            # Add the TimescaleDB extension to the database
            db_manager.add_timescaledb_extension()

        except ValueError as e:
            raise RuntimeError(f"Invalid database name: {e}") from e
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to create a database due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to create a database due to an unexpected error: {e}") from e


class StockService(QObject):
    """Service class for managing stock operations."""
    update_signal = pyqtSignal(str)  # Define a signal to emit messages

    def __init__(self, db_session: Session):
        """
        Initializes the StockService with a database session.
        
        Args:
            db_session (Session): The database session for performing operations.
        """
        super().__init__()  # Initialize the QObject
        self.db_session = db_session

    def create_stock_tables(self) -> None:
        """
        Creates all stock-related tables in the database.

        This function utilizes the `StockManager` to create tables based on the 
        SQLAlchemy models defined for stock data. It wraps the table creation 
        process in a try-except block to handle any SQLAlchemy errors or other 
        exceptions, ensuring that informative errors are raised in case of 
        failure.

        Args:
            None.

        Raises:
            RuntimeError: If an error occurs during the table creation process. 
            This includes both SQLAlchemy related errors and any unexpected 
            exceptions. The error message provides details about the failure to 
            aid in debugging.

        """
        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            # Create tables
            stock_manager.create_stock_tables_sequentially()

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to create stock tables due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to create stock tables due to an unexpected error: {e}") from e 

    def create_business_time_series(self) -> None:
        """
        Generates a time series of business dates, inserts them into a 
        database, and converts the table into a TimescaleDB hypertable.

        Args:
            None

        Raises:
            RuntimeError: If an error occurs during the table creation process. 
            This includes both SQLAlchemy related errors and any unexpected 
            exceptions. The error message provides details about the failure to 
            aid in debugging.

        """
        try:
            # Create table
            generate_business_time_series()

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to generate time series table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate time series table due to an unexpected error: {e}") from e 

    def convert_date_tables_to_hypertables(self) -> None:
        """
        Converts the specified PostgreSQL tables, with a 'date' column, into 
        TimescaleDB hypertables.

        Args:
            None

        Raises:
            RuntimeError: If an error occurs during the table creation process. 
            This includes both SQLAlchemy related errors and any unexpected 
            exceptions. The error message provides details about the failure to 
            aid in debugging.

        """
        try:
            # Stock tables to convert
            tables = ['dailychart', 'dividend', 'keymetrics', 'sxxp']

            for table in tables:
                convert_table_to_hypertable(table)
                time.sleep(0.2)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to generate time series table due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate time series table due to an unexpected error: {e}") from e 

    def fetch_stock_symbols(self) -> None:
        """
        Fetches stock symbols from an external API and updates the database.
        
        This function acts as a part of the business logic layer, orchestrating
        the process of data retrieval and database update.
        
        Args:
            None.
            
        Raises:
            Exception: Raises an exception if the API data retrieval or database update fails.
        """
        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.update_signal.emit(
                f"Fetch stock symbols at {timestamp} -> processing..."
            ) # Emit signal with message

            # Data recovery
            data = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/stock/list?apikey={API_KEY_FMP}") # pylint: disable=line-too-long

            # Inserting data into the database
            stock_manager.insert_stock_symbols(data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to fetch stock symbols due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch stock symbols due to an unexpected error: {e}") from e

    def fetch_company_profiles_for_exchange(self, exchange: str,
        batch_size: int = 50, calls_per_minute: int = 300):
        """Fetches and inserts company profiles in bulk from an external API 
        into the PostgreSQL database.

        This function retrieves company symbols from the specified exchange, 
        makes batch API calls to fetch company profiles, and then uses bulk 
        operations to insert the data into the database. The function handles 
        API rate limits and commits data to the database in batches to optimize 
        performance.

        Args:
            exchange (str): The stock exchange symbol to fetch the company 
            profiles for, such as 'NASDAQ'.
            batch_size (int): The number of company symbols to fetch data for 
            in each API call. Defaults to 50.
            calls_per_minute (int): The maximum number of API calls allowed per 
            minute, used to calculate necessary delays between API calls to 
            adhere to rate limits. Defaults to 300.

        Raises:
            RuntimeError: An error occurred due to database issues or API 
            failures. The error message will provide more details about the 
            nature of the error.
        
        """
        # Fetch all symbols for the given exchange
        symbols = self.db_session.query(StockSymbol.symbol).filter(
            StockSymbol.exchange == exchange).all()
        symbols = [symbol[0] for symbol in symbols]

        stock_manager = StockManager(self.db_session)
        total_symbols = len(symbols)
        api_url_template = "https://financialmodelingprep.com/api/v3/profile/{}?apikey={}"

        try:
            # Process symbols in batches respecting the API rate limit
            for i in range(0, total_symbols, batch_size):
                batch_symbols = symbols[i:i + batch_size]
                api_url = api_url_template.format(','.join(batch_symbols), API_KEY_FMP)
                data = get_jsonparsed_data(api_url)  # Fetch data for the batch

                if data:
                    stock_manager.insert_company_profiles(data)

                # Respect the rate limit
                if i + batch_size < total_symbols:
                    time.sleep(60 * batch_size / calls_per_minute)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to fetch company profiles for exchange due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch company profiles for exchange due to an unexpected error: {e}"
                ) from e
        finally:
            self.db_session.close()

    def fetch_company_profiles(self) -> None:
        """
        Fetches company profiles for stock exchanges listed in a CSV file and 
        updates them in the database. 
        
        This method reads a predefined CSV file containing stock exchange 
        identifiers, then iterates over these identifiers to fetch and update 
        company profiles for each exchange by leveraging the 
        `fetch_company_profiles_for_exchange` method. 

        Args:
            None.

        Raises:
            RuntimeError: If a database error is encountered during the process 
            of fetching company profiles, or if an unexpected error occurs, a 
            RuntimeError is raised with a message detailing the issue. The 
            error details are extracted from the SQLAlchemyError or generic 
            exception caught during the operation.

        """
        try:
            # Define the file path based on the given date string
            file_path = './raw_data/stock_exchange.csv'

            # Open the CSV file and read data
            with open(file_path, 'r', encoding='utf8') as csvfile:
                data = csv.reader(csvfile)
                # Inserting data into the database
                for row in data:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.update_signal.emit(
                        f"Fetch company profiles at {timestamp} -> processing {row[0]} ..."
                    ) # Emit signal with message
                    self.fetch_company_profiles_for_exchange(row[0])

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to fetch company profiles due to database error: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch company profiles due to an unexpected error: {e}") from e

    def fetch_daily_chart_for_period(self, symbol: str, start_date: str,
        end_date:str, operation:str, stock_id: int = 0) -> None:
        """
        Fetches daily chart data for a given symbol and period, and inserts it 
        into the database.

        This function retrieves historical price data for a specified stock 
        symbol between the start and end dates from the Financial Modeling Prep 
        API. It then updates the actual data and inserts the new data into the 
        database using the 'update_daily_chart_data' and        
        `insert_daily_chart_data` methods of the `StockManager` class. The 
        function handles database and unexpected errors by raising a 
        `RuntimeError`.

        Args:
            symbol (str): The stock symbol for which to retrieve historical price data.
            start_date (str): The start date for the period of interest in YYYY-MM-DD format.
            end_date (str): The end date for the period of interest in YYYY-MM-DD format.
            operation (str): Choice between updating actual data into the 
            database or inserting new data or updating adjusted close.

        Raises:
            RuntimeError: An error occurred while updating the daily chart due 
            to either a database error or an unexpected error. The original 
            error is wrapped in the RuntimeError and re-raised.

        """
        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            # Data recovery
            data = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from={start_date}&to={end_date}&apikey={API_KEY_FMP}") # pylint: disable=line-too-long

            if data and 'historical' in data:
                if operation == 'update_recent_data':
                    # Update last data into the database and insert new data
                    stock_manager.update_daily_chart_data(data)
                    stock_manager.insert_daily_chart_data(data)
                elif operation == 'insert':
                    # Only inserting new data into the database (historical data)
                    stock_manager.insert_daily_chart_data(data)
                elif operation == 'update_adj_close':
                    # Update adjusted close price into the database
                    stock_manager.update_daily_chart_by_stock(
                        stock_id, data['historical'], start_date, end_date)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to fetch daily chart for period due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch daily chart for period due to an unexpected error: {e}") from e

    def fetch_historical_dividend(self, symbol: str) -> None:
        """Fetches and stores historical dividend data for a specified stock symbol.

        This function retrieves historical dividend data for a given stock 
        symbol by making an external API call. The retrieved data is then 
        inserted into the database using the `StockManager` class. The function 
        is designed to handle any exceptions that occur during the database 
        operation or data retrieval process, ensuring that any errors are 
        properly reported.

        Args:
            symbol (str): The stock symbol for which to fetch historical dividend data.

        Raises:
            RuntimeError: An error occurred during the database operation or 
            while fetching the data from the external API. The error is logged 
            with a message specifying whether it was a database error or an 
            unexpected error.

        """
        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            # Data recovery
            data = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{symbol}?apikey={API_KEY_FMP}") # pylint: disable=line-too-long

            # Inserting data into the database
            stock_manager.insert_historical_dividend(data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to fetc historical dividend due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch historical dividend due to an unexpected error: {e}") from e

    def fetch_historical_key_metrics(self, symbol: str,
        period: str = 'quarter') -> None:
        """
        Fetches historical key metrics for a given stock symbol and inserts 
        them into the database.

        This function retrieves financial metrics for a specified stock symbol 
        for a given period ('quarter' by default). It uses an external API to 
        fetch the data, then processes and inserts the fetched data into the 
        database using the `StockManager` class. The function handles both
        SQLAlchemy errors related to database operations and general exceptions 
        that may occur during the data fetching process.

        Args:
            symbol (str): The stock symbol for which historical key metrics are 
            to be fetched.
            period (str): The period for which the data should be fetched. 
            Defaults to 'quarter'. Other option : 'annual'  

        Raises:
            RuntimeError: If a database error occurs during the operation. The 
            error message includes the original error for debugging purposes.
            RuntimeError: If an unexpected error occurs during the data 
            fetching or insertion process. The error message includes the 
            original error for further investigation.
            
        """
        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            # Data recovery
            data = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}?period={period}&apikey={API_KEY_FMP}") # pylint: disable=line-too-long

            # Inserting data into the database
            stock_manager.insert_historical_key_metrics(data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to fetch historical key metrics due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch historical key metrics due to an unexpected error: {e}") from e

    def fetch_sxxp_historical_components(self, date_str: str) -> None:
        """
        Updates the database with historical sxxp components from a given CSV file.

        This function reads historical data for the STOXX Europe 600 index from 
        a CSV file corresponding to the provided date and inserts this data 
        into the database using the StockManager's insert function.

        Args:
            date_str (str): The date string used to locate the CSV file. The 
            date string should be in the format 'YYYYMMDD'.

        Raises:
            RuntimeError: If a database error occurs during the insertion 
            process. The error message includes the original error for 
            debugging purposes. 
            RuntimeError: If an unexpected error occurs during the data reading 
            or insertion process. The error message includes the original error 
            for further investigation.

        Example:
            fetch_sxxp_historical_component('20240301')
        """
        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            # Define the file path based on the given date string
            file_path = f'./raw_data/slpublic_sxxp_{date_str}.csv'

            # Open the CSV file and read data
            with open(file_path, 'r', encoding='utf8') as csvfile:
                data = csv.DictReader(csvfile, delimiter=';')
                # Emit signal with message
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.update_signal.emit(
                   f"Fetch STOXX Europe 600 components at {timestamp} -> processing {date_str} CSV file..." # pylint: disable=line-too-long
                )
                # Inserting data into the database
                stock_manager.insert_sxxp_historical_components(data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to fetch historical sxxp components due to database error: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch historical sxxp components due to an unexpected error: {e}"
            ) from e

    def fetch_usindex_components(self, us_market_index: str) -> None:
        """
        Fetches and updates US market constituents from a given index.

        This method retrieves index from a user action and then fetches 
        their constituents using an external API.

        Args:
            us_market_index (str): The US market index ('dowjones', 'sp500', 'nasdaq')
        Raises:
            RuntimeError: If there's a database error or unexpected error during the update process.

        """
        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            # Data recovery
            data = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/{us_market_index}_constituent?apikey={API_KEY_FMP}") # pylint: disable=line-too-long

            # Inserting data into the database
            stock_manager.insert_usindex_components(us_market_index, data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to fetch historical key metrics due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch historical key metrics due to an unexpected error: {e}") from e

    def fetch_dividends_in_batches(self, batch_size: int = 50, calls_per_minute: int = 300) -> None:
        """
        Fetches historical dividends for a list of stock symbols in batches, 
        respecting the API rate limits.

        This method retrieves stock symbols from the database and then fetches 
        their historical dividend information using an external API. The 
        fetching process is done in batches to comply with the rate limit 
        imposed by the API, which is specified by the `calls_per_minute` 
        parameter. If an error occurs while fetching the dividend information
        for a specific symbol, the error is logged, and the method continues to 
        process the next symbols in the batch. This ensures that temporary 
        issues with specific symbols or API limits do not halt the entire 
        fetching process.

        Args:
            batch_size (int): The number of symbols to process in each batch. 
            This determines how many API calls are made in one batch before 
            potentially pausing to respect the API rate limit. Default 50.
            calls_per_minute (int): The maximum number of API calls allowed per 
            minute. This is used to calculate the pause duration between 
            batches if necessary to stay within the rate limit. Default 300 
            (for FMP)

        Raises:
            ValueError: If unable to fetch stock symbols from the database, a 
            ValueError is raised indicating the failure to initiate the 
            fetching process.

        Returns:
            None: This method does not return a value. It performs operations
            to fetch historical dividends and handles errors by logging them 
            without interrupting the process.
        """
        try:
            stock_query = StockQuery(self.db_session)
            stock_symbol_query= (stock_query.extract_list_of_symbols_from_sxxp()
                        + stock_query.extract_list_of_symbols_from_usindex())

            if stock_symbol_query is None:
                raise ValueError("Failed to fetch stock symbols from the database.")

            symbols = [symbol[0] for symbol in stock_symbol_query]
            batch_tot = int(len(symbols)/batch_size) + 1
            batch_n = 1

            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                # Emit signal with message
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.update_signal.emit(
                    f"Fetch dividends at {timestamp} -> processing batch {batch_n} / {batch_tot}..."
                )
                batch_n += 1
                for symbol in batch:
                    # pylint: disable=broad-except
                    try:
                        self.fetch_historical_dividend(symbol)
                    except Exception as api_error:
                        print(f"Error fetching historical dividend for {symbol}: {api_error}")
                    # pylint: enable=broad-except

                # Calculate and respect the rate limit
                if i + batch_size < len(symbols):  # Check if there's another batch
                    sleep_time = 60 * batch_size / calls_per_minute
                    time.sleep(sleep_time)

        except SQLAlchemyError as db_error:
            raise ValueError(
                "Database error occurred while fetching dividends in batches.") from db_error
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch dividends in batches due to an unexpected error: {e}") from e

    def fetch_keys_metrics_in_batches(self, period: str = 'quarter',
        batch_size: int = 50, calls_per_minute: int = 300) -> None:
        """
        Fetches historical key metrics for a list of stock symbols in batches, 
        respecting the API rate limits.

        This method retrieves stock symbols from the database and then fetches 
        their historical key metrics information using an external API. The 
        fetching process is done in batches to comply with the rate limit 
        imposed by the API, which is specified by the `calls_per_minute` 
        parameter. If an error occurs while fetching the key metrics information
        for a specific symbol, the error is logged, and the method continues to 
        process the next symbols in the batch. This ensures that temporary 
        issues with specific symbols or API limits do not halt the entire 
        fetching process.

        Args:
            period (str): The period for which the data should be fetched. 
            Defaults to 'quarter'. Other option : 'annual' 
            batch_size (int): The number of symbols to process in each batch. 
            This determines how many API calls are made in one batch before 
            potentially pausing to respect the API rate limit. Default to 50.
            calls_per_minute (int): The maximum number of API calls allowed per 
            minute. This is used to calculate the pause duration between 
            batches if necessary to stay within the rate limit. Default to 300 
            (for FMP).

        Raises:
            ValueError: If unable to fetch stock symbols from the database, a 
            ValueError is raised indicating the failure to initiate the 
            fetching process.

        Returns:
            None: This method does not return a value. It performs operations
            to fetch historical dividends and handles errors by logging them 
            without interrupting the process.
        """
        try:
            stock_query = StockQuery(self.db_session)
            stock_symbol_query= (stock_query.extract_list_of_symbols_from_sxxp()
                        + stock_query.extract_list_of_symbols_from_usindex())

            if stock_symbol_query is None:
                raise ValueError("Failed to fetch stock symbols from the database.")

            symbols = [symbol[0] for symbol in stock_symbol_query]
            batch_tot = int(len(symbols)/batch_size) + 1
            batch_n = 1

            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                # Emit signal with message
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.update_signal.emit(
                    f"Fetch key metrics at {timestamp} -> processing batch {batch_n} / {batch_tot}..." # pylint: disable=line-too-long
                )
                batch_n += 1
                for symbol in batch:
                    # pylint: disable=broad-except
                    try:
                        self.fetch_historical_key_metrics(symbol, period)
                    except Exception as api_error:
                        print(f"Error fetching historical key metrics for {symbol}: {api_error}")
                    # pylint: enable=broad-except

                # Calculate and respect the rate limit
                if i + batch_size < len(symbols):  # Check if there's another batch
                    sleep_time = 60 * batch_size / calls_per_minute
                    time.sleep(sleep_time)

        except SQLAlchemyError as db_error:
            raise ValueError(
                "Database error occurred while fetching keys metrics in batches.") from db_error
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch keys metrics in batches due to an unexpected error: {e}") from e

    def fetch_daily_charts_by_period(self, calls_per_minute: int = 300) -> None:
        """
        Fetches daily charts for a list of stock symbols in batches, 
        respecting the API rate limits and fetching data in 5-year intervals
        starting from January 1, 1985, to today.

        This method retrieves stock symbols from the database and then fetches 
        their historical key metrics information using an external API. The 
        fetching process is done in batches to comply with the rate limit 
        imposed by the API, which is specified by the `calls_per_minute` 
        parameter. If an error occurs while fetching the key metrics information
        for a specific symbol, the error is logged, and the method continues to 
        process the next symbols in the batch. This ensures that temporary 
        issues with specific symbols or API limits do not halt the entire 
        fetching process.

        Args:
            calls_per_minute (int): The maximum number of API calls allowed per 
            minute. This is used to calculate the pause duration between 
            batches if necessary to stay within the rate limit. Default to 300 
            (for FMP).

        Raises:
            ValueError: If unable to fetch stock symbols from the database, a 
            ValueError is raised indicating the failure to initiate the 
            fetching process.

        Returns:
            None: This method does not return a value. It performs operations
            to fetch historical dividends and handles errors by logging them 
            without interrupting the process.
        """
        start_year = 1985
        period_years = 5
        start_date = datetime(start_year, 1, 1)
        end_date = datetime.now()
        try:
            stock_query = StockQuery(self.db_session)
            stock_symbol_query= (stock_query.extract_list_of_symbols_from_sxxp()
                        + stock_query.extract_list_of_symbols_from_usindex())

            if stock_symbol_query is None:
                raise ValueError("Failed to fetch stock symbols from the database.")

            symbols = [symbol[0] for symbol in stock_symbol_query]
            symbol_tot = len(symbols)
            symbol_n = 1
            for symbol in symbols:
                # Emit signal with message
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.update_signal.emit(
                    f"Fetch daily chart at {timestamp} -> processing {symbol} : {symbol_n} / {symbol_tot}..."# pylint: disable=line-too-long
                )
                symbol_n += 1
                current_start_date = start_date
                while current_start_date < end_date:
                    current_end_date = min(
                        current_start_date + timedelta(days=365 * period_years), end_date)
                    # pylint: disable=broad-except
                    try:
                        self.fetch_daily_chart_for_period(symbol,
                            current_start_date.strftime('%Y-%m-%d'),
                            current_end_date.strftime('%Y-%m-%d'), 'insert')
                    except Exception as api_error:
                        print(f"Error fetching historical daily charts for {symbol} from {current_start_date} to {current_end_date}: {api_error}") # pylint: disable=line-too-long
                    # pylint: enable=broad-except
                    current_start_date = current_end_date + timedelta(days=1)

                    # Respect the rate limit after each call
                    sleep_time = 60 / calls_per_minute
                    time.sleep(sleep_time)

        except SQLAlchemyError as db_error:
            raise ValueError(
                "Database error occurred while fetching daily charts by period.") from db_error
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch daily charts by period due to an unexpected error: {e}") from e

    def fetch_daily_chart_updating(self, calls_per_minute: int = 1000):
        """
        Updates the daily chart data for each stock symbol by fetching new data 
        from a defined period.

        This function first retrieves the most recent date available for each 
        stock symbol in the database. Then, for each symbol, it calculates the 
        start date for updating the daily chart data based on the most recent 
        date available. If no date is available, a default start date is set. 
        It then fetches and updates the daily chart data for each symbol for 
        the period between the calculated start date and the current date.

        Args:
            calls_per_minute (int): The maximum number of API calls allowed per 
            minute. This is used to calculate the pause duration between 
            batches if necessary to stay within the rate limit. Default to 300 
            (for FMP).

        Returns:
            None

        Raises:
            ValueError: If there is a failure in fetching data from the database.

        """
        try:
            end_date = datetime.now().date()

            # Join to fetch stock_id, symbol, and the most recent date for
            # each symbol in a single query
            stock_alias = aliased(StockSymbol)
            most_recent_dates = self.db_session.query(
                stock_alias.id,
                stock_alias.symbol,
                func.max(DailyChartEOD.date).label('most_recent_date')
            ).join(DailyChartEOD, DailyChartEOD.stock_id == stock_alias.id
            ).group_by(stock_alias.id
            ).all()

        except SQLAlchemyError as e:
            raise ValueError(f"Failed to fetch data from database: {e}") from e

        symbol_tot = len(most_recent_dates)
        symbol_n = 1
        for _, symbol, most_recent_date in most_recent_dates:
            try:
                if most_recent_date is not None:
                    # Calculate the start date for the update if a most recent date exists
                    if most_recent_date.weekday() == 0:  # 0 = Monday
                        start_date = most_recent_date - timedelta(days=5)
                    else:
                        start_date = most_recent_date - timedelta(days=3)
                else:
                    # Set a default start date (possibly the company's creation
                    # date or another) if no recent date exists
                    start_date = end_date - timedelta(days=365)  # arbitrary start date

                # Emit signal with message
                timestamp = datetime.now().strftime("%H:%M:%S")
                start_date_str = start_date.strftime('%Y-%m-%d')
                end_date_str = end_date.strftime('%Y-%m-%d')
                self.update_signal.emit(
                    f"Update daily chart at {timestamp} -> processing {symbol} from {start_date_str} to {end_date_str} : {symbol_n} / {symbol_tot}..."# pylint: disable=line-too-long
                )
                symbol_n += 1

                # Fetch daily chart for period
                self.fetch_daily_chart_for_period(
                    symbol,start_date_str, end_date_str, 'update_recent_data')

                # Respect the rate limit after each call
                sleep_time = 60 / calls_per_minute
                time.sleep(sleep_time)

            except SQLAlchemyError as e:
                print(f"Database error updating data for {symbol}: {e}")
            except ValueError as e:
                print(f"Value error for {symbol}: {e}")
            except Exception as e: # pylint: disable=broad-except
                print(f"Unexpected error for {symbol}: {e}")

    def fetch_daily_charts_by_stock(self, stock_id: int, symbol:str,
        calls_per_minute: int = 300) -> None:
        """
        Fetches and processes daily chart data for a specified stock over a 
        span of years, dividing the requests to adhere to API rate limits.

        This function retrieves the earliest and latest dates of daily chart 
        data available for a stock, then iteratively fetches the data in chunks 
        based on a defined period in years, respecting the API's rate limits.

        Args:
            stock_id (int): The unique identifier for the stock.
            symbol (str): The stock symbol.
            calls_per_minute (int): The maximum number of API calls allowed per 
            minute. Defaults to 300.

        Raises:
            ValueError: If there is an error executing the database query.
            RuntimeError: If there is an unexpected error during the fetching process.

        """
        period_years = 5

        try:
            # Determine the minimum and maximum dates for the stock data available in the database.
            query = text(f"""
                SELECT MIN(date), MAX(date) FROM dailychart
                WHERE stock_id = {stock_id};
                """)

            result = self.db_session.execute(query).fetchall()
            (start_date, end_date), = result

            start_date = parse_date(start_date) if isinstance(start_date, str) else start_date
            end_date = parse_date(end_date) if isinstance(end_date, str) else end_date

            # 5-year stage loop
            current_start_date = start_date
            while current_start_date < end_date:
                current_end_date = min(
                    current_start_date + timedelta(days=365 * period_years), end_date)

                self.update_signal.emit(
                    f"Adjusted closing update in dailychart -> processing {symbol} from {current_start_date.strftime('%Y-%m-%d')} to {current_end_date.strftime('%Y-%m-%d')} ..."# pylint: disable=line-too-long
                )
                # Force the event loop to process the emitted signal
                QCoreApplication.processEvents()

                # pylint: disable=broad-except
                try:
                    self.fetch_daily_chart_for_period(
                        symbol,
                        current_start_date.strftime('%Y-%m-%d'),
                        current_end_date.strftime('%Y-%m-%d'),
                        'update_adj_close',
                        stock_id)
                except Exception as api_error:
                    print(f"Error fetching historical daily charts for {symbol} from {current_start_date} to {current_end_date}: {api_error}") # pylint: disable=line-too-long
                # pylint: enable=broad-except
                current_start_date = current_end_date + timedelta(days=1)

                # Respect the rate limit after each call
                sleep_time = 60 / calls_per_minute
                time.sleep(sleep_time)

        except SQLAlchemyError as db_error:
            raise ValueError(
                "Database error occurred while fetching daily charts by stock.") from db_error
        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch daily charts by stock due to an unexpected error: {e}") from e
