#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-12

@author: Roland VANDE MAELE

@abstract: this function converts a table into a TimescaleDB hypertable.

"""

from sqlalchemy import text, exc
from src.models.base import Session


def convert_stock_table_to_hypertable(table_name):
    """
    Converts a specified PostgreSQL table into a TimescaleDB hypertable, 
    handling the necessary preliminary steps, and recreates necessary 
    constraints after the conversion.
    
    This function checks first if the given table is already a hypertable to 
    prevent conversion attempts on hypertables, which could lead to crashes. It 
    then retrieves all indexes associated with the given table, drops any 
    constraints and indexes to avoid interference with the hypertable 
    conversion process, and converts the table into a TimescaleDB hypertable 
    based on the 'date' column. After the conversion, it attempts to recreate 
    the necessary constraints for the table.

    Args:
        table_name (str): The name of the table to be converted into a 
        hypertable.

    Returns:
        None

    Raises:
        exc.SQLAlchemyError: Catches any SQLAlchemy related exceptions that 
        occur during the execution of the function, rolls back the session to 
        its previous state before the function execution, and prints an error 
        message.

    Note:
        - Make sure that the TimescaleDB extension is installed and enabled in 
        the PostgreSQL database before calling this function.

    """
    db_session = Session()

    try:
        # Check if the table is already a hypertable
        hypertable_check = text(
            "SELECT * FROM _timescaledb_catalog.hypertable WHERE table_name = :table_name")
        if db_session.execute(
            hypertable_check, {'table_name': table_name}).fetchone() is not None:
            print(f"Table {table_name} is already a hypertable. No action taken.")
            return

        # Retrieve all indexes for the specified table
        index_query = text("SELECT indexname FROM pg_indexes WHERE tablename = :table_name")
        indexes = db_session.execute(index_query, {'table_name': table_name}).fetchall()

        # Drop constraints and indexes that might interfere with hypertable conversion
        for index in indexes:
            index_name = index[0]
            db_session.execute(text(
                f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {index_name}"))
            db_session.execute(text(
                f"DROP INDEX IF EXISTS {index_name}"))

        db_session.commit()

        # Convert the table into a TimescaleDB hypertable
        db_session.execute(text(
            "SELECT create_hypertable(:table_name, 'date')"), {'table_name': table_name})

        # Recreate necessary constraints after hypertable conversion
        for index in indexes:
            index_name = index[0]
            if 'pkey' not in index_name:
                db_session.execute(
                    text(f"ALTER TABLE {table_name} ADD CONSTRAINT {index_name} UNIQUE (stock_id, date)")) # pylint: disable=line-too-long

        db_session.commit()
        print(f"Table {table_name} has been successfully converted to a hypertable and constraints have been recreated.") # pylint: disable=line-too-long

    except exc.SQLAlchemyError as e:
        # Rollback the transaction in case of an error
        db_session.rollback()
        print(f"An error occurred: {e}")
