#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-12

@author: Roland VANDE MAELE

@abstract: this function converts a table into a TimescaleDB hypertable.

"""

import os
import subprocess
from dotenv import load_dotenv
from sqlalchemy import text, exc
from src.models.base import Session

load_dotenv()

def convert_table_to_hypertable(table_name):
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

    except exc.SQLAlchemyError as e:
        # Rollback the transaction in case of an error
        db_session.rollback()
        raise(f"An error occurred: {e}") from e

def backup_database(output_file):
    """
    Performs a full backup of a PostgreSQL database using environment variables 
    to configure the connection and output settings.

    The function retrieves database connection parameters from the environment, 
    constructs a `pg_dump` command, and executes it. If the command fails, it 
    raises an exception with details of what went wrong.

    Args:
        output_file (str): The path where the backup SQL file will be saved.

    Returns:
        str: A message indicating that the database backup was successful.

    Raises:
        RuntimeError: An error with details if the backup process fails.

    Environment Variables:
        DB_PASSWORD (str): The password for the PostgreSQL database user.
        DB_HOST (str): The hostname of the PostgreSQL server.
        DB_PORT (str): The port on which the PostgreSQL server is running.
        DB_USER (str): The username used to connect to the database.
        DB_NAME (str): The name of the database to back up.

    """
    # Set up the environment with the password
    env = dict(os.environ, PGPASSWORD=os.getenv('DB_PASSWORD'))

    # Prepare the pg_dump command
    command = [
        'pg_dump',
        '-h', os.getenv('DB_HOST'),
        '-p', str(os.getenv('DB_PORT')),
        '-U', os.getenv('DB_USER'),
        '-d', os.getenv('DB_NAME'),
        '-F', 'p',
        '-f', output_file,
        '--encoding', 'UTF8'
    ]

    # Run the command
    try:
        subprocess.run(command, env=env, check=True)
        return "Database backup was successful."
    except subprocess.CalledProcessError as e:
        raise(f"An error occurred while making the database backup : {e}") from e
