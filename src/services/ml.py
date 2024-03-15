#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-12

@author: Roland VANDE MAELE

@abstract: this file contains functions for prepare and run machine learning.

"""

import pandas as pd
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def detection_and_exclusion_of_outliers_ee(df, variable: str,
    contamination: float = 0.01) -> pd.DataFrame:
    """
    Identifies and excludes outliers for a specified variable in the DataFrame 
    using the EllipticEnvelope method (models that assume a normal distribution of data).

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        variable (str): The name of the column for which outliers should be 
        detected and excluded.
        contamination (float, optional): The proportion of observations to be 
        considered as outliers. Defaults to 0.01.

    Returns:
        pandas.DataFrame: A new DataFrame with outliers excluded from the 
        specified variable.

    Raises:
        ValueError: If the specified variable is not found in the DataFrame.
    """

    if variable not in df.columns:
        raise ValueError(f"Variable '{variable}' not found in the DataFrame.")

    # Initialize and fit the EllipticEnvelope
    envelope = EllipticEnvelope(contamination=contamination)
    envelope.fit(df[[variable]])

    # Predict the outliers (-1 for outliers, 1 for inliers)
    outliers = envelope.predict(df[[variable]])

    # Create a mask for inliers (non-outliers)
    inliers_mask = outliers == 1

    # Return a new DataFrame without the outliers
    return df[inliers_mask]

def detection_and_exclusion_of_outliers_if(df, variable: str,
    contamination: float = 0.01) -> pd.DataFrame:
    """
    Identifies and excludes outliers for a specified variable in the DataFrame 
    using the IsolationForest method (works well on data with asymmetric distributions)

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        variable (str): The name of the column for which outliers should be 
        detected and excluded.
        contamination (float, optional): The proportion of observations to be 
        considered as outliers. Defaults to 0.01.

    Returns:
        pandas.DataFrame: A new DataFrame with outliers excluded from the 
        specified variable.

    Raises:
        ValueError: If the specified variable is not found in the DataFrame.
    """

    if variable not in df.columns:
        raise ValueError(f"Variable '{variable}' not found in the DataFrame.")

    # Initialize, fit and predict the IsolationForest
    iso_forest = IsolationForest(contamination=contamination)
    outliers = iso_forest.fit_predict(df[[variable]])

    # Filter outliers (considered -1 by Isolation Forest)
    df_filtered = df[outliers != -1]

    # Return a new DataFrame without the outliers
    return df_filtered

def normalize_data(df, columns_to_normalize: list) -> pd.DataFrame:
    """
    Normalizes the numerical columns of DataFrame.

    This function applies standard normalization to the numerical columns of 
    the DataFrame, which re-scales the features to have a mean of 0 and a 
    standard deviation of 1. This step is crucial for many machine learning 
    algorithms to perform correctly.

    Args:
        df (pd.DataFrame): The DataFrame containing data.
        columns_to_normalize (list): A list of column names to be normalized.

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input, where the 
        numerical data has been normalized.

    Raises:
        ValueError: If any of the columns to normalize are not found in the DataFrame.

    """
    # Check if all specified variables exist in the DataFrame
    missing_cols = [col for col in columns_to_normalize if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Variables {missing_cols} not found in the DataFrame.")

    # Work on a copy of the DataFrame to avoid SettingWithCopyWarning
    df_copy = df.copy()

    # Initialize the scaler
    scaler = StandardScaler()

    # Fit the scaler to the data and transform it
    df_copy[columns_to_normalize] = scaler.fit_transform(
                                    df_copy[columns_to_normalize])

    return df_copy
