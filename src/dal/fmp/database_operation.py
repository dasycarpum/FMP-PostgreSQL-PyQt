#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-10

@author: Roland VANDE MAELE

@abstract: the class act as an interface between the application and the 
database, taking structured data (e.g. JSON) and inserting it into the database 
via SQLAlchemy. These functions are part of the data access logic (DAL).

"""

from sqlalchemy.exc import SQLAlchemyError
from src.models.base import Session
from src.models.fmp.stock import StockSymbol


class StockManager:
    """Manages operations related to stock data in the database."""

    def __init__(self, db_session: Session):
        """Initializes the StockManager with a database session."""
        self.db_session = db_session

    def insert_stock_symbols(self, data):
        """
        Inserts a list of stock symbols into the database.
        
        Args:
            data (list of dict): A list of dictionaries, where each dictionary
            represents a stock symbol.

        Raises:
            RuntimeError: Raises an exception if an error occurs during database operations.
        """
        try:
            for item in data:
                # Create a new StockSymbol instance for each JSON element
                stock_symbol = StockSymbol(
                    symbol=item.get("symbol"),
                    name=item.get("name"),
                    price=item.get("price"),
                    exchange=item.get("exchange"),
                    exchangeShortName=item.get("exchangeShortName"),
                    type_=item.get("type_")
                )
                # Add instance to session
                self.db_session.add(stock_symbol)
            # Commit all new instances to the database
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Important to undo changes in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            # Close session
            self.db_session.close()
