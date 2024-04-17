#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-11

@author: Roland VANDE MAELE

@abstract: this file is intended for functions processing dates

"""

import datetime
import holidays
from sqlalchemy import Table, Column, Date, MetaData
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from src.models.base import engine
from src.services.sql import convert_table_to_hypertable


def parse_date(date_str):
    """
    Attempts to convert a string into a date object according to several formats.

    This function attempts to parse the given string (`date_str`) using several
    date formats. If the string can be correctly converted to a date in one of 
    the formats, the function returns the corresponding date object. If no 
    format matches, or if another error occurs error occurs, the function 
    returns `None`.

    Args:
        date_str (str): The string representing the date to be parsed.

    Returns:
        datetime.date | None: The date object resulting from successful 
        parsing, or `None` if parsing fails.

    Examples:
        >>> parse_date("2023-03-11")
        datetime.date(2023, 3, 11)
        >>> parse_date("11/03/2023")
        datetime.date(2023, 3, 11)
        >>> parse_date("not a date")
        None

    Note:
        Currently supported date formats are "%Y-%m-%d" (e.g. "2023-03-11"), 
        "%d/%m/%Y" (e.g. "11/03/2023") and "%Y%m%d" (e.g. "20230311").

    """
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def generate_business_time_series():
    """
    Generates a time series of business dates excluding weekends and holidays 
    specific to France, inserts them into a database, and converts the table 
    into a TimescaleDB hypertable.

    This function defines a date range from January 1, 1985 to December 31, 
    2030. It generates a list of business dates within this range, excluding 
    weekends and French financial holidays. These dates are then inserted into 
    a specified table in the database. After insertion, the table is converted 
    into a TimescaleDB hypertable for efficient time-series data handling.

    Args:
        None

    Returns:
        None

    Raises:
        Exception: If any database operation fails, the transaction is rolled back.

    """
    try:
        table = 'businessdate'

        # Define the date range
        start_date = datetime.date(1985, 1, 1)
        end_date = datetime.date(2030, 12, 31)

        # Get holidays in the range
        fr_holidays = holidays.financial_holidays('FR')

        # Generate business dates, excluding weekends and holidays
        business_dates = [
            current_date
            for current_date in (start_date + datetime.timedelta(n) for n in range(
                (end_date - start_date).days + 1))
            if current_date.weekday() < 5 and current_date not in fr_holidays
        ]

        # Define metadata object
        metadata = MetaData()

        # Define the table
        business_dates_table = Table(table, metadata,
                                Column('date', Date, primary_key=True),)

        # Create the table in the database
        metadata.create_all(engine)

        # Convert table into TimescaleDB hypertable
        convert_table_to_hypertable(table)

        # Insert business dates into the database
        with engine.connect() as connection:
            # Use transaction to rollback in case of any error
            with connection.begin():
                for business_date in business_dates:
                    connection.execute(
                        business_dates_table.insert().values(date=business_date)
                    )
        # print("Business dates inserted successfully.")

    except IntegrityError as e:
        raise(f"Integrity error occurred: {e}") from e
    except OperationalError as e:
        raise(f"Operational error with the database: {e}") from e
    except SQLAlchemyError as e:
        # Catching other SQLAlchemy-related errors
        raise(f"Database error occurred: {e}") from e
