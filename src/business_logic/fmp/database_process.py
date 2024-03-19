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
import csv
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from src.models.base import Session
from src.models.fmp.stock import StockSymbol
from src.services.api import get_jsonparsed_data
from src.dal.fmp.database_operation import StockManager
from src.dal.fmp.database_query import StockQuery

load_dotenv()
API_KEY_FMP = os.getenv('API_KEY_FMP')

class StockService:
    """Service class for managing stock operations."""

    def __init__(self, db_session: Session):
        """
        Initializes the StockService with a database session.
        
        Args:
            db_session (Session): The database session for performing operations.
        """
        self.db_session = db_session

    def fetch_stock_symbols(self) -> None:
        """
        Fetches stock symbols from an external API and updates the database.
        
        This function acts as a part of the business logic layer, orchestrating
        the process of data retrieval and database update.
        
        Args:
            db_session (Session): The database session for performing database operations.
            
        Raises:
            Exception: Raises an exception if the API data retrieval or database update fails.
        """
        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            # Data recovery
            data = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/stock/list?apikey={API_KEY_FMP}") # pylint: disable=line-too-long

            # Inserting data into the database
            stock_manager.insert_stock_symbols(data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to update stock symbols due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to update stock symbols due to an unexpected error: {e}") from e

    def fetch_company_profiles_for_exchange(self, exchange: str,
        batch_size: int = 50, calls_per_minute: int = 300) -> None:
        """
        Fetches and updates company profiles from a given exchange in batches,
        respecting API rate limits.

        Args:
            exchange (str): The exchange to fetch company profiles for.
            batch_size (int): Number of symbols to process in each batch.
            calls_per_minute (int): Maximum number of API calls allowed per minute.

        Raises:
            RuntimeError: If there's a database error or unexpected error during the update process.

        """
        # Fetch all symbols for the given exchange
        stock_symbol_query = self.db_session.query(
            StockSymbol.symbol).filter(StockSymbol.exchange == exchange).all()

        symbols = [symbol[0] for symbol in stock_symbol_query]

        try:
            # Initialize StockManager with the database session
            stock_manager = StockManager(self.db_session)

            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]

                for symbol in batch:
                    # Data recovery
                    data = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={API_KEY_FMP}") # pylint: disable=line-too-long

                    # Inserting data into the database
                    stock_manager.insert_company_profile(data)

                self.db_session.commit()  # Commit after each batch

                # Calculate and respect the rate limit
                if i + batch_size < len(symbols):  # Check if there's another batch
                    time.sleep(60 * batch_size / calls_per_minute)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to update company profile due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to update company profile due to an unexpected error: {e}") from e

    def fetch_daily_chart_for_period(self, symbol: str, start_date: str,
        end_date:str) -> None:
        """
        Fetches daily chart data for a given symbol and period and inserts it into the database.

        This function retrieves historical price data for a specified stock 
        symbol between the start and end dates from the Financial Modeling Prep 
        API. It then inserts this data into the database using the 
        `insert_daily_chart_data` method of the `StockManager` class. The 
        function handles database and unexpected errors by raising a 
        `RuntimeError`.

        Args:
            symbol (str): The stock symbol for which to retrieve historical price data.
            start_date (str): The start date for the period of interest in YYYY-MM-DD format.
            end_date (str): The end date for the period of interest in YYYY-MM-DD format.

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

            # Inserting data into the database
            stock_manager.insert_daily_chart_data(data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to update daily chart due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to update daily chart due to an unexpected error: {e}") from e

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
                f"Failed to update historical dividend due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to update historical dividend due to an unexpected error: {e}") from e

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
                f"Failed to update historical key metrics due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to update historical key metrics due to an unexpected error: {e}") from e

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
                # Inserting data into the database
                stock_manager.insert_sxxp_historical_components(data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to update historical sxxp components due to database error: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to update historical sxxp components due to an unexpected error: {e}"
            ) from e

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
            stock_symbol_query = stock_query.extract_list_of_symbols_from_sxxp()

            if stock_symbol_query is None:
                raise ValueError("Failed to fetch stock symbols from the database.")

            symbols = [symbol[0] for symbol in stock_symbol_query]

            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]

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
                    print(f"Sleeping for {sleep_time:.2f} seconds to respect rate limit...")
                    time.sleep(sleep_time)

        except SQLAlchemyError as db_error:
            raise ValueError("Database error occurred while fetching stock symbols.") from db_error

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
            stock_symbol_query = stock_query.extract_list_of_symbols_from_sxxp()

            if stock_symbol_query is None:
                raise ValueError("Failed to fetch stock symbols from the database.")

            symbols = [symbol[0] for symbol in stock_symbol_query]

            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]

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
                    print(f"Sleeping for {sleep_time:.2f} seconds to respect rate limit...")
                    time.sleep(sleep_time)

        except SQLAlchemyError as db_error:
            raise ValueError("Database error occurred while fetching stock symbols.") from db_error
