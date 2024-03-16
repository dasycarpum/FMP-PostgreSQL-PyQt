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
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score


def detection_and_exclusion_of_outliers_ee(df: pd.DataFrame, variable: str,
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

def detection_and_exclusion_of_outliers_if(df: pd.DataFrame, variable: str,
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

def normalize_data(df: pd.DataFrame, columns_to_normalize: list) -> pd.DataFrame:
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

def determine_cluster_numbers_with_kmeans(df: pd.DataFrame) -> dict:
    """
    Determines the optimal number of clusters for KMeans clustering.

    This function evaluates the silhouette score for a range of cluster numbers 
    to determine the optimal number of clusters for KMeans clustering. The 
    silhouette score is used as a metric to judge the distance between the 
    resulting clusters. The function iterates over a predefined range of 
    cluster numbers, computes the KMeans clustering for each, and calculates 
    the silhouette score.

    Args:
        df (pd.DataFrame): The normalized dataset used for clustering. This 
        should be a 2D array or DataFrame where rows represent samples and 
        columns represent features.

    Returns:
        dict: A dictionary with the number of clusters as keys and the 
        corresponding silhouette scores as values. This allows for easy 
        identification of the cluster number with the highest silhouette score, 
        which is considered the optimal number of clusters.

    Example:
        >>> data_normalized = np.array([[0.1, 0.2], [0.4, 0.2], [0.1, 0.5], [0.3, 0.3]])
        >>> determine_optimal_number_of_clusters_kmeans(data_normalized)
        {2: 0.5, 3: 0.45, 4: 0.35, 5: 0.3}
    """

    scores = {}

    # Define the range of cluster numbers to evaluate
    range_values = range(2, 6)

    for i in range_values:
        kmeans = KMeans(n_clusters=i, random_state=0)  # Initialize KMeans with i clusters
        kmeans.fit(df)  # Fit KMeans model to the normalized data
        score = silhouette_score(df, kmeans.labels_)
        scores[i] = score  # Store the score in the dictionary

    return scores

def apply_kmeans_clustering(df: pd.DataFrame, scores: dict) -> pd.DataFrame:
    """
    Applies KMeans clustering to the normalized data and adds a cluster label.

    This function finds the optimal number of clusters based on the given 
    silhouette scores, applies KMeans clustering to the normalized dataset with 
    this optimal number of clusters, and assigns the cluster labels to the data.

    Args:
        df (pd.DataFrame): The normalized dataset on which 
        clustering will be applied. It should be a DataFrame for this function 
        to work correctly.
        scores (dict): A dictionary containing the number of clusters as keys 
        and the corresponding silhouette scores as values.

    Returns:
        pd.DataFrame: The original normalized dataset with an additional column 
        'cluster' that contains the cluster labels for each data point.

    """
    # Determine the optimal number of clusters
    n_clusters_optimal = max(scores, key=scores.get)

    # Apply KMeans clustering with the optimal number of clusters
    kmeans = KMeans(n_clusters=n_clusters_optimal, random_state=0)
    clusters = kmeans.fit_predict(df)

    # Add the cluster labels to the DataFrame
    df['cluster'] = clusters

    return df

def apply_dbscan_clustering(df: pd.DataFrame, eps: float, min_samples: int) -> pd.DataFrame:
    """
    Applies DBSCAN clustering to the dataset and adds a cluster label.

    This function applies DBSCAN clustering to the dataset with specified `eps` 
    and `min_samples` parameters, and assigns the cluster labels to the data.

    Args:
        df (pd.DataFrame): The dataset on which clustering will be applied. 
        It should be a DataFrame for this function to work correctly.
        eps (float): The maximum distance between two samples for them to be 
        considered as in the same neighborhood.
        min_samples (int): The number of samples in a neighborhood for a point 
        to be considered as a core point.

    Returns:
        pd.DataFrame: The original dataset with an additional column 'cluster' 
        that contains the cluster labels for each data point.

    """
    # Apply DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(df)

    # Add the cluster labels to the DataFrame
    df['cluster'] = clusters

    return df
