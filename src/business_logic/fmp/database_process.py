#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-10

@author: Roland VANDE MAELE

@abstract: this additional level of abstraction means that data can be 
manipulated and business operations performed without direct concern for the 
implementation details of data retrieval or database interaction.

"""

from sqlalchemy.exc import SQLAlchemyError
from src.models.base import Session
from src.services.api import get_jsonparsed_data
from src.dal.fmp.database_operation import StockManager

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
            data = get_jsonparsed_data("https://financialmodelingprep.com/api/v3/stock/list?apikey=API_KEY") # pylint: disable=line-too-long

            # Inserting data into the database
            stock_manager.insert_stock_symbols(data)

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Failed to update stock symbols due to database error: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to update stock symbols due to an unexpected error: {e}") from e
