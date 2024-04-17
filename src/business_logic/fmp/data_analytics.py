#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-14

@author: Roland VANDE MAELE

@abstract: this additional level of abstraction means that data can be 
manipulated and business operations performed without direct concern for the 
implementation details of data retrieval or database interaction.

"""

import numpy as np
import pandas as pd


def clean_data_for_company_profiles_clustering(data):
    """
    Cleans the company profiles data for clustering analysis.

    This function takes raw company profiles data and performs several cleaning 
    operations to prepare it for clustering analysis. The steps include 
    replacing zero values with NaN for subsequent removal, dropping rows with 
    any missing values, removing duplicate entries, and ensuring that each 
    column is of the correct data type.

    Args:
        data (list of tuples): Raw data to be cleaned. Each element of the list 
        represents a row of data, and should include values for 'stock_id', 
        'beta', 'vol_avg', and 'mkt_cap' in this order.

    Returns:
        pd.DataFrame: A cleaned DataFrame with the columns ['stock_id', 'beta', 
        'vol_avg', 'mkt_cap'].

    Raises:
        ValueError: If there are issues in data type conversion.

    """
    # Convert data into a pandas DataFrame
    columns = ['stock_id', 'beta', 'vol_avg', 'mkt_cap']
    df = pd.DataFrame(data, columns=columns)

    # Replace zeros with NaN and drop rows with any NaN values
    df.replace(0, np.nan, inplace=True)
    df = df.dropna()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Ensure correct data types for each column
    try:
        df['stock_id'] = df['stock_id'].astype(int)
        df['beta'] = df['beta'].astype(float)
        df['vol_avg'] = df['vol_avg'].astype('Int64')
        df['mkt_cap'] = df['mkt_cap'].astype('Int64')
    except ValueError as e:
        # This handles potential issues in type conversion
        raise ValueError("Data type conversion failed.") from e

    return df
