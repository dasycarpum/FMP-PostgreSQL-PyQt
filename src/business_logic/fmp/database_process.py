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
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from src.models.base import Session
from src.models.fmp.stock import StockSymbol
from src.services.api import get_jsonparsed_data
from src.dal.fmp.database_operation import StockManager

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
