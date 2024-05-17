#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-14

@author: Roland VANDE MAELE

@abstract: the class act as an interface between the application and the 
database, selecting data into the database via SQLAlchemy. These functions are 
part of the data access logic (DAL).

"""

import time
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text, inspect
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

    def extract_list_of_symbols_from_usindex(self):
        """
        Extracts a list of stock symbols from the 'usindex' table.

        This method executes a SQL query that retrieves stock symbols 
        ('symbol') from the 'stocksymbol' table. It only selects symbols for 
        stock IDs ('stock_id') in the 'usindex' table.

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
                """
                SELECT ss.symbol, ss.id 
                FROM stocksymbol ss
                INNER JOIN usindex ON usindex.stock_id = ss.id;
                """)

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

    def get_companyprofiles_by_column(self, column: str) -> pd.DataFrame:
        """
        Retrieves a pandas DataFrame containing the values of a specified 
        column, a list of stock IDs, and the count of stock IDs from the 
        companyprofile table, filtered by companies that are actively trading, 
        and are neither ETFs nor funds. The rows are grouped by the specified 
        column and ordered by the count of stock IDs.

        This method executes a SQL query on the companyprofile table, 
        leveraging SQLAlchemy for database interaction. It ensures transaction 
        integrity by handling exceptions and rolling back the transaction if 
        necessary. The database session is closed in all cases, ensuring no 
        resources are leaked.

        Args:
            column (str): The name of the column in the companyprofile table to 
            retrieve and group by in the resulting DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame with three columns: the specified 
            column name, 'list_stock_ids' (a list of stock IDs for each group), 
            and 'count_stock_ids' (the count of stock IDs in each group). The 
            DataFrame is ordered by 'count_stock_ids'.

        Raises:
            RuntimeError: An error occurred during the database transaction or 
            query execution. The original SQLAlchemyError is wrapped in this 
            RuntimeError, and the database session is rolled back and closed 
            before re-raising the error.

        """
        try:
            query = text(f"""
            SELECT {column}, 
                   ARRAY_AGG(stock_id) AS list_stock_ids,
                   COUNT(stock_id) AS count_stock_ids
            FROM companyprofile
            WHERE is_actively_trading IS TRUE
                  AND is_etf IS FALSE 
                  AND is_fund IS FALSE
            GROUP BY {column}
            ORDER BY count_stock_ids;
            """)

            data = self.db_session.execute(query).fetchall()

            return pd.DataFrame(data, columns=[column, 'list_stock_ids', 'count_stock_ids'])

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_index_by_company_profile(self, index: str) -> pd.DataFrame:
        """
        Retrieves a pandas DataFrame containing all records from the 'sxxp' 
        table joined with the 'companyprofile' table on the 'stock_id' column. 
        This join operation includes all columns from both tables, providing a 
        comprehensive view of the STOXX Europe 600 index companies along with 
        their profiles.

        Args:
            index (str): The name of the table with index constituents, 'sxxp' or 'usindex'.

        Returns:
            pd.DataFrame: A pandas DataFrame comprising all fields from the 
            'sxxp' and 'companyprofile' tables, merged on the 'stock_id'. 

        Raises:
            RuntimeError: An error occurred during the database transaction or 
            query execution. This exception wraps the original SQLAlchemyError, 
            ensuring that the database session is rolled back and closed before 
            re-raising the error.

        """
        try:
            query = text(f"""
            SELECT * FROM {index}
            LEFT JOIN companyprofile 
                ON {index}.stock_id = companyprofile.stock_id;
            """)

            data = self.db_session.execute(query).fetchall()

            return pd.DataFrame(data)

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_dailychart_missing_update(self) -> pd.DataFrame:
        """
        Retrieves a list of stock_ids from the `dailychart` table that have not 
        been updated to the latest date, alongside their most recent update 
        date and active trading status from the `companyprofile` table.

        Args:
            None

        Returns:
            pd.DataFrame: A DataFrame containing three columns: `stock_id`, 
            `max_date`, and `is_actively_trading`.

        Raises:
            RuntimeError: If an error occurs during the execution of the query, 
            including issues related to the database connection or the query 
            execution itself. The error is logged, and a runtime error is 
            raised with the original error message.

        """
        min_date = (datetime.now() - timedelta(365)).strftime('%Y-%m-%d')

        try:
            query = text(f"""
            WITH MaxDate AS (
                SELECT MAX(date) AS overall_max_date
                FROM dailychart
                WHERE date > '{min_date}'
            ), LatestStockDates AS (
                SELECT stock_id, MAX(date) AS max_date
                FROM dailychart
                WHERE date > '{min_date}'
                GROUP BY stock_id
            )
            SELECT lsd.stock_id, lsd.max_date, cp.is_actively_trading
            FROM LatestStockDates lsd
            LEFT JOIN companyprofile cp ON lsd.stock_id = cp.stock_id
            WHERE lsd.max_date < (SELECT overall_max_date FROM MaxDate);
            """)

            data = self.db_session.execute(query).fetchall()

            return pd.DataFrame(data)

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_table_missing_value_by_column(self, table: str, column: str,
        years: int = 1) -> pd.DataFrame:
        """
        Retrieves a list of action identifiers ('stock_id') from a stock table 
        which has at least one null value in the specified column.

        The function dynamically incorporates the specified column name into 
        the SQL query to perform the aggregation and calculations. It filters 
        records based on a minimum date set to one year from the current date.

        Args:
            table (str) : The name of the table.
            column (str): The name of the column to check for zero values.
            years (int) : The number of years back compared to today.

        Returns:
            pd.DataFrame: A DataFrame with each row containing:
                        - stock_id: The unique identifier of the stock.
                        - zero_{column}_count: The count of records where the 
                        specified column has a zero value.
                        - total_count: The total number of records for the stock_id.
                        - is_actively_trading: A boolean indicating if the 
                        stock is currently actively trading.
                        - percentage: The percentage of zero-value records for 
                        the specified column relative to the total count of records.

        Raises:
            RuntimeError: If an error occurs during query execution, such as a 
            database connection issue or a problem with the query syntax. The 
            transaction is rolled back and the session is closed before raising 
            the error.

        """
        min_date = (datetime.now() - timedelta(years * 365)).strftime('%Y-%m-%d')
        max_date = datetime.now().strftime('%Y-%m-%d')

        try:
            query = text(f"""
            SELECT 
                ta.stock_id, 
                SUM(CASE WHEN ta.{column} = 0 THEN 1 ELSE 0 END) AS zero_column_count,
                COUNT(ta.id) AS total_count,
                cp.is_actively_trading,
                (SUM(CASE WHEN ta.{column} = 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(ta.id)) * 100 AS percentage
            FROM 
                {table} ta
            LEFT JOIN 
                companyprofile cp ON ta.stock_id = cp.stock_id
            WHERE 
                ta.date > '{min_date}' AND ta.date <= '{max_date}'
            GROUP BY 
                ta.stock_id, 
                cp.is_actively_trading
            HAVING 
                SUM(CASE WHEN ta.{column} = 0 THEN 1 ELSE 0 END) > 0
            ORDER BY 
                percentage DESC;
            """)

            data = self.db_session.execute(query).fetchall()

            return pd.DataFrame(data)

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_dailychart_finding_gap_by_stock(self, stock_id: int) -> pd.DataFrame:
        """
        Retrieves dates within the last year for which there are no daily chart 
        records for the specified stock.

        This function queries a database for dates from the last 365 days up to 
        the most recent date in the `dailychart` table for a given stock ID. It 
        identifies any dates for which there is no corresponding daily chart 
        record for the stock, indicating a "gap" in the data.

        Args:
            stock_id (int): The unique identifier for the stock of interest.

        Returns:
            pd.DataFrame: A DataFrame containing the dates (as `missing_date`) 
            for which there are no daily chart records for the specified stock.

        Raises:
            RuntimeError: An error occurred during the database query or 
            transaction, which includes the original error message.

        """
        min_date = (datetime.now() - timedelta(365)).strftime('%Y-%m-%d')

        try:
            query = text(f"""
            WITH expected_dates AS (
                SELECT b.date
                FROM businessdate b
                WHERE b.date >= '{min_date}'
                AND b.date <= (SELECT MAX(d.date) FROM dailychart d WHERE d.stock_id = {stock_id})
            ),
            actual_dates AS (
                SELECT d.date
                FROM dailychart d
                WHERE d.stock_id = {stock_id}
            )
            SELECT e.date AS missing_date
            FROM expected_dates e
            LEFT JOIN actual_dates a ON e.date = a.date
            WHERE a.date IS NULL
            ORDER BY e.date;
            """)

            data = self.db_session.execute(query).fetchall()

            return pd.DataFrame(data)

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_keymetrics_columns(self) -> list:
        """
        Retrieves the column names from the 'keymetrics' table in the database.

        This method executes a SQL query to fetch all column names from the 
        'keymetrics' table within the connected database. It utilizes the 
        database session associated with the instance to perform the query.

        Args:
            None

        Returns:
            list: A list of strings where each string represents a column name in the
                'keymetrics' table.

        Raises:
            RuntimeError: An error occurs during the execution of the query or 
            fetching of results. The original error message from SQLAlchemy is 
            included in the raised RuntimeError exception.
        """
        try:
            query = text("""
            SELECT COLUMN_NAME 
            FROM information_schema.columns 
            WHERE table_name = 'keymetrics'
            """)

            data = self.db_session.execute(query).fetchall()

            column_list = [column[0] for column in data]

            return column_list

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_table_date(self, table: str) -> pd.DataFrame:
        """
        Retrieves the most recent date by stock ID from a specified database 
        table and returns them as a pandas DataFrame with the dates converted 
        to datetime objects.

        This function executes a SQL query to select all last date entries from 
        the specified table. It then fetches the results, converts them into a 
        pandas DataFrame, and ensures the 'max_date' column is in datetime format. 

        Args:
            table (str): The name of the database table from which to retrieve the dates.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the dates from the 
            specified table, with the dates converted to datetime objects.

        Raises:
            RuntimeError: If an error occurs during the execution of the query 
            or the handling of the database session. The original error from 
            SQLAlchemy is included in the RuntimeError exception message.

        """
        try:
            # Inspect table columns
            inspector = inspect(self.db_session.bind)
            if 'date' not in [column['name'] for column in inspector.get_columns(table)]:
                raise ValueError(f"The specified table '{table}' does not contain a 'date' column.")

            # Proceed with the original query if the 'date' column exists
            query = text(f"""
            SELECT ta.stock_id, MAX(ta.date) AS max_date
            FROM {table} ta
            INNER JOIN 
                companyprofile cp ON ta.stock_id = cp.stock_id
            WHERE cp.is_actively_trading is True
            GROUP BY ta.stock_id
            ORDER BY max_date DESC
            """)
            data = self.db_session.execute(query).fetchall()

            df = pd.DataFrame(data)
            df['max_date'] = pd.to_datetime(df['max_date'])

            return df

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_table_performance(self, table_name: str):
        """
        Measures the performance of a specified database table in terms of 
        query response time and disk space usage. It first checks if the given 
        table is a hypertable in a TimescaleDB environment and accordingly 
        measures the disk space used. It also measures the time taken to 
        execute a simple SELECT query on the table.

        Args:
            table_name (str): The name of the table for which performance 
            metrics are to be measured.

        Returns:
            tuple: A tuple containing four elements:
                - the date and time of the query (datetime)
                - the name of the table (str)
                - table is a TimescaleDB hypertable (bool)
                - execution_time (float): The time taken to execute the SELECT 
                query, rounded to 4 decimal places.
                - disk_space (str): The disk space used by the table, formatted 
                as a human-readable string (e.g., "10 MB").

        Raises:
            RuntimeError: If any database operation fails, it raises a 
            RuntimeError with information about the specific SQLAlchemyError.

        """
        try:
            # Measuring query response time
            start_time = time.time()

            # Sample SQL query to measure execution time on a small data sample
            query_rt = text(f"""
            SELECT * FROM {table_name} TABLESAMPLE BERNOULLI (1)  -- 1% of table
            """)
            result_rt = self.db_session.execute(query_rt) # pylint: disable=unused-variable

            # Calculate execution time
            execution_time = round(time.time() - start_time, 4)

            # Check if the table is already a hypertable
            hypertable = False
            hypertable_check = text(
                "SELECT * FROM _timescaledb_catalog.hypertable WHERE table_name = :table_name")
            if self.db_session.execute(
                hypertable_check, {'table_name': table_name}).fetchone() is not None:
                hypertable = True
                # Measuring the disk space used by a TimescaleDB table
                query_ds = text(f"""
                SELECT pg_size_pretty(hypertable_size('public.{table_name}'));
                """)
            else :
                # Measuring the disk space used by a normal table
                query_ds = text(f"""
                SELECT pg_size_pretty(pg_total_relation_size('public.{table_name}'))
                """)

            # Get the disk space used by the table
            result_ds = self.db_session.execute(query_ds).fetchone()

            # Get the number of rows in the table
            row_count = self.db_session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()

            # Get the number of columns in the table
            column_count = self.db_session.execute(text(f"""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND table_schema = 'public'
            """)).scalar()

            return (datetime.now(), table_name, hypertable, row_count,
                column_count, execution_time, result_ds[0])

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def get_list_of_tables(self) -> list:
        """
        Retrieves a list of table names from the 'public' schema of the 
        database. This method executes a query to fetch all table names 
        available in the 'public' schema and returns them as a list.

        Args:
            None

        Returns:
            list: A list of strings, where each string is the name of a table 
            within the 'public' schema of the connected database.

        Raises:
            RuntimeError: If any issues occur during the database operation, 
            including connection issues or SQL execution problems. The error 
            raised will contain a message from the underlying SQLAlchemyError 
            that caused the failure.

        """
        try:
            query = text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public';
            """)

            data = self.db_session.execute(query).fetchall()

            table_list = [table[0] for table in data]

            return table_list

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def fetch_sql_query_as_dataframe(self, query_text: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the results as a pandas DataFrame.

        This method executes a given SQL query using the active database 
        session and returns the results in a pandas DataFrame. The DataFrame 
        will have columns corresponding to the SQL query output.
        If an error occurs during the execution of the query, the transaction 
        is rolled back and the session is closed before raising an error. The 
        session is also closed upon successful completion of the query.

        Args:
            query_text (str): The SQL query to execute.

        Returns:
            pd.DataFrame: A DataFrame containing the results of the SQL query.

        Raises:
            RuntimeError: An error occurs during the query execution or during session handling.
        
        """
        try:
            query = text(query_text)
            result = self.db_session.execute(query)

            # Create a DataFrame from the result set
            df = pd.DataFrame(result.fetchall())
            # This sets the column headers to the names of the SQL columns
            df.columns = result.keys()

            return df

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def fetch_stock_dictionary(self) -> dict[int, list[str]]:
        """Fetches stock data and returns it as a dictionary.

        This function executes a SQL query that retrieves stock identifiers, 
        names, symbols, and ISINs from a database. It right joins the 
        `stocksymbol` table with the `sxxp` table on stock id. The data is then 
        converted into a dictionary where each key is the stock id and the 
        value is a list containing the stock name, symbol, and ISIN.

        Returns:
            dict[int, list[str]]: A dictionary mapping stock ids to a list of 
            attributes (name, symbol, ISIN).

        Raises:
            RuntimeError: If an error occurs during the database operation.

        """
        try:
            query = text("""
            SELECT ss.id, ss.name, ss.symbol, sxxp.isin, NULL AS cik
            FROM stocksymbol ss
            RIGHT JOIN sxxp ON ss.id = sxxp.stock_id

            UNION ALL

            SELECT ss.id, ss.name, ss.symbol, NULL AS isin, usindex.cik
            FROM stocksymbol ss
            RIGHT JOIN usindex ON ss.id = usindex.stock_id;
            """)

            data = self.db_session.execute(query).fetchall()

            # Creating the dictionary from fetched data
            stock_dict = {item.id: [item.name, item.symbol, item.isin, item.cik] for item in data}

            return stock_dict

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def fetch_dailychart_data(self, stock_id: int, start_date: str) -> pd.DataFrame :
        """
        Retrieves daily chart data from a database for a specified stock 
        starting from a given date.

        This function queries a database table 'dailychart' to fetch all 
        entries for a given stock ID that are on or after a specified start 
        date. The data is returned as a pandas DataFrame. If the query does not 
        return any results, an empty DataFrame with appropriate column names is 
        returned.

        Args:
            stock_id (int): The ID of the stock for which to retrieve chart data.
            start_date (str): The starting date from which to retrieve the data (inclusive).

        Returns:
            pd.DataFrame: A DataFrame containing the queried daily chart data. 
            The DataFrame will have columns corresponding to the database table structure.

        Raises:
            RuntimeError: If an error occurs during database access, the error 
            is logged and a runtime error with the error message is raised. 
            Also includes a rollback of the database transaction to avoid 
            corrupt data.

        """
        try:
            query = text(f"""
            SELECT * FROM dailychart
            WHERE stock_id = {stock_id}
                AND date >= '{start_date}' 
            """)

            result = self.db_session.execute(query)
            fetched_data = result.fetchall()  # Fetch data once to avoid cursor exhaustion

            # Check if fetched data is not empty
            if fetched_data:
                df = pd.DataFrame(fetched_data)
                df.columns = result.keys()  # Set columns only if data is fetched
            else:
                df = pd.DataFrame(columns=result.keys())  # Create an empty df with column names

            return df

        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback the transaction in case of an error
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            self.db_session.close()  # Close session in all cases (on success or failure)

    def fetch_stock_data_from_table(self, sql_table: str, stock_id: int) -> pd.DataFrame:
        """
        Fetches data for a specified stock ID from a database table.

        This method retrieves all entries from the table where the stock_id 
        matches the provided stock_id. The function executes a SQL query, 
        fetches the result, and converts it into a pandas DataFrame. If 
        no data is found, it returns an empty DataFrame with the appropriate 
        column headers. Any SQL-related errors trigger a rollback, and the
        session is closed after fetching the data or upon an error.

        Args:
            sql_table (str) : The name of the SQL table
            stock_id (int): The ID of the stock for which to retrieve data.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched data. Columns 
            correspond to those in the database table. The DataFrame will be 
            empty if no records are found.

        Raises:
            RuntimeError: An error occurs during the database query or 
            transaction, such as connection issues or SQL syntax errors. The 
            error message from SQLAlchemy is included in the raised 
            RuntimeError.

        """
        try:
            query = text(f"""
            SELECT * FROM {sql_table}
            WHERE stock_id = {stock_id} 
            """)

            result = self.db_session.execute(query)
            fetched_data = result.fetchall()  # Fetch data once to avoid cursor exhaustion

            # Check if fetched data is not empty
            if fetched_data:
                df = pd.DataFrame(fetched_data)
                df.columns = result.keys()  # Set columns only if data is fetched
            else:
                df = pd.DataFrame(columns=result.keys())  # Create an empty df with column names

            return df

        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback the transaction in case of an error
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            self.db_session.close()  # Close session in all cases (on success or failure)

    def fetch_companyprofile_data(self) -> pd.DataFrame:
        """Fetches STOXX Europe 600 and US indexes company profiles.

        This function executes a SQL query that retrieves stock identifiers, 
        currency, sector and country  from a database. It right joins the 
        `companyprofile` table with the `sxxp` and `usindex` tables on stock 
        ID. The data is then converted into a DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched data. Columns 
            correspond to those in the database table.

        Raises:
            RuntimeError: If an error occurs during the database operation.

        """
        try:
            query = text("""
            SELECT cp.stock_id, currency, sector, country
            FROM companyprofile cp
            RIGHT JOIN sxxp ON cp.stock_id = sxxp.stock_id
                
            UNION ALL

            SELECT cp.stock_id, currency, sector, country
            FROM companyprofile cp
            RIGHT JOIN usindex ON cp.stock_id = usindex.stock_id;
            """)

            result = self.db_session.execute(query)
            fetched_data = result.fetchall()

            df = pd.DataFrame(fetched_data)
            df.columns = result.keys()

            return df

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def fetch_sector_study_data(self, setting: dict) -> pd.DataFrame:
        """
        Fetches and returns a DataFrame containing stock and key metrics data 
        for a specified sector, filtered by country and currency using given 
        settings.

        This function constructs and executes a SQL query based on the provided 
        settings which include a list of countries, currencies, a sector, and 
        specific metrics. The result is converted into a DataFrame before being 
        returned. If an error occurs during the database operation, it raises
        a RuntimeError and rolls back the transaction.

        Args:
            setting (dict): A dictionary containing:
                - country (list of str): List of countries to filter the data.
                - currency (list of str): List of currencies to filter the data.
                - sector (str): The sector to filter the data.
                - metric_x (str): The specific key metric to be included in the output as a column.
                - metric_y (str): Another specific key metric to be included in 
                the output as a column.
                - metric_size (str): A third key metric to be included in the output as a column.

        Returns:
            pd.DataFrame: A DataFrame containing the query results with columns 
            for each stock symbol and the specified metrics. The DataFrame will 
            have columns if data is fetched; otherwise, it will be empty but 
            with column names set.

        Raises:
            RuntimeError: An error that encapsulates any exceptions thrown 
            during the execution, typically database-related errors like 
            connection or syntax issues in the SQL.

        """
        try:
            # Prepare country and currency lists for SQL IN clause
            country_list = ", ".join([f"'{country}'" for country in setting['country']])
            currency_list = ", ".join([f"'{currency}'" for currency in setting['currency']])

            # Construct the SQL query using safe string formatting
            query = text(f"""
            SELECT 
                stocksymbol.id,
                stocksymbol.symbol,
                stocksymbol.name,
                companyprofile.country,
                companyprofile.currency,
                keymetrics.date,
                keymetrics.period,
                keymetrics.{setting['metric_x']},
                keymetrics.{setting['metric_y']},
                keymetrics.{setting['metric_size']}
            FROM 
                stocksymbol
            JOIN 
                companyprofile ON stocksymbol.id = companyprofile.stock_id
            JOIN 
                keymetrics ON stocksymbol.id = keymetrics.stock_id
            WHERE 
                companyprofile.sector = '{setting['sector']}'
                AND companyprofile.country IN ({country_list})
                AND companyprofile.currency IN ({currency_list});

            """)

            result = self.db_session.execute(query)
            fetched_data = result.fetchall()  # Fetch data once to avoid cursor exhaustion

            # Check if fetched data is not empty
            if fetched_data:
                df = pd.DataFrame(fetched_data)
                df.columns = result.keys()  # Set columns only if data is fetched
            else:
                df = pd.DataFrame(columns=result.keys())  # Create an empty df with column names

            return df

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()

    def fetch_dividend_paying_companies(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches a list of dividend-paying companies within a specified date range.

        This method queries a database to retrieve the dates and corresponding 
        stock names of companies that paid dividends within the given date 
        range. The data is aggregated by date and sorted in descending order. 
        This function handles database session management, ensuring the session 
        is closed after execution, whether successful or not.

        Args:
            start_date (str): The start date for the query range, formatted as 
            'YYYY-MM-DD'.
            end_date (str): The end date for the query range, formatted as 
            'YYYY-MM-DD', exclusive.

        Returns:
            pd.DataFrame: A DataFrame containing the dates and corresponding 
            lists of stock names that paid dividends. If no data is found, 
            returns an empty DataFrame with appropriate column names.

        Raises:
            RuntimeError: An error occurs during the database operation. The 
            error from the database is caught as an SQLAlchemyError, and a more 
            generic RuntimeError is raised, with the original error included 
            for debugging.

        """
        try:
            # Construct the SQL query using safe string formatting
            query = text(f"""
            SELECT 
                d.date,
                ARRAY_AGG(s.name) AS list_stock_names
            FROM 
                dividend d
            JOIN 
                stocksymbol s ON d.stock_id = s.id
            WHERE 
                d.date >= '{start_date}' AND d.date < '{end_date}'
            GROUP BY 
                d.date 
            ORDER BY 
                d.date DESC;
            """)

            result = self.db_session.execute(query)
            fetched_data = result.fetchall()  # Fetch data once to avoid cursor exhaustion

            # Check if fetched data is not empty
            if fetched_data:
                df = pd.DataFrame(fetched_data)
                df.columns = result.keys()  # Set columns only if data is fetched
            else:
                df = pd.DataFrame(columns=result.keys())  # Create an empty df with column names

            return df

        except SQLAlchemyError as e:
            # Rollback the transaction in case of an error
            self.db_session.rollback()
            raise RuntimeError(f"An error occurred: {e}") from e

        finally:
            # Close session in all cases (on success or failure)
            self.db_session.close()
