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
