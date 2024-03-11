#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-10

@author: Roland VANDE MAELE

@abstract: the class act as an interface between the application and the 
database, taking structured data (e.g. JSON) and inserting it into the database 
via SQLAlchemy. These functions are part of the data access logic (DAL).

"""

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from src.models.base import Session
from src.models.fmp.stock import StockSymbol, CompanyProfile
from src.services.date import parse_date


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
                # Create and insert a new StockSymbol instance for each JSON element
                stmt = insert(StockSymbol).values(
                    symbol=item.get("symbol"),
                    name=item.get("name"),
                    price=item.get("price"),
                    exchange=item.get("exchange"),
                    exchangeshortname=item.get("exchangeShortName"),
                    type_=item.get("type")
                )
                # Use insertion with ON CONFLICT DO NOTHING
                stmt = stmt.on_conflict_do_nothing(index_elements=['symbol'])
                self.db_session.execute(stmt)
            # Commit all new instances to the database
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Important to undo changes in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            # Close session
            self.db_session.close()

    def insert_company_profile(self, data):
        """
        Inserts company profiles into the database based on provided data.

        This function iterates over a list of dictionaries, each representing a 
        company profile, and inserts them into the 'companyprofile' table. 
        Before inserting, it retrieves the corresponding 'stock_id' from the 
        'stocksymbol' table using the 'symbol' provided in each dictionary. If 
        the symbol does not exist in 'stocksymbol', the function skips 
        inserting that company profile. It handles duplicates by ignoring 
        attempts to insert records that would violate the unique constraint on 
        'stock_id'.

        Args:
            data (list of dict): A list of dictionaries, where each dictionary 
            contains data about a company profile. The 'symbol' is used to link 
            the company profile with its corresponding stock symbol.

        Raises:
            RuntimeError: An error occurred during database operations. The 
            error is logged, and a RuntimeError is raised with a message 
            indicating a database error occurred.

        Note:
            The function commits the transaction if all insertions are 
            successful. In case of an error, it performs a rollback to undo any 
            changes made during the transaction. This ensures the database 
            integrity is maintained. After attempting the operations, the 
            database session is closed.

        Example:
            >>> data = [
                    {
                        "symbol": "TTE.PA",
                        "currency": "EUR",
                        "cik": "0000320193",
                        "isin": "FR0000120271",
                        ...
                    }
                ]
            >>> insert_company_profiles(data)
        """
        try:
            for item in data:
                # Date parsing
                ipo_date_parsed = parse_date(item.get("ipoDate"))
                # Find the stock id from the 'stocksymbol' table based on the symbol
                stock_id_query = self.db_session.query(StockSymbol.id).filter(
                    StockSymbol.symbol == item.get("symbol")).scalar()

                # If stock symbol exists, insert the company profile
                if stock_id_query:
                    stmt = insert(CompanyProfile).values(
                        stock_id=stock_id_query,
                        currency=item.get("currency"),
                        cik=str(item.get("cik")),  # convert to string
                        isin=item.get("isin"),
                        cusip=str(item.get("cusip")),  # Same as cik
                        industry=item.get("industry"),
                        website=item.get("website"),
                        description=item.get("description"),
                        sector=item.get("sector"),
                        country=item.get("country"),
                        image=item.get("image"),
                        ipo_date=ipo_date_parsed,
                        is_etf=item.get("isEtf"),
                        is_actively_trading=item.get("isActivelyTrading"),
                        is_adr=item.get("isAdr"),
                        is_fund=item.get("isFund")
                    )
                    # Use insertion with ON CONFLICT DO NOTHING to avoid stock_id duplicates
                    stmt = stmt.on_conflict_do_nothing(index_elements=['stock_id'])
                    self.db_session.execute(stmt)
                else:
                    # Handle case where stock symbol is not found
                    print(f"Stock symbol {item.get('symbol')} not found.")

            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            self.db_session.close()
