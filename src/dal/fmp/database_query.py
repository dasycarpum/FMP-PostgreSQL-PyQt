#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-14

@author: Roland VANDE MAELE

@abstract: the class act as an interface between the application and the 
database, selecting data into the database via SQLAlchemy. These functions are 
part of the data access logic (DAL).

"""

import pandas as pd
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

    def get_undeclared_dividends(self, start_date: str) -> list:
        """
        The aim is to identify stocks where no dividend has been declared by 
        FMP, but which are nonetheless subject to an adjustment : the function 
        retrieves the most recent date for each stock where the 'close' and 
        'adj_close' values differ, starting from a specified date, and where 
        the 'dividend_signature' is NULL.

        This function executes a SQL query using a Common Table Expression 
        (CTE) to rank differences between 'close' and 'adj_close' values for 
        each 'stock_id', starting from a given date. It selects the most recent 
        date (highest rank) for each stock where these conditions are met. The 
        difference between 'close' and 'adj_close' is calculated as 'dividend',
        and only records without a 'dividend_signature' are considered.

        Args:
            start_date (str): The starting date from which to search for 
            differences, in 'YYYY-MM-DD' format.

        Returns:
            list: A list of tuples, each containing the 'stock_id', the most 
            recent 'date' (as a string in 'YYYY-MM-DD' format) where 'close' 
            and 'adj_close' differ, and the calculated 'dividend'.
        Raises:
            RuntimeError: If any error occurs during the execution of the SQL 
            query, with the error message included.

        Example:
            >>> get_undeclared_dividends('2024-03-15')
            # This might return: [(28117, '2024-03-19', 10.0), ...] indicating 
            # the stock_id, date, and dividend where applicable.
        """
        try:
            query = text(f"""
            WITH RankedDifferences AS (
                SELECT
                    stock_id,
                    date,
                    close,
                    adj_close,
                    dividend_signature,
                    ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY date DESC) as rn
                FROM
                    dailychart
                WHERE
                    close != adj_close AND date > '{start_date}'
            )
            SELECT
                stock_id,
                date,
                (close-adj_close) as dividend
            FROM
                RankedDifferences
            WHERE
                rn = 1 AND dividend_signature IS NULL;
            """)

            data = self.db_session.execute(query).fetchall()

            return [(
                stock_id, date.strftime('%Y-%m-%d'), round(dividend,3)
                ) for stock_id, date, dividend in data]

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_stocksymbols_by_column(self, column: str) -> pd.DataFrame:
        """
        Retrieves stock symbols from the database, grouped and aggregated by a specified column.

        This method dynamically groups stock symbols based on a specified 
        column in the 'stocksymbol' table, such as 'exchange' or 'type_'. It 
        constructs and executes a SQL query that groups symbols by the 
        specified column, aggregates them into a list per group, and counts the 
        number of symbols in each group. The results are returned as a pandas 
        DataFrame, which includes the name of the group (based on the specified 
        column), a list of symbols in each group, and the count of symbols per 
        group. The DataFrame is ordered by the count of symbols in ascending 
        order.

        Args:
            column (str): The name of the column by which to group stock 
            symbols. This should be a valid column name in the 'stocksymbol' table.

        Returns:
            pandas.DataFrame: A DataFrame containing three columns:
                - The specified column name (str): The name of the group.
                - 'list_symbols' (list): A list of stock symbols associated with each group.
                - 'count_symbols' (int): The number of symbols associated with each group.

        Raises:
            RuntimeError: If an error occurs during query execution or data 
            processing, a RuntimeError is raised, including the original error 
            message from SQLAlchemy.
            
        """
        try:
            query = text(f"""
            SELECT {column}, 
                   ARRAY_AGG(symbol) AS list_symbols,
                   COUNT(symbol) AS count_symbols
            FROM stocksymbol
            GROUP BY {column}
            ORDER BY count_symbols;
            """)

            data = self.db_session.execute(query).fetchall()

            return pd.DataFrame(data, columns=[column, 'list_symbols', 'count_symbols'])

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()
