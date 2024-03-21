#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-14

@author: Roland VANDE MAELE

@abstract: the class act as an interface between the application and the 
database, selecting data into the database via SQLAlchemy. These functions are 
part of the data access logic (DAL).

"""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.models.base import Session

class StockQuery:
    """
    A class for performing query operations related to stock data in the database.

    This class provides functionality to query stock data, specifically designed
    for operations such as extracting data necessary for clustering company
    profiles based on certain financial metrics.

    """

    def __init__(self, db_session: Session):
        """
        Initializes the StockQuery with a database session.

        Args:
            db_session (Session): The database session used for executing
                                  queries against the database.
        """
        self.db_session = db_session

    def extract_data_for_company_profiles_clustering(self):
        """
        Extracts stock data needed for clustering company profiles.

        This method queries the database for specific attributes of company
        profiles: stock_id, beta, vol_avg, and mkt_cap. These attributes are
        essential for performing clustering analysis to identify groups of
        companies with similar trading characteristics.

        Returns:
            A list of tuples where each tuple contains the stock_id, beta,
            vol_avg, and mkt_cap of a company, representing the data needed
            for clustering analysis.

        Raises:
            SQLAlchemyError: An error occurred during the database transaction.
                             The transaction is rolled back and the session
                             is closed in case of an error.
        """
        try:
            query = text(
                "SELECT stock_id, beta, vol_avg, mkt_cap FROM companyprofile")
            data = self.db_session.execute(query).fetchall()

            return data

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def extract_list_of_symbols_from_sxxp(self):
        """
        Extracts a list of stock symbols from the 'sxxp' table for their most recent date.

        This method executes a SQL query that retrieves stock symbols 
        ('symbol') from the 'stocksymbol' table. It only selects symbols for 
        stock IDs ('stock_id') in the 'sxxp' table that correspond to the most 
        recent date for each stock ID. The query uses a Common Table Expression 
        (CTE) named 'LatestDates' to first find the latest date for each 
        'stock_id' in 'sxxp', and then it performs inner joins to fetch the 
        corresponding 'symbol' from 'stocksymbol'.

        The method handles exceptions that may arise during the database 
        operation, particularly those from SQLAlchemy, ensuring that the 
        database session is properly rolled back and closed in case of an error.

        Returns:
            list: A list of tuples, where each tuple contains the symbol and id 
            of a stock as its only elements.
                
        Raises:
            SQLAlchemyError: If any database operation fails, an error is 
            raised. The database session is rolled back to undo any partial 
            changes and closed to ensure no resources are leaked.

        """
        try:
            query = text(
                "WITH LatestDates AS (  \
                    SELECT \
                        stock_id, \
                        MAX(date) AS latest_date \
                    FROM \
                        sxxp \
                    GROUP BY \
                        stock_id \
                ) \
                SELECT \
                    ss.symbol, ss.id \
                FROM \
                    stocksymbol ss \
                INNER JOIN \
                    LatestDates ld ON ss.id = ld.stock_id \
                INNER JOIN \
                    sxxp ON sxxp.stock_id = ld.stock_id AND sxxp.date = ld.latest_date;"
                )

            data = self.db_session.execute(query).fetchall()

            return data

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_unmatched_stock_ids(self, table: str) -> list:
        """
        Retrieves a list of stock_ids from the 'sxxp' table that do not exist 
        in the specified table.

        This function executes a SQL query to select all stock_ids from the 
        'sxxp' table where there are no corresponding entries in the given 
        `table`. It fetches the latest stock_id based on the maximum date for 
        each stock_id that does not exist in the specified table.
        
        Args:
            table (str): The name of the table to check against the 'sxxp' 
            table for the existence of stock_ids.

        Returns:
            list: A list of stock_ids from the 'sxxp' table that are not 
            present in the specified `table`.
        
        Raises:
            RuntimeError: An error occurs during the database transaction. The 
            error is logged, and the transaction is rolled back. This exception 
            is raised if any SQLAlchemy related error occurs during the 
            execution of the query.
            
        """
        try:
            query = text(
                f"""
                SELECT stock_id, MAX(date)
                FROM sxxp
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM {table}
                    WHERE {table}.stock_id = sxxp.stock_id
                )
                GROUP BY stock_id;
                """)

            data = self.db_session.execute(query).fetchall()

            return [stock_id[0] for stock_id in data]

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()
